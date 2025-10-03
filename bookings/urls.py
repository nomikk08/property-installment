from django.urls import path
from . import views

urlpatterns = [
    path("", views.bookings_page, name="bookings_page"),
]
