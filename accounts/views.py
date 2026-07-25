from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import InviteRegistrationForm

@ensure_csrf_cookie
def register(request):
    form = InviteRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(); login(request, user)
        if user.role != "student":
            messages.success(request, "Welcome to the Dream Ball operations console.")
            return redirect("moderation:dashboard")
        messages.success(request, "Welcome to Dream Ball. Complete your profile for review.")
        return redirect("students:profile")
    return render(request, "accounts/register.html", {"form": form})

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = AuthenticationForm

    def get_success_url(self):
        if self.request.user.role != "student":
            return "/moderation/"
        return super().get_success_url()
