task_routes = {
    'webapp.pa_tasks.celery.update_cnn_version': {'queue': 'celery'},
    'webapp.pa_tasks.celery.bypass_storages': {'queue': 'celery'},
    'webapp.pa_tasks.celery.sync_file_list': {'queue': 'sync'},
    'webapp.pa_tasks.celery.reclassify_photos': {'queue' : 'reclassify'},
    'webapp.pa_tasks.celery.get_class': {'queue': 'classify'},
    }

