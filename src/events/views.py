from django.db.models import Prefetch
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from .models import Event, EventVenue
from .serializers import EventSerializer, EventVenueSerializer


class EventVenueViewSet(ModelViewSet):  # ← Добавить этот ViewSet
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
