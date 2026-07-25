from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProfileForm
from .models import Partnership, PartnershipRequest, Profile
from notifications.models import Notification

def approved_required(view):
    def wrapped(request,*args,**kwargs):
        if not hasattr(request.user,"profile") or request.user.profile.status != Profile.Status.APPROVED:
            return redirect("students:profile")
        return view(request,*args,**kwargs)
    return login_required(wrapped)

@login_required
def profile(request):
    if request.user.role != "student":
        return redirect("moderation:dashboard")
    profile, _=Profile.objects.get_or_create(user=request.user)
    form=ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method=="POST" and form.is_valid():
        profile=form.save(commit=False); profile.status=Profile.Status.PENDING; profile.moderation_note=""; profile.save()
        messages.success(request,"Your profile was submitted for moderation."); return redirect("students:profile")
    return render(request,"students/profile.html",{"form":form,"profile":profile})

@approved_required
def browse(request):
    profiles=Profile.objects.filter(status=Profile.Status.APPROVED).exclude(user=request.user).select_related("user")
    q=request.GET.get("q","")
    if q: profiles=profiles.filter(Q(user__first_name__icontains=q)|Q(user__last_name__icontains=q)|Q(bio__icontains=q))
    for field in ("grade","dance_experience"):
        if request.GET.get(field): profiles=profiles.filter(**{field:request.GET[field]})
    if request.GET.get("height_min"): profiles=profiles.filter(height__gte=request.GET["height_min"])
    return render(request,"students/browse.html",{"profiles":profiles,"grades":Profile.objects.values_list("grade",flat=True).distinct(),"experiences":Profile.objects.values_list("dance_experience",flat=True).distinct()})

@approved_required
def requests_page(request):
    return render(request,"students/requests.html",{"incoming":request.user.received_partnership_requests.filter(status="pending").select_related("sender"),"outgoing":request.user.sent_partnership_requests.select_related("receiver")})

@approved_required
def send_request(request,user_id):
    if request.method!="POST": return redirect("students:browse")
    receiver=get_object_or_404(Profile,user_id=user_id,status="approved").user
    if receiver==request.user: messages.error(request,"You cannot invite yourself.")
    elif Partnership.objects.filter(Q(student_one=request.user)|Q(student_two=request.user)).exists(): messages.error(request,"You already have a confirmed partnership.")
    elif PartnershipRequest.objects.filter(sender=request.user, status=PartnershipRequest.Status.PENDING).exists(): messages.error(request,"You already have an active partnership request. You can send one request at a time.")
    elif PartnershipRequest.objects.filter(sender=receiver, receiver=request.user, status=PartnershipRequest.Status.PENDING).exists(): messages.info(request,"This student has already sent you a request. Please respond from Requests.")
    else:
        try:
            PartnershipRequest.objects.create(sender=request.user,receiver=receiver); Notification.objects.create(user=receiver,message=f"{request.user.get_full_name()} sent a partnership request."); messages.success(request,"Partnership request sent.")
        except IntegrityError: messages.info(request,"That request already exists.")
    return redirect("students:browse")

@approved_required
def respond_request(request,pk,action):
    if request.method != "POST" or action not in {"accept", "decline"}:
        return redirect("students:requests")
    item=get_object_or_404(PartnershipRequest,pk=pk,receiver=request.user,status="pending")
    if action == "accept" and Partnership.objects.filter(Q(student_one=request.user)|Q(student_two=request.user)).exists():
        messages.error(request, "You already have a confirmed partnership.")
        return redirect("students:requests")
    item.status="accepted" if action=="accept" else "declined"; item.save()
    if item.status=="accepted":
        first,second=sorted([item.sender,item.receiver],key=lambda x:x.id); Partnership.objects.get_or_create(student_one=first,student_two=second); Notification.objects.create(user=item.sender,message="Your partnership request was accepted. Your meeting planner is ready.")
        PartnershipRequest.objects.filter(sender=item.sender, status=PartnershipRequest.Status.PENDING).exclude(pk=item.pk).update(status=PartnershipRequest.Status.DECLINED)
        Notification.objects.create(user=item.receiver,message="Partnership confirmed. You can now plan a rehearsal together.")
    else:
        Notification.objects.create(user=item.sender,message="Your partnership request was declined.")
    return redirect("students:requests")

@approved_required
def partnership(request):
    partnership=Partnership.objects.filter(Q(student_one=request.user)|Q(student_two=request.user)).select_related("student_one","student_two").first()
    return render(request,"students/partnership.html",{"partnership":partnership})
