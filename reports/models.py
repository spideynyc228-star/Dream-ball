from django.conf import settings
from django.db import models
from students.models import Profile
class Report(models.Model):
    class Reason(models.TextChoices): SPAM="spam","Spam"; PHOTO="photo","Inappropriate photo"; HARASSMENT="harassment","Harassment"; FAKE="fake","Fake profile"; OTHER="other","Other"
    class Status(models.TextChoices): OPEN="open", "Open"; REVIEWING="reviewing", "In review"; RESOLVED="resolved", "Resolved"
    reporter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reports_made")
    profile=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="reports")
    reason=models.CharField(max_length=16,choices=Reason.choices); details=models.TextField(blank=True)
    status=models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN)
    moderator_note=models.TextField(blank=True)
    reviewed=models.BooleanField(default=False); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["reporter","profile"],name="one_report_per_profile")]
