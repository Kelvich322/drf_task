import re

from rest_framework import serializers

from .models import Event, EventRegistration, EventVenue


class EventVenueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EventVenue
        fields = ["url", "id", "name"]


class EventSerializer(serializers.HyperlinkedModelSerializer):
    venue = EventVenueSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ["url", "id", "name", "date", "status", "venue"]


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ["full_name", "email"]

    def validate_full_name(self, value):
        if len(value) > 128:
            raise serializers.ValidationError("Full name cannot exceed 128 characters")
        return value

    def validate_email(self, value):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email format")
        return value
