from django.contrib import admin
from .models import User,InvitationCode

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")

@admin.register(InvitationCode)
class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "role", "is_active", "used_by", "created_at", "expires_at")
    list_filter = ("role", "is_active")
    search_fields = ("code", "used_by__username", "used_by__email")
