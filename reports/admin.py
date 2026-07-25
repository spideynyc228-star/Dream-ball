from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("profile", "reason", "status", "reviewed", "created_at")
    list_filter = ("status", "reason", "reviewed")
    search_fields = ("profile__user__first_name", "profile__user__last_name", "details")
