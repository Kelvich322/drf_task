from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventVenueViewSet, EventViewSet, register_for_event

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"venues", EventVenueViewSet, basename="eventvenue")


urlpatterns = [
    path("", include(router.urls)),
    path("events/<str:event_id>/register/", register_for_event, name="event-register"),
]
