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

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


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

    class Meta:
        ordering = ["-visit_date", "-id"]

    def __str__(self) -> str:
        return f"Visit {self.id} - {self.patient}"


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

    def __str__(self) -> str:
        return f"Bill {self.id} - {self.visit.patient}"
