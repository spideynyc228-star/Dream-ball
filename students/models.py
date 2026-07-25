from django.conf import settings
from django.db import models
from django.utils import timezone

class Profile(models.Model):
    class Status(models.TextChoices): PENDING="pending", "Pending review"; APPROVED="approved", "Approved"; REJECTED="rejected", "Needs changes"
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="profile")
    grade=models.CharField(max_length=8, blank=True); class_letter=models.CharField(max_length=4, blank=True)
    height=models.PositiveSmallIntegerField(help_text="Height in cm", null=True, blank=True)
    bio=models.TextField(max_length=600, blank=True); dance_experience=models.CharField(max_length=40, blank=True)
    personality=models.CharField(max_length=80, blank=True); preferred_rehearsal_time=models.CharField(max_length=80, blank=True)
    photo=models.ImageField(upload_to="profiles/", blank=True)
    agreed_to_rules=models.BooleanField(default=False)
    status=models.CharField(max_length=10,choices=Status.choices,default=Status.PENDING)
    moderation_note=models.TextField(blank=True)
    created_at=models.DateTimeField(default=timezone.now, editable=False)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return self.user.get_full_name() or self.user.username

class PartnershipRequest(models.Model):
    class Status(models.TextChoices): PENDING="pending", "Pending"; ACCEPTED="accepted", "Accepted"; DECLINED="declined", "Declined"
    sender=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="sent_partnership_requests")
    receiver=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="received_partnership_requests")
    status=models.CharField(max_length=10,choices=Status.choices,default=Status.PENDING); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["sender","receiver"],name="unique_partnership_request")]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.sender_id == self.receiver_id:
            raise ValidationError("A student cannot request a partnership with themselves.")

class Partnership(models.Model):
    student_one=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="partnerships_one")
    student_two=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="partnerships_two")
    created_at=models.DateTimeField(auto_now_add=True)
    shared_notes=models.TextField(blank=True)
    preparation_complete=models.BooleanField(default=False)
    class Meta: constraints=[models.UniqueConstraint(fields=["student_one","student_two"],name="unique_partnership")]
    def partner_for(self,user): return self.student_two if self.student_one_id==user.id else self.student_one
