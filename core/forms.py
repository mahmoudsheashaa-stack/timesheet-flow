from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import UserProfile, Timesheet, TimesheetEntry


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["hourly_rate"]


class TimesheetCreateForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ["month", "year"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now()
        self.fields["month"].initial = now.month
        self.fields["year"].initial = now.year


class TimesheetEntryForm(forms.ModelForm):
    class Meta:
        model = TimesheetEntry
        fields = ["date", "hours_worked", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
