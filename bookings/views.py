from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.db import transaction
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import BuyerForm, PlotForm, BookingForm
from .models import Booking, Payment

from accounts.models import Buyer
from plots.models import Plot

from reportlab.pdfgen import canvas

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


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
    if request.method == "POST":
        received_by = request.POST.get("received_by")  # ✅ Get selected receiver
        payment.is_paid = True
        payment.paid_date = timezone.now().date()
        payment.received_by = received_by  # ✅ Save receiver
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

@staff_required
def create_booking_combined(request):
    """
    Unified page to select/add Buyer and Plot and create Booking.
    Only staff users allowed (change decorator if you want different permission).
    """
    buyer_form = BuyerForm(prefix="buyer")
    plot_form = PlotForm(prefix="plot")
    booking_form = BookingForm(prefix="booking")

    buyers = Buyer.objects.order_by("name")[:200] 
    plots = Plot.objects.filter(status="available").order_by("title")[:500]

    if request.method == "POST":
        # Use transaction to ensure consistency
        with transaction.atomic():
            # Decide buyer: existing or new
            buyer_choice = request.POST.get("buyer_select")
            if buyer_choice and buyer_choice != "new":
                buyer = get_object_or_404(Buyer, id=int(buyer_choice))
            else:
                buyer_form = BuyerForm(request.POST, prefix="buyer")
                if buyer_form.is_valid():
                    buyer = buyer_form.save()
                else:
                    messages.error(request, "Please fix buyer form errors.")
                    # fall through to render with errors

            # Decide plot: existing or new
            plot_choice = request.POST.get("plot_select")
            if plot_choice and plot_choice != "new":
                plot = get_object_or_404(Plot, id=int(plot_choice))
            else:
                plot_form = PlotForm(request.POST, prefix="plot")
                if plot_form.is_valid():
                    plot = plot_form.save()
                else:
                    messages.error(request, "Please fix plot form errors.")
                    # fall through to render with errors

            # If any form invalid, render page with errors
            # Check forms validity before creating booking
            if (buyer_choice == "new" and not buyer_form.is_valid()) or (
                plot_choice == "new" and not plot_form.is_valid()
            ):
                # fall through to render with forms containing errors
                pass
            else:
                # Booking details
                booking_form = BookingForm(request.POST, prefix="booking")
                if booking_form.is_valid():
                    booking = booking_form.save(commit=False)
                    booking.buyer = buyer
                    booking.plot = plot
                    booking.save()

                    # Set plot status to sold
                    plot.status = "sold"
                    plot.save()

                    messages.success(request, "Booking created successfully.")
                    return redirect("booking_detail", booking_id=booking.id)
                else:
                    messages.error(request, "Please fix booking form errors.")

    context = {
        "buyer_form": buyer_form,
        "plot_form": plot_form,
        "booking_form": booking_form,
        "buyers": buyers,
        "plots": plots,
    }
    return render(request, "bookings/booking_create_combined.html", context)

@require_GET
@staff_required
def api_get_plot(request, pk):
    plot = get_object_or_404(Plot, id=pk)
    data = {
        "id": plot.id,
        "title": plot.title,
        "plot_type": plot.plot_type,
        "location": plot.location,
        "length_ft": str(plot.length_ft) if plot.length_ft is not None else "",
        "width_ft": str(plot.width_ft) if plot.width_ft is not None else "",
        "size_sqft": str(plot.size_sqft) if plot.size_sqft is not None else "",
        "price": str(plot.price),
        "price_per_sqft": str(plot.price_per_sqft) if plot.price_per_sqft is not None else "",
        "is_corner": plot.is_corner,
        "facing_direction": plot.facing_direction or "",
        "block_name": plot.block_name or "",
        "status": plot.status,
    }
    return JsonResponse(data)

@require_GET
@staff_required
def api_get_buyer(request, pk):
    buyer = get_object_or_404(Buyer, id=pk)
    data = {
        "id": buyer.id,
        "name": buyer.name,
        "father_name": buyer.father_name,
        "contact_no": buyer.contact_no,
        "cnic": buyer.cnic,
        "address": buyer.address,
        "inheritor": buyer.inheritor,
        "inheritor_cnic": buyer.inheritor_cnic,
        "inheritor_relation": buyer.inheritor_relation,
    }
    return JsonResponse(data)