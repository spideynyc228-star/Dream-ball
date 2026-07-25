import secrets

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from students.models import Profile, Partnership
from accounts.models import InvitationCode
from events.models import Event
from reports.models import Report
from notifications.models import Notification
staff_required=user_passes_test(lambda u:u.is_authenticated and u.is_staff_member)
moderator_required = user_passes_test(lambda u: u.is_authenticated and u.role in {"moderator", "admin"})
admin_required = user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
@staff_required
def dashboard(request):
    status = request.GET.get("status", "pending")
    search = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "-updated_at")
    allowed_sort = {"updated_at", "-updated_at", "created_at", "-created_at", "user__last_name", "-user__last_name"}
    if sort not in allowed_sort:
        sort = "-updated_at"
    profiles = Profile.objects.select_related("user")
    if status in {Profile.Status.PENDING, Profile.Status.APPROVED, Profile.Status.REJECTED}:
        profiles = profiles.filter(status=status)
    if search:
        profiles = profiles.filter(Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | Q(user__username__icontains=search))
    report_search = request.GET.get("report_q", "").strip()
    reports = Report.objects.filter(reviewed=False).select_related("profile__user", "reporter")
    if report_search:
        reports = reports.filter(Q(profile__user__first_name__icontains=report_search) | Q(profile__user__last_name__icontains=report_search) | Q(details__icontains=report_search))
    code_search = request.GET.get("code_q", "").strip()
    codes = InvitationCode.objects.filter(is_active=True, used_by__isnull=True).order_by("-created_at")
    if code_search:
        codes = codes.filter(code__icontains=code_search)
    return render(request,"moderation/dashboard.html",{
        "profiles": profiles.order_by(sort), "selected_status": status, "student_search": search,
        "pending":Profile.objects.filter(status="pending").count(),
        "reports": reports,
        "approved_count":Profile.objects.filter(status="approved").count(),
        "codes_count":codes.count(), "codes":codes[:20], "code_search":code_search,
        "partnerships":Partnership.objects.select_related("student_one", "student_two").order_by("-created_at")[:8],
        "events":Event.objects.order_by("date")[:4],
    })
@staff_required
@moderator_required
def review_profile(request,pk,status):
    if request.method != "POST" or status not in {Profile.Status.APPROVED, Profile.Status.REJECTED}: return redirect("moderation:dashboard")
    profile=get_object_or_404(Profile,pk=pk); profile.status=status; profile.moderation_note=request.POST.get("note",""); profile.save()
    message = "Your profile was approved. You can now browse the student directory." if status == Profile.Status.APPROVED else "Your profile needs an update before approval. Please read the moderator note."
    Notification.objects.create(user=profile.user, message=message)
    return redirect("moderation:dashboard")
@staff_required
@moderator_required
def review_report(request,pk):
    if request.method != "POST": return redirect("moderation:dashboard")
    report=get_object_or_404(Report,pk=pk); report.status=request.POST.get("status", Report.Status.RESOLVED); report.reviewed=report.status == Report.Status.RESOLVED; report.moderator_note=request.POST.get("note", ""); report.save(); return redirect("moderation:dashboard")


@moderator_required
def delete_report(request, pk):
    if request.method == "POST":
        get_object_or_404(Report, pk=pk).delete()
        messages.success(request, "Report deleted.")
    return redirect("moderation:dashboard")


@moderator_required
def delete_profile(request, pk):
    if request.method == "POST":
        profile = get_object_or_404(Profile, pk=pk)
        profile.user.delete()
        messages.success(request, "Student profile and account deleted.")
    return redirect("moderation:dashboard")


@admin_required
def create_invitation(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper() or secrets.token_urlsafe(7).upper()
        role = request.POST.get("role", "student")
        if role not in {"student", "moderator", "teacher", "admin"}:
            role = "student"
        if InvitationCode.objects.filter(code=code).exists():
            messages.error(request, "That invitation code already exists.")
        else:
            InvitationCode.objects.create(code=code, role=role)
            messages.success(request, f"Invitation code {code} is ready to share.")
    return redirect("moderation:dashboard")
