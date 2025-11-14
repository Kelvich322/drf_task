from django.db import models
from django.utils import timezone


class SyncResult(models.Model):
    executed_at = models.DateTimeField(default=timezone.now)
    added_events = models.PositiveIntegerField(default=0)
    updated_events = models.PositiveIntegerField(default=0)
    last_synced_event_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "sync_results"
        ordering = ["-executed_at"]
