from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("signup/", views.signup, name="signup"),
    path("patients/", views.patient_list, name="patient_list"),
    path("patients/new/", views.patient_create, name="patient_create"),
    path("patients/<int:patient_id>/", views.patient_detail, name="patient_detail"),
    path(
        "patients/<int:patient_id>/edit/",
        views.patient_update,
        name="patient_update",
    ),
    path(
        "patients/<int:patient_id>/delete/",
        views.patient_delete,
        name="patient_delete",
    ),
    path(
        "patients/<int:patient_id>/visits/new/",
        views.visit_create,
        name="visit_create",
    ),
    path("visits/<int:visit_id>/", views.visit_detail, name="visit_detail"),
    path("visits/<int:visit_id>/bill/", views.bill_create, name="bill_create"),
    path("billing/<int:bill_id>/", views.bill_detail, name="bill_detail"),
    path("billing/<int:bill_id>/pdf/", views.bill_pdf, name="bill_pdf"),
]
