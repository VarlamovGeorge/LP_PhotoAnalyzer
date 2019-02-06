from celery import Celery
from celery.utils.log import get_task_logger
from sqlalchemy import func
import requests
import dropbox

from webapp.model import StorageUsers, Folders, Photos, Classes, Algorithms, photosclasses
from webapp import db, create_app


celery_app = Celery('pa_tasks', broker='amqp://guest@rabbitmq//')
celery_app.config_from_object('webapp.pa_tasks.celeryconfig')

logger = get_task_logger(__name__)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    '''

    '''
    sender.add_periodic_task(300.0, bypass_storages.s(), name='run resync every 300 sec')
    sender.add_periodic_task(300.0, update_cnn_version.s(), name='update cnn version')
    sender.add_periodic_task(300.0, reclassify_photos.s(), name='classify photos')


@celery_app.task
def update_cnn_version():
    '''
    Получает актуальную версию нейронки и пишет ее в базу
    '''
    # cnn_descr
    # cnn_date
    app = create_app()
    with app.app_context():
        try:
            cnn_response = requests.get('http://cnn_service:5000/version')
            cnn_response.raise_for_status()

            cnn_version = cnn_response.json()
            if not (cnn_version.get('cnn_date', None) and cnn_version.get('cnn_descr', None)):
                logger.error('Странный ответ от сервиса: %s' % cnn_response.text)
                return

            current_version = db.session.query(Algorithms) \
                                        .filter(Algorithms.name == cnn_version['cnn_descr']) \
                                        .filter(Algorithms.create_date == cnn_version['cnn_date']) \
                                        .first()

            if not current_version:
                new_cnn_version = Algorithms(name=cnn_version['cnn_descr'],
                                            create_date=cnn_version['cnn_date'])
                db.session.add(new_cnn_version)
                db.session.commit()
                logger.info('Новая версия нейронной сети - name:"%s" create_date:"%s"' %
                            (cnn_version['cnn_descr'], cnn_version['cnn_date']))

        except requests.exceptions.RequestException as ex:
            logger.error(ex)


@celery_app.task
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
            Ставим картинке признак ОК
        Иначе:
            Создаем картинку в базе

    Шаг3.
    Удаляем информацию о картинках, которые до сих пор инвалидны
    '''

    root_folder = db.session.query(Folders) \
                            .filter(Folders.storage_user_id == storage.id) \
                            .filter(Folders.local_path == '/') \
                            .first()
    if not root_folder:
        return

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

    def process_file(fmd):
        if not fmd.name.endswith('.jpg'):
            return
        image_in_db = db.session.query(Photos).filter(Photos.remote_id == fmd.id).first()
        if image_in_db is None:
            logger.info('Картинка "{}" в базе не найдена'.format(fmd.path_display))

            new_image = Photos(
                    create_date=fmd.server_modified,
                    folder_id=root_folder.id,
                    remote_id=fmd.id,
                    path=fmd.path_lower,
                    dropb_file_rev=fmd.rev,
                    dropb_hash=fmd.content_hash,
                    name=fmd.name,
                    size=fmd.size,
                    status=Photos.STATUS_OK)
            db.session.add(new_image)
            db.session.commit()
        else:
            if image_in_db.dropb_file_rev == fmd.rev:
                logger.info('Картинка "{}" не менялась'.format(image_in_db.path))

                image_in_db.status = Photos.STATUS_OK
                db.session.add(image_in_db)
                db.session.commit()
            else:
                logger.info('Картинка "{}" поменялась'.format(image_in_db.path))

                image_in_db.path = fmd.path_lower
                image_in_db.name = fmd.name
                image_in_db.dropb_file_rev = fmd.rev
                image_in_db.dropb_hash = fmd.content_hash
                image_in_db.size = fmd.size
                image_in_db.status = Photos.STATUS_OK
                db.session.add(image_in_db)
                db.session.commit()

                delete_classes(image_in_db.id)

    def process_entries(entries):
        for entry in entries:
             if isinstance(entry, dropbox.files.FileMetadata):
                 process_file(entry)

    # Main loop
    process_entries(result.entries)

    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)

        process_entries(result.entries)
    # End of main loop

    # Step3
    for image in Photos.query.filter(Photos.status == Photos.STATUS_NEED_RESYNC):
        logger.info('Картинка %s не была найдена в Dropbox и будет удалена.' % image.path)
        delete_photo(image)


def sync_yandex_storage(storage):
    pass


@celery_app.task
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

        # TODO: Можно сделать отдельные таски для каждого типа стораджей
        if storage.storage_id == 1:
            sync_dropbox_storage(storage)
        if storage.storage_id == 2:
            sync_yandex_storage(storage)


@celery_app.task
def reclassify_photos():
    '''
    Для каждой неотклассифицированной фотографии запускает отдельную задачу классификации
    '''
    logger.info('Task 3: reclassify_photos')

    app = create_app()
    with app.app_context():
        current_cnn_version = get_current_cnn_version()
        photos = db.session.query(Photos.id.label('id'), StorageUsers.id.label('id_storage')) \
                       .join(Folders) \
                       .join(StorageUsers) \
                       .filter(StorageUsers.storage_id == 1).all()
        for photo in photos:
            logger.info('Проверяем картинку с id: %s, id_storage: %s' % (photo.id, photo.id_storage))
            c_q = db.session.query(func.count(photosclasses.c.alg_id)) \
                        .select_from(photosclasses) \
                        .filter(photosclasses.c.photo_id == photo.id) \
                        .filter(photosclasses.c.alg_id == current_cnn_version) \
                        .group_by(photosclasses.c.alg_id)
            cnt = db.session.execute(c_q).scalar()
            if cnt is None or cnt == 0:
                logger.info('Отправляем на классификацию картинку с id: %s' % photo.id)
                get_class.delay(photo.id, photo.id_storage)


# TODO: часть этого надо точно где-то в модели делать
def delete_photo(photo):
    '''
    Удаляет фото из базы, предварительно удалив все метки
    '''
    d = photosclasses.delete().where(photosclasses.c.photo_id == photo.id)
    db.session.execute(d)
    db.session.delete(photo)
    db.session.commit()


# TODO: часть этого надо точно где-то в модели делать
def delete_classes(id_photo):
    '''
    Удаляет у фотографии метки классов, проставленных текущей нейронкой
    '''
    current_cnn_version = get_current_cnn_version()
    d = photosclasses.delete() \
                     .where(photosclasses.c.photo_id == id_photo) \
                     .where(photosclasses.c.alg_id == current_cnn_version)
    db.session.execute(d)
    db.session.commit()


def get_current_cnn_version():
    '''
    Возвращает id текущей версии нейронки
    '''
    current_cnn = db.session.query(Algorithms).order_by(Algorithms.create_date.desc()).first()
    return current_cnn.id


@celery_app.task(bind=True)
def get_class(self, id_file, id_storage):
    '''
    Классификация файла

    Шаг1. Выкачать файл из хранилища
    Шаг2. Отправить файл в виде POST запроса в сервис нейронки
    Шаг3. Полученные классы разложить по таблицам

    В случае ошибок, задача перезапускается
    '''
    logger.info('Task 4: get_class')

    app = create_app()
    with app.app_context():
        # Step0 - Get ACCESS_TOKEN
        storage = StorageUsers.query.filter(StorageUsers.id == id_storage).first()
        if (not storage) or (storage.storage_id != 1):
            return
        ACCESS_TOKEN = storage.credentials
        dbx = dropbox.Dropbox(ACCESS_TOKEN)

        image_in_db = db.session.query(Photos) \
                                .filter(Photos.id == id_file) \
                                .first()
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
                raise self.retry()

            prediction = result.get('prediction', {})

            logger.info('Записываем информацию о картинке: %s' % image_in_db.path)

            labels = prediction.get('labels', {})
            for label_name, weight in labels.items():
                class_for_label = db.session.query(Classes) \
                                            .filter(Classes.name == label_name) \
                                            .first()
                if class_for_label:
                    photo_label = photosclasses.insert().values(
                            alg_id=get_current_cnn_version(),
                            photo_id=image_in_db.id,
                            class_id=class_for_label.id,
                            weight=weight)
                    db.session.execute(photo_label)

            db.session.commit()

        except dropbox.exceptions.ApiError as ex:
            logger.error('Проблемы с выкачиванием картинки id: %s' % id_file)
            raise self.retry(exc=ex)
        except requests.exceptions.RequestException as ex:
            logger.error('Проблема работы с cnn сервисом')
            raise self.retry(exc=ex)
