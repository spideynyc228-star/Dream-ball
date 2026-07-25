from django.db import models
from students.models import Partnership
class Event(models.Model):
    title=models.CharField(max_length=160); description=models.TextField()
    theme=models.CharField(max_length=120, blank=True)
    date=models.DateField(); time=models.TimeField(null=True, blank=True)
    location=models.CharField(max_length=160); address=models.CharField(max_length=240, blank=True)
    dress_code=models.CharField(max_length=160, blank=True)
    program=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    hero_image_url=models.URLField(blank=True)
    rules=models.TextField(blank=True)
    preparation_tips=models.TextField(blank=True)

    class Meta:
        ordering = ["date", "time"]
class Meeting(models.Model):
    class Status(models.TextChoices): PLANNED="planned", "Planned"; COMPLETED="completed", "Completed"; CANCELLED="cancelled", "Cancelled"
    partnership=models.ForeignKey(Partnership,on_delete=models.CASCADE,related_name="meetings")
    date=models.DateField(); time=models.TimeField(); location=models.CharField(max_length=160); notes=models.TextField(blank=True)
    status=models.CharField(max_length=12, choices=Status.choices, default=Status.PLANNED)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "time"]


class Announcement(models.Model):
    event=models.ForeignKey(Event, on_delete=models.CASCADE, related_name="announcements")
    title=models.CharField(max_length=180)
    body=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
