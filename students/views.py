from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time

from notifications.models import Notification
from .forms import ProfileForm
from .models import FinalPartnerProposal, Partnership, PartnershipRequest, Profile, Rehearsal


def approved_required(view):
    def wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "profile") or request.user.profile.status != Profile.Status.APPROVED:
            return redirect("dashboard:home")
        return view(request, *args, **kwargs)
    return login_required(wrapped)


@login_required
def profile(request):
    existing_profile = getattr(request.user, "profile", None)
    if request.user.role == "admin":
        return redirect("moderation:dashboard")
    if existing_profile and existing_profile.status == Profile.Status.PENDING and existing_profile.is_complete:
        return redirect("dashboard:home")
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if profile.status == Profile.Status.APPROVED and not profile.is_complete:
        profile.status = Profile.Status.PENDING
        profile.save(update_fields=["status"])
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        profile = form.save(commit=False)
        profile.status = Profile.Status.PENDING
        profile.moderation_note = ""
        profile.save()
        messages.success(request, "Your profile was submitted for moderation.")
        return redirect("dashboard:home")
    return render(request, "students/profile.html", {"form": form, "profile": profile, "has_saved_profile": profile.is_complete})


@approved_required
def browse(request):
    profiles = Profile.objects.filter(status=Profile.Status.APPROVED).exclude(user=request.user).select_related("user")
    opposite_gender = {
        Profile.Gender.FEMALE: Profile.Gender.MALE,
        Profile.Gender.MALE: Profile.Gender.FEMALE,
    }.get(request.user.profile.gender)
    if opposite_gender:
        profiles = profiles.filter(gender=opposite_gender)
    else:
        profiles = profiles.none()
    q = request.GET.get("q", "")
    if q:
        profiles = profiles.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(bio__icontains=q))
    for field in ("grade", "dance_experience"):
        if request.GET.get(field):
            profiles = profiles.filter(**{field: request.GET[field]})
    if request.GET.get("height_min"):
        profiles = profiles.filter(height__gte=request.GET["height_min"])
    return render(request, "students/browse.html", {"profiles": profiles, "grades": Profile.objects.values_list("grade", flat=True).distinct(), "experiences": Profile.objects.values_list("dance_experience", flat=True).distinct(), "today": timezone.localdate().isoformat()})


@approved_required
def requests_page(request):
    return render(request, "students/requests.html", {
        "incoming": request.user.received_partnership_requests.filter(status="pending").select_related("sender"),
        "outgoing": request.user.sent_partnership_requests.select_related("receiver"),
    })


@approved_required
def send_request(request, user_id):
    if request.method != "POST":
        return redirect("students:browse")
    receiver = get_object_or_404(Profile, user_id=user_id, status="approved").user
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    def reply(message, ok=False, status=400):
        if is_ajax:
            return JsonResponse({"ok": ok, "message": message}, status=status)
        (messages.success if ok else messages.error)(request, message)
        return redirect("students:browse")

    if receiver == request.user:
        return reply("You cannot invite yourself.")
    opposite_gender = {
        Profile.Gender.FEMALE: Profile.Gender.MALE,
        Profile.Gender.MALE: Profile.Gender.FEMALE,
    }.get(request.user.profile.gender)
    if not opposite_gender or receiver.profile.gender != opposite_gender:
        return reply("Rehearsal invitations are available only to opposite-gender profiles.")
    if Partnership.objects.filter(Q(student_one=request.user) | Q(student_two=request.user)).exists():
        return reply("You already have a final dance partner.")
    date = request.POST.get("proposed_date") or None
    time = request.POST.get("proposed_time") or None
    location = request.POST.get("location", "").strip()
    note = request.POST.get("note", "").strip()
    if not date or not time or not location:
        return reply("Choose a date, time and a public rehearsal location.")
    proposed_date, proposed_time = parse_date(date), parse_time(time)
    if not proposed_date or not proposed_time:
        return reply("Choose a valid rehearsal date and time.")
    local_now = timezone.localtime()
    if proposed_date < timezone.localdate() or (proposed_date == timezone.localdate() and proposed_time <= local_now.time()):
        return reply("Choose a future rehearsal date and time.")
    try:
        PartnershipRequest.objects.create(sender=request.user, receiver=receiver, proposed_date=date, proposed_time=time, location=location, note=note)
    except IntegrityError:
        return reply("That rehearsal invitation already exists.")
    Notification.objects.create(user=receiver, message=f"{request.user.get_full_name()} invited you to a rehearsal.")
    return reply("Rehearsal invitation sent.", ok=True, status=201)


@approved_required
def respond_request(request, pk, action):
    if request.method != "POST" or action not in {"accept", "decline"}:
        return redirect("students:requests")
    item = get_object_or_404(PartnershipRequest, pk=pk, receiver=request.user, status="pending")
    item.status = "accepted" if action == "accept" else "declined"
    item.save(update_fields=["status"])
    if item.status == "accepted":
        first, second = sorted([item.sender, item.receiver], key=lambda user: user.id)
        Rehearsal.objects.create(student_one=first, student_two=second, date=item.proposed_date, time=item.proposed_time, location=item.location, note=item.note)
        Notification.objects.create(user=item.sender, message="Your rehearsal invitation was accepted. It is now in your preparation space.")
        Notification.objects.create(user=item.receiver, message="Rehearsal scheduled. You can confirm it once you have practised together.")
    else:
        Notification.objects.create(user=item.sender, message="Your rehearsal invitation was declined.")
    return redirect("students:requests")


@approved_required
def partnership(request):
    partnership = Partnership.objects.filter(Q(student_one=request.user) | Q(student_two=request.user)).select_related("student_one", "student_two").first()
    rehearsals = Rehearsal.objects.filter(Q(student_one=request.user) | Q(student_two=request.user)).select_related("student_one", "student_two")
    candidate_ids = {rehearsal.partner_for(request.user).id for rehearsal in rehearsals.filter(status=Rehearsal.Status.COMPLETED)}
    candidates = Profile.objects.filter(user_id__in=candidate_ids, status=Profile.Status.APPROVED).select_related("user")
    incoming_final = request.user.final_partner_proposals_received.filter(status=FinalPartnerProposal.Status.PENDING).select_related("proposer").first()
    outgoing_final = request.user.final_partner_proposals_sent.filter(status=FinalPartnerProposal.Status.PENDING).select_related("candidate").first()
    rehearsal_items = [{"item": rehearsal, "partner": rehearsal.partner_for(request.user)} for rehearsal in rehearsals]
    return render(request, "students/partnership.html", {"partnership": partnership, "rehearsals": rehearsal_items, "candidates": candidates, "incoming_final": incoming_final, "outgoing_final": outgoing_final})


@approved_required
def complete_rehearsal(request, pk):
    rehearsal = get_object_or_404(Rehearsal, pk=pk)
    if request.method != "POST" or request.user.id not in (rehearsal.student_one_id, rehearsal.student_two_id):
        return redirect("students:partnership")
    rehearsal.status = Rehearsal.Status.COMPLETED
    rehearsal.save(update_fields=["status"])
    Notification.objects.create(user=rehearsal.partner_for(request.user), message="A rehearsal was marked as completed. You can now be considered as a final dance partner.")
    messages.success(request, "Rehearsal marked as completed.")
    return redirect("students:partnership")


@approved_required
def propose_final_partner(request, user_id):
    if request.method != "POST":
        return redirect("students:partnership")
    if Partnership.objects.filter(Q(student_one=request.user) | Q(student_two=request.user)).exists():
        messages.error(request, "You already have a final dance partner.")
        return redirect("students:partnership")
    candidate = get_object_or_404(Profile, user_id=user_id, status=Profile.Status.APPROVED).user
    rehearsed = Rehearsal.objects.filter(status=Rehearsal.Status.COMPLETED).filter(Q(student_one=request.user, student_two=candidate) | Q(student_one=candidate, student_two=request.user)).exists()
    if not rehearsed:
        messages.error(request, "You can choose a final partner only after a completed rehearsal together.")
    elif FinalPartnerProposal.objects.filter(proposer=request.user, status=FinalPartnerProposal.Status.PENDING).exists():
        messages.info(request, "You already have a final-partner invitation awaiting a response.")
    else:
        FinalPartnerProposal.objects.create(proposer=request.user, candidate=candidate)
        Notification.objects.create(user=candidate, message=f"{request.user.get_full_name()} would like to choose you as their final dance partner.")
        messages.success(request, "Final-partner invitation sent.")
    return redirect("students:partnership")


@approved_required
def respond_final_partner(request, pk, action):
    if request.method != "POST" or action not in {"accept", "decline"}:
        return redirect("students:partnership")
    proposal = get_object_or_404(FinalPartnerProposal, pk=pk, candidate=request.user, status=FinalPartnerProposal.Status.PENDING)
    if action == "accept" and Partnership.objects.filter(Q(student_one=request.user) | Q(student_two=request.user)).exists():
        messages.error(request, "You already have a final dance partner.")
        return redirect("students:partnership")
    proposal.status = FinalPartnerProposal.Status.ACCEPTED if action == "accept" else FinalPartnerProposal.Status.DECLINED
    proposal.save(update_fields=["status"])
    if action == "accept":
        first, second = sorted([proposal.proposer, proposal.candidate], key=lambda user: user.id)
        Partnership.objects.get_or_create(student_one=first, student_two=second)
        Notification.objects.create(user=proposal.proposer, message="Your final dance partnership was confirmed.")
        Notification.objects.create(user=proposal.candidate, message="Your final dance partnership was confirmed. You can now use the meeting planner.")
        FinalPartnerProposal.objects.filter(proposer=proposal.proposer, status=FinalPartnerProposal.Status.PENDING).exclude(pk=proposal.pk).update(status=FinalPartnerProposal.Status.DECLINED)
    else:
        Notification.objects.create(user=proposal.proposer, message="Your final-partner invitation was declined. You can keep rehearsing with other students.")
    return redirect("students:partnership")
