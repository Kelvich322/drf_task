from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventVenueViewSet, EventViewSet

router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")
router.register(r"venues", EventVenueViewSet, basename="eventvenue")


urlpatterns = [
    path("", include(router.urls)),
]
