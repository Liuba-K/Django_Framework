import os

#from django.conf import settings #add
from celery import Celery

#if settings.DEBUG:
#    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

celery_app = Celery("config")  #почему braniac? Django_Framework
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
