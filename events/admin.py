from django.contrib import admin
from .models import Announcement, Event,Meeting

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "time", "location", "is_active")
    list_filter = ("is_active", "date")
    search_fields = ("title", "location", "theme")

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("partnership", "date", "time", "location", "status")
    list_filter = ("status", "date")
    search_fields = ("location", "notes")

admin.site.register(Announcement)
