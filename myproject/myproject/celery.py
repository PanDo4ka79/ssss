from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
app = Celery('myproject')
CELERY_BROKER_URL = 'redis://localhost:6379/0'

app.conf.beat_schedule = {
    'send_weekly_newsletter': {
        'task': 'send_weekly_updates',
        'schedule': crontab(minute=0, hour=0, day_of_week=0),
    },
}

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()