from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.http import require_GET

from .forms import BuyerForm, PlotForm, BookingForm
from .models import Booking, Payment, PaymentSource

from accounts.models import Buyer
from plots.models import Plot

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


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
    next_due = payments.filter(is_paid=False).order_by("due_date").first()
    payment_sources = PaymentSource.objects.filter(is_active=True)

    if request.method == "POST" and next_due:
        if str(next_due.id) == request.POST.get("payment_id"):
            next_due.due_date = request.POST.get("due_date") or next_due.due_date
            next_due.amount = request.POST.get("amount") or next_due.amount
            next_due.received_by = (
                request.POST.get("received_by") or next_due.received_by
            )

            source_id = request.POST.get("payment_source")
            if source_id:
                next_due.source_id = source_id

            if "mark_paid" in request.POST:
                next_due.is_paid = True
                next_due.paid_date = timezone.now().date()
                messages.success(request, "✅ Payment marked as paid successfully!")
            else:
                messages.success(request, "✅ Payment updated successfully!")

            next_due.save()
            return redirect("booking_detail", booking_id=booking.id)

    return render(
        request,
        "bookings/booking_detail.html",
        {
            "booking": booking,
            "payments": payments,
            "next_due": next_due,
            "payment_sources": payment_sources,
        },
    )


@login_required
def mark_payment_paid(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    booking = payment.booking

    if request.method == "POST":
        received_by = request.POST.get("received_by")
        payment.is_paid = True
        payment.paid_date = timezone.now().date()
        payment.received_by = received_by
        payment.save()

        messages.success(request, f"✅ Payment for {payment.due_date} marked as PAID.")

    return redirect("booking_detail", booking_id=booking.id)


def download_booking_pdf(request, pk):
    booking = Booking.objects.select_related("buyer", "plot").get(id=pk)
    payments = booking.payments.select_related("source").all().order_by("due_date")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=Booking_{booking.id}.pdf"

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - inch

    # -------- HEADER --------
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "Abrar Green City - Booking Report")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawCentredString(
        width / 2, y, f"Generated on {timezone.now().strftime('%b %d, %Y, %I:%M %p')}"
    )
    y -= 40

    # -------- BOOKING SUMMARY --------
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, f"📄 Booking Summary (ID: {booking.id})")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(60, y, f"Installment Months: {booking.installment_months}")
    y -= 15
    p.drawString(60, y, f"Monthly Installment: Rs {booking.monthly_installment}")
    y -= 15
    p.drawString(60, y, f"Down Payment: Rs {booking.down_payment_amount}")
    y -= 15
    p.drawString(60, y, f"Total Paid: Rs {booking.total_paid_amount}")
    y -= 15
    p.drawString(60, y, f"Source: {booking.source.name if booking.source else '-'}")
    y -= 15
    remaining = float(booking.plot.price or 0) - float(booking.total_paid_amount or 0)
    p.drawString(60, y, f"Remaining Balance: Rs {remaining:.2f}")
    y -= 25

    # -------- BUYER INFO --------
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "👤 Buyer Details")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(60, y, f"Name: {booking.buyer.name}")
    y -= 15
    p.drawString(60, y, f"Father's Name: {booking.buyer.father_name}")
    y -= 15
    p.drawString(60, y, f"CNIC: {booking.buyer.cnic}")
    y -= 15
    p.drawString(60, y, f"Contact: {booking.buyer.contact_no}")
    y -= 15
    p.drawString(60, y, f"Address: {booking.buyer.address}")
    y -= 15
    p.drawString(60, y, f"Inheritor: {booking.buyer.inheritor}")
    y -= 15
    p.drawString(60, y, f"Inheritor CNIC: {booking.buyer.inheritor_cnic}")
    y -= 15
    p.drawString(60, y, f"Relation: {booking.buyer.inheritor_relation}")
    y -= 25

    # -------- PLOT INFO --------
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "🏡 Plot Details")
    y -= 20
    p.setFont("Helvetica", 10)
    p.drawString(60, y, f"Title: {booking.plot.title}")
    y -= 15
    p.drawString(60, y, f"Location: {booking.plot.location}")
    y -= 15
    p.drawString(60, y, f"Type: {booking.plot.plot_type.title()}")
    y -= 15
    p.drawString(60, y, f"Block: {booking.plot.block_name}")
    y -= 15
    p.drawString(60, y, f"Size: {booking.plot.size_sqft} sqft")
    y -= 15
    p.drawString(60, y, f"Facing Direction: {booking.plot.facing_direction}")
    y -= 15
    p.drawString(60, y, f"Corner Plot: {'Yes' if booking.plot.is_corner else 'No'}")
    y -= 15
    p.drawString(60, y, f"Price per Sqft: Rs {booking.plot.price_per_sqft}")
    y -= 15
    p.drawString(60, y, f"Total Price: Rs {booking.plot.price}")
    y -= 25

    # -------- PAYMENT SCHEDULE --------
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "💳 Payment Schedule")
    y -= 20

    # Table Header
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Due Date")
    p.drawString(120, y, "Amount")
    p.drawString(190, y, "Status")
    p.drawString(250, y, "Paid Date")
    p.drawString(320, y, "Received By")
    p.drawString(420, y, "Source")
    y -= 15
    p.line(50, y, 550, y)
    y -= 10

    # Table Rows
    p.setFont("Helvetica", 9)
    for pay in payments:
        if y < 60:
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 9)

        status = "✅ PAID" if pay.is_paid else "⏳ Pending"
        paid_date = pay.paid_date.strftime("%Y-%m-%d") if pay.paid_date else "-"
        receiver = pay.get_received_by_display() if pay.received_by else "-"
        source = pay.source.name if getattr(pay, "source", None) else "-"

        p.drawString(50, y, str(pay.due_date))
        p.drawString(120, y, f"Rs {pay.amount}")
        p.drawString(190, y, status)
        p.drawString(250, y, paid_date)
        p.drawString(320, y, receiver[:15])
        p.drawString(420, y, source[:20])
        y -= 15

    p.showPage()
    p.save()
    return response


@staff_required
@staff_required
def create_booking_combined(request):
    buyers = Buyer.objects.order_by("name")[:200]
    plots = Plot.objects.filter(status="available").order_by("title")[:500]
    payment_sources = PaymentSource.objects.filter(is_active=True)

    buyer_form = BuyerForm(prefix="buyer")
    plot_form = PlotForm(prefix="plot")
    booking_form = BookingForm(prefix="booking")

    if request.method == "POST":
        with transaction.atomic():
            # ---------------- Buyer ----------------
            buyer_choice = request.POST.get("buyer_select")
            if buyer_choice and buyer_choice != "new":
                buyer = get_object_or_404(Buyer, id=int(buyer_choice))
                buyer_form = BuyerForm(request.POST, instance=buyer, prefix="buyer")
                if buyer_form.is_valid():
                    buyer = buyer_form.save()
                else:
                    messages.error(request, "Please fix buyer form errors.")
            else:
                buyer_form = BuyerForm(request.POST, prefix="buyer")
                if buyer_form.is_valid():
                    buyer = buyer_form.save()
                else:
                    messages.error(request, "Please fix buyer form errors.")

            # ---------------- Plot ----------------
            plot_choice = request.POST.get("plot_select")
            if plot_choice and plot_choice != "new":
                plot = get_object_or_404(Plot, id=int(plot_choice))
                plot_form = PlotForm(request.POST, instance=plot, prefix="plot")
                if plot_form.is_valid():
                    plot = plot_form.save()
                else:
                    messages.error(request, "Please fix plot form errors.")
            else:
                plot_form = PlotForm(request.POST, prefix="plot")
                if plot_form.is_valid():
                    plot = plot_form.save()
                else:
                    messages.error(request, "Please fix plot form errors.")

            # ---------------- Booking ----------------
            booking_form = BookingForm(request.POST, prefix="booking")
            if (
                buyer_form.is_valid()
                and plot_form.is_valid()
                and booking_form.is_valid()
            ):
                booking = booking_form.save(commit=False)
                booking.buyer = buyer
                booking.plot = plot
                booking.save()

                plot.status = "sold"
                plot.save()

                messages.success(request, "✅ Booking created successfully.")
                return redirect("booking_detail", booking_id=booking.id)
            else:
                messages.error(request, "Please fix all form errors below.")

    context = {
        "buyer_form": buyer_form,
        "plot_form": plot_form,
        "booking_form": booking_form,
        "buyers": buyers,
        "plots": plots,
        "payment_sources": payment_sources,
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
        "price_per_sqft": (
            str(plot.price_per_sqft) if plot.price_per_sqft is not None else ""
        ),
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
