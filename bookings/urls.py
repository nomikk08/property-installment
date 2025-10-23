from django.urls import path
from . import views

urlpatterns = [
    path("", views.bookings_page, name="bookings_page"),
    path("bookings/<int:booking_id>/", views.booking_detail, name="booking_detail"),
    path(
        "payments/<int:payment_id>/mark-paid/",
        views.mark_payment_paid,
        name="mark_payment_paid",
    ),
    path(
        "<int:pk>/download-pdf/",
        views.download_booking_pdf,
        name="download_booking_pdf",
    ),
    path("create-booking/", views.create_booking_combined, name="create_booking_combined"),
    path("api/plot/<int:pk>/", views.api_get_plot, name="api_get_plot"),
    path("api/buyer/<int:pk>/", views.api_get_buyer, name="api_get_buyer"),
]
