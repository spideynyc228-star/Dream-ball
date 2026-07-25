from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from students.models import Profile
from .models import Event, Meeting


@receiver(post_save, sender=Event)
def notify_event_update(sender, instance, created, **kwargs):
    message = f"New event details are available for {instance.title}." if created else f"{instance.title} has been updated."
    Notification.objects.bulk_create([
        Notification(user_id=user_id, message=message)
        for user_id in Profile.objects.filter(status=Profile.Status.APPROVED).values_list("user_id", flat=True)
    ])


@receiver(post_save, sender=Meeting)
def notify_meeting_update(sender, instance, created, **kwargs):
    label = "planned" if created else "updated"
    for user_id in (instance.partnership.student_one_id, instance.partnership.student_two_id):
        Notification.objects.get_or_create(
            user_id=user_id,
            message=f"A rehearsal meeting was {label} for {instance.date:%B %d} at {instance.time:%H:%M}.",
        )
