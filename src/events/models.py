import uuid

from django.db import models


class EventVenue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = "event_venues"


class Event(models.Model):
    class EventStatus(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=255, null=False)
    date = models.DateTimeField(null=False)
    status = models.CharField(
        max_length=10,
        choices=EventStatus.choices,
        null=False
    )
    venue = models.ForeignKey(EventVenue, on_delete=models.CASCADE, null=True)

    
