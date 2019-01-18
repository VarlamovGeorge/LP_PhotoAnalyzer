from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

import dropbox

from webapp.model import StorageUsers, Folders, Photos, Classes
from webapp import db, create_app




app = Celery('pa_tasks', broker='amqp://guest@rabbitmq//')
app.config_from_object('webapp.pa_tasks.celeryconfig')

logger = get_task_logger(__name__)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(300.0, bypass_storages.s(), name='run resync every 300 sec')


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
    Photos.update().
            where(Photos.folder_id == Folders.id).
            where(Folders.storage_user_id = storage.storage_id).
            values(Photos.status == Photos.STATUS_NEED_RESYNC)
    db.session.commit()

    # Step2
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    result = dbx.files_list_folder("", recursive=True, include_media_info=True)

    def process_file(fmd):
        if not fmd.name.endswith('.jpg'):
            return
        image_in_db = Photos.query.filter(Photos.remote_id==fmd.id).first()
        if image_in_db is None:
            logger.info('Картинка "{}" в базе не найдена'.format(fmd.path_display))

            new_image = Photos(
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

            get_class.delay(new_image.id)
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

                get_class.delay(image_in_db.id)

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

    storage = StorageUsers.query.filter(StorageUsers.id == id_storage).first()
    if storage is None:
        return

    if storage.storage_id == 1:
        sync_dropbox_storage(storage)


@app.task
def get_class(id_file):
    '''
    Классификация файла
    '''
    logger.info('Task 3: get_class')

