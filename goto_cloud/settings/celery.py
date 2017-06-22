from __future__ import absolute_import, unicode_literals

import os
import sys

from celery import Celery

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

app = Celery('goto_cloud')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
