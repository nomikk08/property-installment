from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booking


@login_required
def bookings_page(request):
    bookings = Booking.objects.select_related("buyer", "plot").prefetch_related(
        "payments"
    )

    return render(request, "bookings/bookings_page.html", {"bookings": bookings})
