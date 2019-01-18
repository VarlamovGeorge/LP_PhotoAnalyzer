task_routes = {
    'webapp.pa_tasks.celery.bypass_storages': {'queue': 'celery'},
    'webapp.pa_tasks.celery.sync_file_list': {'queue': 'q2'},
    'webapp.pa_tasks.celery.get_class': {'queue': 'q3'},
    }

