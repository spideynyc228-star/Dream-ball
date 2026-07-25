from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices): STUDENT="student", "Student"; MODERATOR="moderator", "Moderator"; TEACHER="teacher", "Teacher"; ADMIN="admin", "Administrator"
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.STUDENT)
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = ["email"]

    @property
    def is_staff_member(self): return self.role in {self.Role.MODERATOR, self.Role.TEACHER, self.Role.ADMIN} or self.is_superuser

class InvitationCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    role = models.CharField(max_length=12, choices=User.Role.choices, default=User.Role.STUDENT)
    used_by = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="invitation")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    @property
    def available(self):
        from django.utils import timezone
        return self.is_active and self.used_by_id is None and (not self.expires_at or self.expires_at > timezone.now())
    def __str__(self): return self.code
