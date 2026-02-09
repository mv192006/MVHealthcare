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
def dashboard(request: HttpRequest) -> HttpResponse:
    patients = Patient.objects.filter(created_by=request.user)[:5]
    visits = OPDVisit.objects.filter(doctor=request.user)[:5]
    return render(
        request,
        "dashboard.html",
        {"patients": patients, "visits": visits},
    )


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
            messages.success(request, "Patient registered successfully.")
            return redirect("patient_list")
    else:
        form = PatientForm()
    return render(request, "patients/patient_form.html", {"form": form})


@login_required
def patient_update(request: HttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(Patient, id=patient_id, created_by=request.user)
    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient updated successfully.")
            return redirect("patient_detail", patient_id=patient.id)
    else:
        form = PatientForm(instance=patient)
    return render(request, "patients/patient_form.html", {"form": form})


@login_required
def patient_delete(request: HttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(Patient, id=patient_id, created_by=request.user)
    if request.method == "POST":
        patient.delete()
        messages.success(request, "Patient deleted successfully.")
        return redirect("patient_list")
    return render(
        request, "patients/patient_confirm_delete.html", {"patient": patient}
    )


@login_required
def patient_detail(request: HttpRequest, patient_id: int) -> HttpResponse:
    patient = get_object_or_404(Patient, id=patient_id, created_by=request.user)
    visits = patient.visits.all()
    return render(
        request,
        "patients/patient_detail.html",
        {"patient": patient, "visits": visits},
    )


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
            messages.success(request, "OPD visit saved successfully.")
            return redirect("patient_detail", patient_id=patient.id)
    else:
        form = OPDVisitForm()
    return render(
        request,
        "visits/visit_form.html",
        {"form": form, "patient": patient},
    )


@login_required
def visit_detail(request: HttpRequest, visit_id: int) -> HttpResponse:
    visit = get_object_or_404(OPDVisit, id=visit_id, doctor=request.user)
    bill = getattr(visit, "bill", None)
    return render(
        request,
        "visits/visit_detail.html",
        {"visit": visit, "bill": bill},
    )


@login_required
def bill_create(request: HttpRequest, visit_id: int) -> HttpResponse:
    visit = get_object_or_404(OPDVisit, id=visit_id, doctor=request.user)
    if hasattr(visit, "bill"):
        messages.info(request, "Bill already exists for this visit.")
        return redirect("bill_detail", bill_id=visit.bill.id)
    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.visit = visit
            bill.save()
            messages.success(request, "Bill created successfully.")
            return redirect("bill_detail", bill_id=bill.id)
    else:
        form = BillForm(initial={"total_amount": visit.consultation_fee})
    return render(
        request,
        "billing/bill_form.html",
        {"form": form, "visit": visit},
    )


@login_required
def bill_detail(request: HttpRequest, bill_id: int) -> HttpResponse:
    bill = get_object_or_404(Bill, id=bill_id, visit__doctor=request.user)
    return render(request, "billing/bill_detail.html", {"bill": bill})


@login_required
def bill_pdf(request: HttpRequest, bill_id: int) -> HttpResponse:
    bill = get_object_or_404(Bill, id=bill_id, visit__doctor=request.user)
    template = get_template("billing/bill_pdf.html")
    html = template.render({"bill": bill})
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=bill-{bill.id}.pdf"
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        messages.error(request, "Could not generate PDF. Please try again.")
        return redirect("bill_detail", bill_id=bill.id)
    return response
