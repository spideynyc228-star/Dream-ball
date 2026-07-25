from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, InvitationCode

class InviteRegistrationForm(UserCreationForm):
    invitation_code = forms.CharField(max_length=32, help_text="Use the one-time code issued by your school.", widget=forms.TextInput(attrs={"placeholder": "For example: DREAM-2026-01", "autocomplete": "off"}))
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "For example: maria_ivanova"}),
            "email": forms.EmailInput(attrs={"placeholder": "For example: maria@example.com"}),
            "first_name": forms.TextInput(attrs={"placeholder": "For example: Maria"}),
            "last_name": forms.TextInput(attrs={"placeholder": "For example: Ivanova"}),
        }
    def clean_invitation_code(self):
        value = self.cleaned_data["invitation_code"].strip().upper()
        try: self.invite = InvitationCode.objects.get(code__iexact=value, is_active=True, used_by__isnull=True)
        except InvitationCode.DoesNotExist: raise forms.ValidationError("This invitation code is unavailable.")
        if not self.invite.available:
            raise forms.ValidationError("This invitation code has expired or is no longer available.")
        return value
    def save(self, commit=True):
        user = super().save(commit=False); user.role = self.invite.role
        if user.role == User.Role.ADMIN:
            user.is_staff = True
        if commit: user.save(); self.invite.used_by = user; self.invite.is_active = False; self.invite.save(update_fields=["used_by", "is_active"])
        return user
