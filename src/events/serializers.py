from models import Event, EventVenue
from rest_framework import serializers


class EventsVenueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventVenue
        fields = ["id", "name"]
class EventsSerializer(serializers.HyperlinkedModelSerializer):


    class Meta:
        model = Event

        fields = ["id", "name", "date", "status", "venue"]
