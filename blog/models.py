from django.db import models
class Article(models.Model):
    title=models.CharField(max_length=180); slug=models.SlugField(unique=True); excerpt=models.TextField(); body=models.TextField()
    cover_image_url=models.URLField(blank=True)
    category=models.CharField(max_length=80, default="Student life")
    author=models.CharField(max_length=120, default="Dream Ball Team")
    reading_time=models.PositiveSmallIntegerField(default=4, help_text="Estimated reading time in minutes")
    published_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]
    def __str__(self): return self.title
