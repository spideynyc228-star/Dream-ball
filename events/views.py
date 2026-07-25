from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render
from notifications.models import Notification
from students.models import Partnership
from .models import Meeting
class MeetingForm(forms.ModelForm):
    class Meta: model=Meeting; fields=["date","time","location","notes"]; widgets={"date":forms.DateInput(attrs={"type":"date"}),"time":forms.TimeInput(attrs={"type":"time"})}
@login_required
def planner(request):
    p=Partnership.objects.filter(student_one=request.user).first() or Partnership.objects.filter(student_two=request.user).first()
    if not p:return redirect("students:partnership")
    form=MeetingForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        meeting=form.save(commit=False); meeting.partnership=p; meeting.save()
        messages.success(request, "Meeting saved. Your partner has been notified.")
        return redirect("events:planner")
    return render(request,"events/planner.html",{"form":form,"meetings":p.meetings.all()})
