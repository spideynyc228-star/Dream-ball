from django.contrib import admin
from django.utils.html import format_html
from .models import Profile,Partnership,PartnershipRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("photo_preview", "user", "grade", "class_letter", "status", "created_at", "updated_at")
    list_filter = ("status", "grade", "dance_experience")
    search_fields = ("user__first_name", "user__last_name", "user__username", "bio")
    readonly_fields = ("created_at", "updated_at", "photo_preview")

    @admin.display(description="Photo")
    def photo_preview(self, obj):
        return format_html('<img src="{}" style="width:36px;height:36px;border-radius:50%;object-fit:cover;" alt="">', obj.photo.url) if obj.photo else "—"

admin.site.register([Partnership,PartnershipRequest])
