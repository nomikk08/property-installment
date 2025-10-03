from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def bookings_page(request):
    # Admin/staff can see all bookings
    if request.user.is_staff:
        bookings = Booking.objects.select_related("buyer", "plot", "plan").prefetch_related("payments")
    else:
        bookings = Booking.objects.filter(buyer=request.user).select_related("plot", "plan").prefetch_related("payments")

    return render(request, "bookings/bookings_page.html", {"bookings": bookings})
