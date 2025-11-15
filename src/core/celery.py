from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.core.settings")

app = Celery("drf_task")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "outbox-transaction": {
        "task": "src.events.tasks.process_outbox_event",
        "schedule": 10.0,
    },
}
