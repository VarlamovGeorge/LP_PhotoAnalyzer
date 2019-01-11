from celery import Celery
from kombu import Exchange, Queue
import dropbox

from webapp.model import StorageUsers, Folder, Photos, Classes
from webapp import db


CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('for_task_1', Exchange('for_task_1'), routing_key='for_task_1'),
    Queue('for_task_2', Exchange('for_task_2'), routing_key='for_task_2'),
    Queue('for_task_3', Exchange('for_task_3'), routing_key='for_task_3'),
    )

CELERY_ROUTES = {
    'task1': {'queue': 'for_task_1', 'routing_key': 'for_task_1'},
    'task2': {'queue': 'for_task_2', 'routing_key': 'for_task_2'},
    'task3': {'queue': 'for_task_3', 'routing_key': 'for_task_3'},
    }

app = Celery('photo_analyzer', broker='amqp://admin:mypass@rabbitmq//')


@app.task
def bypass_storages():
    '''
    Для каждого хранилища запускаем отдельную задачу синхронизации
    '''
    pass


@app.task
def sync_file_list(id_storage):
    '''
    Синхронизирует локальный список файлов с хранилищем.
    Для каждого отличающегося файла запускается задача классификации.
    '''
    pass


@app.task
def get_class(id_file):
    '''
    Классификация файла
    '''
    pass

