from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Bill, OPDVisit, Patient


class DoctorSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "gender", "age", "phone", "address"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 2}),
        }


class OPDVisitForm(forms.ModelForm):
    class Meta:
        model = OPDVisit
        fields = ["visit_date", "symptoms", "diagnosis", "prescription", "consultation_fee"]
        widgets = {
            "visit_date": forms.DateInput(attrs={"type": "date"}),
            "symptoms": forms.Textarea(attrs={"rows": 2}),
            "diagnosis": forms.Textarea(attrs={"rows": 2}),
            "prescription": forms.Textarea(attrs={"rows": 2}),
        }


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ["total_amount", "payment_status", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
