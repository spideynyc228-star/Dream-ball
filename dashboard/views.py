from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from events.models import Event
from blog.models import Article
from notifications.models import Notification
from students.models import Partnership


def home(request):
    event = Event.objects.filter(is_active=True).first()
    return render(request, "home.html", {"event": event, "today": timezone.localdate()})


@login_required
def dashboard(request):
    event = Event.objects.filter(is_active=True).first()
    partnership = Partnership.objects.filter(student_one=request.user).select_related("student_two").first()
    if not partnership:
        partnership = Partnership.objects.filter(student_two=request.user).select_related("student_one").first()
    partner = partnership.partner_for(request.user) if partnership else None
    return render(request, "dashboard/home.html", {
        "event": event,
        "partnership": partnership,
        "partner": partner,
        "notifications": request.user.notifications.order_by("-created_at")[:5],
        "profile": getattr(request.user, "profile", None),
        "articles": Article.objects.all()[:3],
    })


@login_required
def event_detail(request):
    event = Event.objects.filter(is_active=True).prefetch_related("announcements").first()
    return render(request, "dashboard/event.html", {"event": event})


@login_required
def notifications(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "dashboard/notifications.html", {"notifications": request.user.notifications.order_by("-created_at")})
