from django import forms
from .models import Profile
class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=["grade","class_letter","gender","height","bio","dance_experience","personality","preferred_rehearsal_time","photo","agreed_to_rules"]
        widgets={
            "grade": forms.Select(choices=[("", "Choose your grade"), ("9", "Grade 9"), ("10", "Grade 10"), ("11", "Grade 11"), ("12", "Grade 12")]),
            "class_letter": forms.TextInput(attrs={"placeholder": "For example: A"}),
            "gender": forms.Select(choices=[("", "Choose for matching"), ("female", "Female"), ("male", "Male")]),
            "height": forms.NumberInput(attrs={"placeholder": "For example: 168", "min": "120", "max": "230"}),
            "bio":forms.Textarea(attrs={"rows":4, "placeholder": "For example: I enjoy music, school events and learning a new dance step. I would be happy to prepare calmly and respectfully."}),
            "dance_experience": forms.Select(choices=[("", "Choose an option"), ("Beginner", "Beginner - I am just starting"), ("Some experience", "Some experience - I have tried a few dances"), ("Intermediate", "Intermediate - I attend classes or practise regularly"), ("Experienced", "Experienced - I feel confident dancing")]),
            "personality": forms.Select(choices=[("", "Choose an option"), ("Calm", "Calm and thoughtful"), ("Creative", "Creative and curious"), ("Outgoing", "Outgoing and sociable"), ("Organised", "Organised and practical")]),
            "preferred_rehearsal_time": forms.Select(choices=[("", "Choose an option"), ("After school", "After school"), ("Early evening", "Early evening"), ("Weekends", "Weekends"), ("Flexible", "Flexible - we can agree together")]),
            "photo":forms.ClearableFileInput(attrs={"accept":"image/jpeg,image/png,image/webp"}),
            "agreed_to_rules":forms.CheckboxInput(attrs={"required": True}),
        }

        help_texts = {
            "grade": "Select the grade you are currently in.",
            "class_letter": "Use the class letter your school uses, such as A or B.",
            "gender": "Used only to show opposite-gender dance matches in the directory.",
            "height": "This is optional context for dance partnerships; enter centimetres only.",
            "bio": "Keep it friendly and event-focused. Do not include contact details or private information.",
            "dance_experience": "Choose the description that feels most accurate today.",
            "personality": "Pick the option that best describes how you like to prepare with others.",
            "preferred_rehearsal_time": "Choose a time that usually works for your schedule.",
        }

        labels = {
            "gender": "Gender for dance matching",
            "agreed_to_rules": "I agree to the site policy",
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Please upload an image smaller than 5 MB.")
        return photo

    def clean(self):
        cleaned = super().clean()
        required = ["grade", "class_letter", "gender", "height", "bio", "dance_experience", "personality", "preferred_rehearsal_time"]
        for field in required:
            if not cleaned.get(field):
                self.add_error(field, "Please complete this field before submitting for review.")
        if not cleaned.get("agreed_to_rules"):
            self.add_error("agreed_to_rules", "You must agree to the community rules.")
        return cleaned
