from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required   
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse

from .models import Booking, Payment

from reportlab.pdfgen import canvas


@login_required
def bookings_page(request):
    bookings = Booking.objects.select_related("buyer", "plot").prefetch_related(
        "payments"
    )

    return render(request, "bookings/bookings_page.html", {"bookings": bookings})


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payments = booking.payments.order_by("due_date")
    return render(
        request,
        "bookings/booking_detail.html",
        {"booking": booking, "payments": payments},
    )


@login_required
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


def download_booking_pdf(request, pk):
    booking = Booking.objects.select_related("buyer", "plot").get(id=pk)
    payments = booking.payments.all()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=Booking_{booking.id}.pdf"

    p = canvas.Canvas(response)
    y = 800

    # Title
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, f"Booking Summary - #{booking.id}")
    y -= 40

    # Buyer Info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Buyer Information:")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(60, y, f"Name: {booking.buyer.name}")
    y -= 15
    p.drawString(60, y, f"CNIC: {booking.buyer.cnic}")
    y -= 15
    p.drawString(60, y, f"Contact: {booking.buyer.contact_no}")
    y -= 30

    # Plot Info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Plot Information:")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(60, y, f"Plot: {booking.plot.title}")
    y -= 15
    p.drawString(60, y, f"Price: Rs {booking.plot.price}")
    y -= 15
    p.drawString(60, y, f"Installments: {booking.installment_months} months")
    y -= 30

    # Payment Summary
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Payment Schedule:")
    y -= 20
    p.setFont("Helvetica", 10)

    for pay in payments:
        status = "PAID" if pay.is_paid else "Pending"
        paid_date = pay.paid_date.strftime("%Y-%m-%d") if pay.paid_date else "-"
        p.drawString(
            60, y, f"{pay.due_date} — Rs {pay.amount} — {status} (Paid: {paid_date})"
        )
        y -= 15
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response
