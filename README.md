# Clinic MVP (Hospital/Clinic Management System - India)

This project is a beginner-friendly Django MVP for small clinics in India. It covers patient registration, OPD visit records, billing with PDF receipts, and doctor authentication.

## 1. Project Folder Structure

```
MVHealthcare/
├── clinic/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── registration/
│       │   ├── login.html
│       │   └── signup.html
│       ├── patients/
│       │   ├── patient_confirm_delete.html
│       │   ├── patient_detail.html
│       │   ├── patient_form.html
│       │   └── patient_list.html
│       ├── visits/
│       │   ├── visit_detail.html
│       │   └── visit_form.html
│       └── billing/
│           ├── bill_detail.html
│           ├── bill_form.html
│           └── bill_pdf.html
├── clinic_mgmt/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── requirements.txt
```

## 2. Setup Instructions (Local)

1. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE clinic_mvp;
   CREATE USER clinic_mvp WITH PASSWORD 'clinic_mvp';
   GRANT ALL PRIVILEGES ON DATABASE clinic_mvp TO clinic_mvp;
   ```

4. **Set environment variables**
   ```bash
   export POSTGRES_DB=clinic_mvp
   export POSTGRES_USER=clinic_mvp
   export POSTGRES_PASSWORD=clinic_mvp
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export DJANGO_SECRET_KEY="your-secret"
   export DJANGO_DEBUG=True
   # Optional for quick local demo without Postgres:
   # export USE_SQLITE=True
   ```

5. **Run migrations and create admin user**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start the server**
   ```bash
   python manage.py runserver
   ```

7. **Open in browser**
   Visit `http://127.0.0.1:8000/`

## 3. Deployment Guide (Render / Railway)

### Render
1. Create a new **PostgreSQL** database on Render.
2. Create a **Web Service** with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn clinic_mgmt.wsgi:application`
3. Set environment variables:
   - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
   - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`
4. Add `ALLOWED_HOSTS` with your Render domain in `settings.py`.
5. Run migrations using Render Shell: `python manage.py migrate`.

### Railway
1. Create a new project and add PostgreSQL plugin.
2. Deploy the repo. Set the same environment variables as above.
3. Use command: `python manage.py migrate` after deploy.

## 4. Database Schema (`models.py`)

```python
from django.conf import settings
from django.db import models
from django.utils import timezone


class Patient(models.Model):
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="patients"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class OPDVisit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="visits"
    )
    visit_date = models.DateField(default=timezone.now)
    symptoms = models.TextField()
    diagnosis = models.TextField()
    prescription = models.TextField()
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)


class Bill(models.Model):
    visit = models.OneToOneField(OPDVisit, on_delete=models.CASCADE, related_name="bill")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=[("paid", "Paid"), ("pending", "Pending")],
        default="pending",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## 5. Views (`views.py`)

```python
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template

from xhtml2pdf import pisa

from .forms import BillForm, DoctorSignupForm, OPDVisitForm, PatientForm
from .models import Bill, OPDVisit, Patient


def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = DoctorSignupForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("patient_list")
    else:
        form = DoctorSignupForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def patient_list(request: HttpRequest) -> HttpResponse:
    patients = Patient.objects.filter(created_by=request.user)
    return render(request, "patients/patient_list.html", {"patients": patients})


@login_required
def patient_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            return redirect("patient_list")
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form})


@login_required
def visit_create(request: HttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(Patient, id=patient_id, created_by=request.user)
    if request.method == "POST":
        form = OPDVisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.patient = patient
            visit.doctor = request.user
            visit.save()
            return redirect("patient_detail", patient_id=patient.id)
    else:
        form = OPDVisitForm()
    return render(request, "visits/visit_form.html", {"form": form, "patient": patient})


@login_required
def bill_pdf(request: HttpRequest, bill_id: int) -> HttpResponse:
    bill = get_object_or_404(Bill, id=bill_id, visit__doctor=request.user)
    template = get_template("billing/bill_pdf.html")
    html = template.render({"bill": bill})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=bill-{bill.id}.pdf"
    pisa.CreatePDF(html, dest=response)
    return response
```

## 6. URLs (`urls.py`)

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("patients/", views.patient_list, name="patient_list"),
    path("patients/new/", views.patient_create, name="patient_create"),
    path("patients/<int:patient_id>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:patient_id>/edit/", views.patient_update, name="patient_update"),
    path("patients/<int:patient_id>/delete/", views.patient_delete, name="patient_delete"),
    path("patients/<int:patient_id>/visits/new/", views.visit_create, name="visit_create"),
    path("visits/<int:visit_id>/", views.visit_detail, name="visit_detail"),
    path("visits/<int:visit_id>/bill/", views.bill_create, name="bill_create"),
    path("billing/<int:bill_id>/", views.bill_detail, name="bill_detail"),
    path("billing/<int:bill_id>/pdf/", views.bill_pdf, name="bill_pdf"),
]
```

## 7. Templates (HTML + Bootstrap)

Each template is placed in `clinic/templates/` and uses Bootstrap CDN. Example base template:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Clinic MVP</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
  </head>
  <body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <a class="navbar-brand" href="/">Clinic MVP</a>
      </div>
    </nav>
  </body>
</html>
```

## 8. PDF Generation

We use `xhtml2pdf` for simple HTML → PDF receipts. The PDF template is `clinic/templates/billing/bill_pdf.html` and the view is `bill_pdf`.

## 9. Security & Best Practices

- All patient/visit/billing views are protected with `@login_required`.
- User input is validated using Django Forms.
- CSRF protection is enabled by default in Django templates.
- Doctor-specific data is filtered per logged-in user.

## 10. Next Steps

- Add file uploads (e.g., reports).
- Add more detailed billing items.
- Add staff roles (nurse/receptionist).
- Add backups/export CSV.
