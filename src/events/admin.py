from django.contrib import admin

from .models import Event, EventVenue

admin.site.register([EventVenue, Event])
