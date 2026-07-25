from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from events.models import Event
from blog.models import Article
from notifications.models import Notification
from students.models import Partnership, Profile


def home(request):
    event = Event.objects.filter(is_active=True).first()
    return render(request, "home.html", {"event": event, "today": timezone.localdate()})


@login_required
def dashboard(request):
    if request.user.role != "student":
        return redirect("moderation:dashboard")
    profile = getattr(request.user, "profile", None)
    if profile and profile.status == Profile.Status.PENDING:
        return render(request, "dashboard/pending_activity.html", {
            "profile": profile,
            "notifications": request.user.notifications.order_by("-created_at")[:5],
        })
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
        "profile": profile,
        "articles": Article.objects.all()[:3],
    })


@login_required
def event_detail(request):
    if request.user.role != "student":
        return redirect("moderation:dashboard")
    profile = getattr(request.user, "profile", None)
    if not profile or profile.status != Profile.Status.APPROVED:
        return redirect("dashboard:home")
    event = Event.objects.filter(is_active=True).prefetch_related("announcements").first()
    program_items = []
    if event and event.program:
        for line in event.program.splitlines():
            time, separator, title = line.partition(" - ")
            if separator:
                program_items.append({"time": time.strip(), "title": title.strip()})
    if not program_items:
        program_items = [
            {"time": "18:00", "title": "Opening ceremony"},
            {"time": "18:30", "title": "Celebration dinner"},
            {"time": "20:00", "title": "Dance & music"},
            {"time": "22:00", "title": "Class awards"},
            {"time": "22:45", "title": "Closing ceremony"},
        ]
    return render(request, "dashboard/event.html", {"event": event, "program_items": program_items})


@login_required
def notifications(request):
    if request.user.role != "student":
        return redirect("moderation:dashboard")
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "dashboard/notifications.html", {"notifications": request.user.notifications.order_by("-created_at")})
