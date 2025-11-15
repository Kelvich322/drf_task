import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone
from httpx import Client

from src.core.settings import JWT_TOKEN, OWNER_ID

from .models import OutboxEvent

logger = logging.getLogger(__name__)


@shared_task
def process_outbox_event():
    with transaction.atomic():
        events = OutboxEvent.objects.select_for_update(skip_locked=True).filter(
            processed=False
        )[:100]

        for event in events:
            try:
                send_confirmation_email.delay(event.payload)
                event.processed = True
                event.processed_at = timezone.now()
                event.save()

            except Exception as e:
                logger.error(f"Error processing outbox event {event.id}: {e}")


@shared_task
def send_confirmation_email(payload):
    """Отправка уведомления о регистрации пользователя"""
    NOTIFICATIONS_URL = "https://notifications.k3scluster.tech/api/notifications"

    with Client() as client:
        email_message = f"Your verification code: {payload['confirmation_code']}"

        data = {
            "id": str(payload["registration_id"]),
            "owner_id": OWNER_ID,
            "email": payload["email"],
            "message": email_message,
        }

        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json",
            "accept": "application/json",
        }

        try:
            response = client.post(NOTIFICATIONS_URL, json=data, headers=headers)
            response.raise_for_status()
            logger.info(
                f"Successfully sent registration notification to {payload['email']}"
            )

        except Exception as e:
            logger.error(
                f"Error sending registration notification to {payload['email']}: {e}"
            )
            raise
