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
    reports = Report.objects.select_related("profile__user", "reporter").order_by("-created_at")
    codes = InvitationCode.objects.select_related("used_by").order_by("-created_at")
    return render(request,"moderation/dashboard.html",{
        "profiles": profiles.order_by(sort), "selected_status": status, "student_search": search,
        "pending":Profile.objects.filter(status="pending").count(),
        "reports": reports,
        "approved_count":Profile.objects.filter(status="approved").count(),
        "codes_count":InvitationCode.objects.filter(is_active=True, used_by__isnull=True).count(), "codes":codes[:30],
        "partnerships":Partnership.objects.select_related("student_one", "student_two").order_by("-created_at")[:8],
        "events":Event.objects.order_by("date")[:4],
    })
@staff_required
@moderator_required
def review_profile(request,pk,status):
    if request.method != "POST" or status not in {Profile.Status.APPROVED, Profile.Status.REJECTED}: return redirect("moderation:dashboard")
    profile=get_object_or_404(Profile,pk=pk)
    if status == Profile.Status.APPROVED and not profile.is_complete:
        messages.error(request, "This profile cannot be approved yet because required answers are missing.")
        return redirect("moderation:dashboard")
    profile.status=status; profile.moderation_note=request.POST.get("note",""); profile.save()
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


@admin_required
def update_invitation(request, pk):
    if request.method == "POST":
        invitation = get_object_or_404(InvitationCode, pk=pk)
        code = request.POST.get("code", "").strip().upper()
        role = request.POST.get("role", invitation.role)
        if not code:
            messages.error(request, "Invitation code cannot be empty.")
        elif InvitationCode.objects.exclude(pk=invitation.pk).filter(code=code).exists():
            messages.error(request, "That invitation code already exists.")
        elif role not in {"student", "moderator", "teacher", "admin"}:
            messages.error(request, "Choose a valid account role.")
        else:
            invitation.code = code
            invitation.role = role
            invitation.save(update_fields=["code", "role"])
            messages.success(request, "Invitation code updated.")
    return redirect("moderation:dashboard")


@admin_required
def delete_invitation(request, pk):
    if request.method == "POST":
        invitation = get_object_or_404(InvitationCode, pk=pk)
        invitation.delete()
        messages.success(request, "Invitation code deleted. Existing accounts stay active.")
    return redirect("moderation:dashboard")
