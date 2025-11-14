from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from httpx import Client, HTTPStatusError

from src.core.settings import JWT_TOKEN
from src.events.models import Event, EventVenue

from ...models import SyncResult


class Command(BaseCommand):
    help = "Sync events from external API"

    API_URL = "https://events.k3scluster.tech/api/events/"
    CLIENT = Client()

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Sync all events")

    def handle(self, *args, **options):
        """Основной метод, который выполняется при вызове команды"""
        self.use_full_sync = options["all"]

        try:
            with transaction.atomic():
                sync_result = SyncResult.objects.create()
                added, updated, latest_date = self.perform_sync()

                sync_result.added_events = added
                sync_result.updated_events = updated
                sync_result.last_synced_event_date = latest_date
                sync_result.save()

        except Exception as e:
            raise CommandError(f"Sync failed: {e}")

    def perform_sync(self):
        """Основная логика синхронизации"""
        added_count = 0
        updated_count = 0
        latest_event_date = None

        next_url = self.build_initial_url()

        while next_url:
            page_data = self.fetch_events_data(next_url)
            if not page_data:
                break

            events_data = page_data.get("results", [])
            for event_data in events_data:
                created, event_date = self.sync_single_event(event_data)

                if event_date and (
                    latest_event_date is None or event_date > latest_event_date
                ):
                    latest_event_date = event_date

                if created:
                    added_count += 1
                else:
                    updated_count += 1

            next_url = page_data.get("next")

        return added_count, updated_count, latest_event_date

    def build_initial_url(self):
        """Строит URL для запроса"""
        params = {}

        if not self.use_full_sync:
            last_sync_date = self.get_last_sync_date()
            if last_sync_date:
                changed_at_param = last_sync_date.strftime("%Y-%m-%d")
                params["changed_at"] = changed_at_param

        url = self.API_URL
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"

        return url

    def fetch_events_data(self, url):
        """Получение данных из внешнего API"""
        try:
            headers = {"Authorization": f"Bearer {JWT_TOKEN}"}
            response = self.CLIENT.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data

        except HTTPStatusError as e:
            raise CommandError(f"Request error: {e}")

    def get_last_sync_date(self):
        """Получает дату последней синхронизации"""
        sync_result = SyncResult.objects.last()
        if sync_result:
            return sync_result.last_synced_event_date
        return None

    def sync_single_event(self, event_data):
        """Синхронизация одного мероприятия"""
        try:
            event_id = event_data["id"]
            event_date = datetime.fromisoformat(event_data["event_time"])

            try:
                event = Event.objects.get(id=event_id)
                created = False
            except Event.DoesNotExist:
                event = Event(id=event_id)
                created = True

            venue_data = event_data["place"]
            venue, _ = EventVenue.objects.get_or_create(
                id=venue_data["id"], defaults={"name": venue_data["name"]}
            )

            event.id = event_data["id"]
            event.name = event_data["name"]
            event.date = event_date

            registration_deadline = datetime.fromisoformat(
                event_data["registration_deadline"]
            )
            event.status = (
                "open"
                if registration_deadline >= datetime.now().astimezone()
                else "closed"
            )

            event.venue = venue
            event.save()

            return created, event_date

        except KeyError:
            return False, None
        except Exception:  # разделение для последующего добавления verbose
            return False, None
