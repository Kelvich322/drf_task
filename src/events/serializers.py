from rest_framework import serializers

from .models import Event, EventVenue


class EventVenueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventVenue
        fields = ["url", "id", "name"]


class EventSerializer(serializers.HyperlinkedModelSerializer):
    venue = EventVenueSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ["url", "id", "name", "date", "status", "venue"]
