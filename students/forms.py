from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator

from .models import Profile


class ProfileForm(forms.ModelForm):
    REHEARSAL_TIME_CHOICES = [
        ("After school", "After school"),
        ("Early evening", "Early evening"),
        ("Weekends", "Weekends"),
        ("Flexible", "Flexible — we can agree together"),
    ]

    preferred_rehearsal_time = forms.MultipleChoiceField(
        choices=REHEARSAL_TIME_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="When can you rehearse?",
        help_text="Select every time that normally works for you.",
    )
    nickname = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        label="Nickname",
        help_text="This is your unique sign-in name. Use letters, numbers and @/./+/-/_ only.",
        widget=forms.TextInput(attrs={"placeholder": "For example: maria_dances"}),
    )

    class Meta:
        model=Profile
        fields=["photo","photo_position_x","photo_position_y","photo_scale","grade","class_letter","gender","height","bio","dance_experience","preferred_rehearsal_time","agreed_to_rules"]
        widgets={
            "grade": forms.Select(choices=[("", "Choose your grade"), ("9", "Grade 9"), ("10", "Grade 10"), ("11", "Grade 11"), ("12", "Grade 12")]),
            "class_letter": forms.TextInput(attrs={"placeholder": "For example: A"}),
            "gender": forms.Select(choices=[("", "Choose for matching"), ("female", "Female"), ("male", "Male")]),
            "height": forms.NumberInput(attrs={"placeholder": "For example: 168", "min": "120", "max": "230"}),
            "bio":forms.Textarea(attrs={"rows":4, "placeholder": "For example: I enjoy music, school events and learning a new dance step. I would be happy to prepare calmly and respectfully."}),
            "dance_experience": forms.Select(choices=[("", "Choose an option"), ("Beginner", "Beginner - I am just starting"), ("Some experience", "Some experience - I have tried a few dances"), ("Intermediate", "Intermediate - I attend classes or practise regularly"), ("Experienced", "Experienced - I feel confident dancing")]),
            "photo":forms.ClearableFileInput(attrs={"accept":"image/jpeg,image/png,image/webp"}),
            "photo_position_x": forms.HiddenInput(),
            "photo_position_y": forms.HiddenInput(),
            "photo_scale": forms.HiddenInput(),
            "agreed_to_rules":forms.CheckboxInput(attrs={"required": True}),
        }

        help_texts = {
            "grade": "Select the grade you are currently in.",
            "class_letter": "Use the class letter your school uses, such as A or B.",
            "gender": "Used only to show opposite-gender dance matches in the directory.",
            "height": "This is optional context for dance partnerships; enter centimetres only.",
            "bio": "Keep it friendly and event-focused. Do not include contact details or private information.",
            "dance_experience": "Choose the description that feels most accurate today.",
        }

        labels = {
            "gender": "Gender for dance matching",
            "agreed_to_rules": "I agree to the site policy",
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user and not self.is_bound:
            self.initial["nickname"] = self.user.username
        if not self.is_bound and self.instance.preferred_rehearsal_time:
            self.initial["preferred_rehearsal_time"] = [
                value.strip()
                for value in self.instance.preferred_rehearsal_time.split("|")
                if value.strip()
            ]

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"].strip()
        users = get_user_model().objects.filter(username__iexact=nickname)
        if self.user:
            users = users.exclude(pk=self.user.pk)
        if users.exists():
            raise forms.ValidationError("This nickname is already taken. Please choose another one.")
        return nickname

    def clean_preferred_rehearsal_time(self):
        return " | ".join(self.cleaned_data["preferred_rehearsal_time"])

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Please upload an image smaller than 5 MB.")
        return photo

    def clean_photo_position_x(self):
        return min(100, max(0, self.cleaned_data["photo_position_x"]))

    def clean_photo_position_y(self):
        return min(100, max(0, self.cleaned_data["photo_position_y"]))

    def clean_photo_scale(self):
        return min(220, max(100, self.cleaned_data["photo_scale"]))

    def clean(self):
        cleaned = super().clean()
        required = ["grade", "class_letter", "gender", "height", "bio", "dance_experience", "preferred_rehearsal_time"]
        for field in required:
            if not cleaned.get(field):
                self.add_error(field, "Please complete this field before submitting for review.")
        if not cleaned.get("agreed_to_rules"):
            self.add_error("agreed_to_rules", "You must agree to the community rules.")
        return cleaned
