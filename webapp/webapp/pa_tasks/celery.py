from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import requests

import dropbox

from webapp.model import StorageUsers, Folders, Photos, Classes, Algorithms, photosclasses
from webapp import db, create_app




app = Celery('pa_tasks', broker='amqp://guest@rabbitmq//')
app.config_from_object('webapp.pa_tasks.celeryconfig')

logger = get_task_logger(__name__)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(120.0, bypass_storages.s(), name='run resync every 300 sec')


@app.task
def bypass_storages():
    '''
    Для каждого хранилища запускаем отдельную задачу синхронизации
    '''
    logger.info('Task 1: bypass storages')

    app = create_app()
    with app.app_context():
        for storage in StorageUsers.query.all():
            sync_file_list.delay(storage.id)


def sync_dropbox_storage(storage):
    '''
    Шаг 1.
    Инвалидация всех картинок (мы не знаем что с ними сейчас происходит в Dropbox)

    Шаг2.
    Для каждой картики в хранилище:
        Если картинка есть в базе То:
            Если картинка изменилась То:
                Обновляем метаинформацию у картинки
                Ставим картинке признак необходимости провести дополнительные действия, например классификацию
            Иначе:
                Ставим картинке признак ОК
        Иначе:
            Создаем картинку в базе
            Ставим картинке признак необходимости провести дополнительные действия, например классификацию

    Шаг3.
    Удаляем информацию о картинках, которые до сих пор инвалидны
    '''

    # Step0 - Get ACCESS_TOKEN
    if (storage is None) or (storage.storage_id != 1):
        return
    ACCESS_TOKEN = storage.credentials

    # Step1
    db.session.query(Photos) \
             .filter(Photos.folder_id == Folders.id) \
             .filter(Folders.storage_user_id == storage.id) \
             .update({'status': Photos.STATUS_NEED_RESYNC}, synchronize_session='fetch')
    db.session.commit()

    # Step2
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    result = dbx.files_list_folder("", recursive=True, include_media_info=True)

    root_folder = db.session.query(Folders).filter(Folders.storage_user_id==storage.id).filter(Folders.local_path=='/').first()
    if root_folder is None:
        root_folder = Folders(
                local_path='/',
                storage_user_id=storage.id)
        db.session.add(root_folder)
        db.session.commit()
        db.session.refresh(root_folder)

    def process_file(fmd):
        if not fmd.name.endswith('.jpg'):
            return
        image_in_db = db.session.query(Photos).filter(Photos.remote_id==fmd.id).first()
        if image_in_db is None:
            logger.info('Картинка "{}" в базе не найдена'.format(fmd.path_display))

            new_image = Photos(
                    create_date=fmd.server_modified,
                    folder_id = root_folder.id,
                    remote_id=fmd.id,
                    path=fmd.path_lower,
                    revision=fmd.rev,
                    content_hash=fmd.content_hash,
                    name=fmd.name,
                    size=fmd.size,
                    status=Photos.STATUS_NEED_CLASSIFY)
            db.session.add(new_image)
            db.session.commit()
            db.session.flush()
            db.session.refresh(new_image)

            get_class.delay(new_image.id, storage.id)
        else:
            if image_in_db.revision == fmd.rev:
                logger.info('Картинка "{}" не менялась'.format(image_in_db.path))

                image_in_db.status = Photos.STATUS_OK
                db.session.add(image_in_db)
                db.session.commit()
            else:
                logger.info('Картинка "{}" поменялась'.format(image_in_db.path))

                image_in_db.path = fmd.path_lower
                image_in_db.name = fmd.name
                image_in_db.revision = fmd.rev
                image_in_db.content_hash = fmd.content_hash
                image_in_db.size = fmd.size
                image_in_db.status = Photos.STATUS_NEED_CLASSIFY
                db.session.add(image_in_db)
                db.session.commit()
                db.session.flush()

                get_class.delay(image_in_db.id, storage.id)

    def process_entries(entries):
        for entry in entries:
             if isinstance(entry, dropbox.files.FileMetadata):
                 process_file(entry)

    ### Main loop
    process_entries(result.entries)

    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)

        process_entries(result.entries)
    ### End of main loop

    # Step3
    for image in Photos.query.filter(Photos.status==Photos.STATUS_NEED_RESYNC):
        logger.info('Картинка {} не была найдена в Dropbox'.format(image.path))



@app.task
def sync_file_list(id_storage):
    '''
    Синхронизирует локальный список файлов с хранилищем.
    Для каждого отличающегося файла запускается задача классификации.
    '''
    logger.info('Task 2: sync_file_list for id storage: %s' % id_storage)

    app = create_app()
    with app.app_context():
        storage = StorageUsers.query.filter(StorageUsers.id == id_storage).first()
        if storage is None:
            return

        if storage.storage_id == 1:
            sync_dropbox_storage(storage)


def get_current_cnn_version():
    '''
    Возвращает id текущей версии нейронки
    '''
    return 0


@app.task(bind=True)
def get_class(self, id_file, id_storage):
    '''
    Классификация файла

    Шаг1. Выкачать файл из хранилища
    Шаг2. Отправить файл в виде POST запроса в сервис нейронки
    Шаг3. Полученные классы разложить по таблицам

    В случае ошибок, задача перезапускается
    https://www.distributedpython.com/2018/09/04/error-handling-retry/
    '''
    logger.info('Task 3: get_class')

    app = create_app()
    with app.app_context():
        # Step0 - Get ACCESS_TOKEN
        storage = StorageUsers.query.filter(StorageUsers.id == id_storage).first()
        if (not storage) or (storage.storage_id != 1):
            return
        ACCESS_TOKEN = storage.credentials
        dbx = dropbox.Dropbox(ACCESS_TOKEN)

        image_in_db = db.session.query(Photos).filter(Photos.id==id_file).filter(Photos.status==Photos.STATUS_NEED_CLASSIFY).first()
        if not image_in_db:
            return

        try:
            # Шаг1
            logger.info('Скачиваем картинку: %s' % image_in_db.path)
            metadata, response = dbx.files_download(image_in_db.path)
            image_in_dropbox = response.content

            # Шаг2
            logger.info('Отправляем картинку в нейронку: %s' % image_in_db.path)
            files = {'image': image_in_dropbox}
            cnn_response = requests.post('http://cnn_service:5000/cnn', files=files)
            cnn_response.raise_for_status()

            # Шаг3
            result = cnn_response.json()
            if result.get('status', '') != 'OK':
                logger.error('Проблема работы с cnn сервисом: %s' % result)
                raise self.retry(exc=ex)

            prediction = result.get('prediction',{})

            logger.info('Записываем информацию о картинке: %s' % image_in_db.path)

            # Удаляем все классы, которые были получены текущей CNN
            current_cnn_version = get_current_cnn_version()
            d = photosclasses.delete() \
                        .where(photosclasses.c.photo_id==image_in_db.id) \
                        .where(photosclasses.c.alg_id==current_cnn_version)
            db.session.execute(d)

            labels = prediction.get('labels', {})
            for label_name, weight in labels.items():
                class_for_label = db.session.query(Classes).filter(Classes.name==label_name).first()
                if class_for_label:
                    photo_label = photosclasses.insert().values(
                            alg_id=current_cnn_version,
                            photo_id=image_in_db.id,
                            class_id=class_for_label.id,
                            weight=weight)
                    db.session.execute(photo_label)

            db.session.commit()

        except dropbox.exceptions.ApiError as ex:
            logger.error('Проблемы с выкачиванием картинки id:{}'.format(id_file))
            raise self.retry(exc=ex)
        except requests.exceptions.RequestException as ex:
            logger.error('Проблема работы с cnn сервисом')
            raise self.retry(exc=ex)

