from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from flask import current_app as flask_app

from webapp.model import StorageUsers, Folders, Photos, Classes
from webapp import db


app = Celery('pa_tasks', broker='amqp://guest@rabbitmq//')
app.config_from_object('webapp.pa_tasks.celeryconfig')

logger = get_task_logger(__name__)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(300.0, bypass_storages.s(), name='add every 300')


@app.task
def bypass_storages():
    '''
    Для каждого хранилища запускаем отдельную задачу синхронизации
    '''
    logger.info('Task 1: bypass storages')

    for i in range(0, 2):
        sync_file_list.delay(1)


@app.task
def sync_file_list(id_storage):
    '''
    Синхронизирует локальный список файлов с хранилищем.
    Для каждого отличающегося файла запускается задача классификации.
    '''
    logger.info('Task 2: sync_file_list')

    for i in range(0, 2):
        get_class.delay(1)


@app.task
def get_class(id_file):
    '''
    Классификация файла
    '''
    logger.info('Task 3: get_class')

