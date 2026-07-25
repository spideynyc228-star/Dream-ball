from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "reading_time", "published_at")
    list_filter = ("category", "published_at")
    search_fields = ("title", "excerpt", "body", "author")
    prepopulated_fields = {"slug": ("title",)}
