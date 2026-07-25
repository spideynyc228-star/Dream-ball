from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from students.models import Profile
from .models import Report
class ReportForm(forms.ModelForm):
    class Meta: model=Report; fields=["reason","details"]
@login_required
def create(request,profile_id):
    profile=get_object_or_404(Profile,pk=profile_id)
    form=ReportForm(request.POST)
    if request.method=="POST" and form.is_valid():
        Report.objects.get_or_create(reporter=request.user,profile=profile,defaults=form.cleaned_data); messages.success(request,"Thank you. A moderator will review this report.")
    return redirect("students:browse")
