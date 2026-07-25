from django import forms
from .models import Profile
class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=["grade","class_letter","height","bio","dance_experience","personality","preferred_rehearsal_time","photo","agreed_to_rules"]
        widgets={"bio":forms.Textarea(attrs={"rows":4}),"photo":forms.ClearableFileInput(attrs={"accept":"image/jpeg,image/png,image/webp"}),"agreed_to_rules":forms.CheckboxInput()}

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError("Please upload an image smaller than 5 MB.")
        return photo

    def clean(self):
        cleaned = super().clean()
        required = ["grade", "class_letter", "height", "bio", "dance_experience", "personality", "preferred_rehearsal_time"]
        for field in required:
            if not cleaned.get(field):
                self.add_error(field, "Please complete this field before submitting for review.")
        if not cleaned.get("agreed_to_rules"):
            self.add_error("agreed_to_rules", "You must agree to the community rules.")
        return cleaned
