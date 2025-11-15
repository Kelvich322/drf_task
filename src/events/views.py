import random

from django.db import transaction
from django.db.models import Prefetch
from rest_framework import filters, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Event, EventRegistration, EventVenue, OutboxEvent
from .serializers import (
    EventRegistrationSerializer,
    EventSerializer,
    EventVenueSerializer,
)


class EventVenueViewSet(ModelViewSet):
    queryset = EventVenue.objects.all()
    serializer_class = EventVenueSerializer


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class EventViewSet(ModelViewSet):
    queryset = (
        Event.objects.filter(status="open")
        .order_by("date", "name")
        .prefetch_related(Prefetch("venue", queryset=EventVenue.objects.only("name")))
    )
    serializer_class = EventSerializer
    pagination_class = EventPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["date"]


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_for_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    if event.status != "open":
        return Response(
            {"error": "Registration is closed for this event"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = EventRegistrationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            if EventRegistration.objects.filter(
                event=event, email=serializer.validated_data["email"]
            ).exists():
                return Response(
                    {"error": "You are already registered for this event"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            confirmation_code = generate_confirmation_code()

            registration = EventRegistration.objects.create(
                event=event,
                full_name=serializer.validated_data["full_name"],
                email=serializer.validated_data["email"],
                confirmation_code=confirmation_code,
            )

            OutboxEvent.objects.create(
                topic="registration_confirm",
                payload={
                    "registration_id": str(registration.id),
                    "email": registration.email,
                    "confirmation_code": confirmation_code,
                },
            )

            return Response(
                {
                    "message": "Registration successful. Confirmation code sent to your email.",
                },
                status=status.HTTP_201_CREATED,
            )

    except Exception as e:
        return Response(
            {"error": "Registration failed", "datail": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def generate_confirmation_code():
    return random.randint(11111, 99999)
