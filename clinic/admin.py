from django.contrib import admin

from .models import Bill, OPDVisit, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "created_by", "created_at")
    search_fields = ("first_name", "last_name", "phone")


@admin.register(OPDVisit)
class OPDVisitAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "visit_date", "consultation_fee")
    search_fields = ("patient__first_name", "patient__last_name")


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("visit", "total_amount", "payment_status", "created_at")
    list_filter = ("payment_status",)
