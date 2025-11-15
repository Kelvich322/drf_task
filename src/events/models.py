import uuid

from django.db import models


class EventVenue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = "event_venues"

    def __str__(self):
        return self.name


class Event(models.Model):
    class EventStatus(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    date = models.DateTimeField(null=False)
    status = models.CharField(max_length=10, choices=EventStatus.choices, null=False)
    venue = models.ForeignKey(EventVenue, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "events"

    def __str__(self):
        return self.name


class EventRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )
    full_name = models.CharField(max_length=128)
    email = models.EmailField()
    confirmation_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_registrations"
        unique_together = ["event", "email"]


class OutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    topic = models.CharField(max_length=255)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "outbox_events"
