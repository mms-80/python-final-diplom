import os

from celery import Celery
from celery.result import AsyncResult

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netology_pd_diplom.settings')

celery_app = Celery('celery_app_for_pyhon_diplom')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
celery_app.autodiscover_tasks()

# return satus and result of async task
def get_task(task_id: str) -> AsyncResult:
    """
    Get the result of a Celery task by its ID.

    Args:
        task_id (str): The ID of the task.

    Returns:
        AsyncResult: The result of the task.
    """
    return AsyncResult(task_id, app=celery_app)