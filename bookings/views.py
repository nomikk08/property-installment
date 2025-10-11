from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking, Payment


# @login_required
def bookings_page(request):
    bookings = Booking.objects.select_related("buyer", "plot").prefetch_related(
        "payments"
    )

    return render(request, "bookings/bookings_page.html", {"bookings": bookings})


# @login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payments = booking.payments.order_by("due_date")
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking, "payments": payments},
    )


# @login_required
def mark_payment_paid(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    booking = payment.booking  # For redirect after marking paid

    # Update payment status
    payment.is_paid = True
    payment.paid_date = timezone.now().date()
    payment.save()

    messages.success(
        request, f"Payment for {payment.due_date} marked as PAID successfully!"
    )

    # ✅ Redirect back to booking detail page
    return redirect("booking_detail", booking_id=booking.id)
