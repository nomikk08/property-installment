from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone

from bookings.models import Booking, Payment
from plots.models import Plot
from expenses.models import Expense

from datetime import datetime
from reportlab.pdfgen import canvas


def earnings_page(request):
    # Total Plot Sales Value (all booked plots)
    total_plot_value = (
        Plot.objects.filter(status="sold").aggregate(total=Sum("price"))["total"] or 0
    )

    # Total Received (Down payments + Paid installments)
    total_received = (
        Booking.objects.aggregate(total_down=Sum("down_payment_amount")).get(
            "total_down"
        )
        or 0
    ) + (
        Payment.objects.filter(is_paid=True)
        .aggregate(total_inst=Sum("amount"))
        .get("total_inst")
        or 0
    )

    # Total Pending Amount (remaining installments)
    total_installment_value = (
        Payment.objects.aggregate(total=Sum("amount"))["total"] or 0
    )
    total_pending = total_installment_value - (
        Payment.objects.filter(is_paid=True).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    # Total Expenses
    total_expenses = Expense.objects.aggregate(total=Sum("amount"))["total"] or 0

    # Net Profit
    net_profit = total_received - total_expenses

    context = {
        "total_plot_value": total_plot_value,
        "total_received": total_received,
        "total_pending": total_pending,
        "total_expenses": total_expenses,
        "net_profit": net_profit,
    }

    return render(request, "reports/earnings_page.html", context)


def download_earnings_pdf(request):
    # Fetch Data
    total_plot_value = (
        Plot.objects.filter(status="sold").aggregate(total=Sum("price"))["total"] or 0
    )
    total_received = (
        Booking.objects.aggregate(total_down=Sum("down_payment_amount")).get(
            "total_down"
        )
        or 0
    ) + (
        Payment.objects.filter(is_paid=True)
        .aggregate(total_inst=Sum("amount"))
        .get("total_inst")
        or 0
    )
    total_installment_value = (
        Payment.objects.aggregate(total=Sum("amount"))["total"] or 0
    )
    total_pending = total_installment_value - (
        Payment.objects.filter(is_paid=True).aggregate(total=Sum("amount"))["total"]
        or 0
    )
    total_expenses = Expense.objects.aggregate(total=Sum("amount"))["total"] or 0
    net_profit = total_received - total_expenses

    # PDF response setup
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=Earnings_Report.pdf"

    p = canvas.Canvas(response)
    y = 800

    # Title
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Earnings Report - Abrar Green City")
    y -= 40

    # Summary Section
    summary_data = [
        ("Total Plot Sales Value", total_plot_value),
        ("Total Received", total_received),
        ("Pending Amount", total_pending),
        ("Total Expenses", total_expenses),
        ("Net Profit", net_profit),
    ]

    p.setFont("Helvetica", 11)
    for label, value in summary_data:
        p.drawString(50, y, f"{label}: Rs {value}")
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Bookings Revenue Breakdown:")
    y -= 30

    # Table Headers
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Plot")
    p.drawString(180, y, "Buyer")
    p.drawString(300, y, "Paid")
    p.drawString(380, y, "Pending")
    y -= 20

    # Table Data
    p.setFont("Helvetica", 9)
    bookings = Booking.objects.all().select_related("plot", "buyer")
    for b in bookings:
        paid = b.total_paid_amount
        pending = b.plot.price - paid

        p.drawString(50, y, str(b.plot.title))
        p.drawString(180, y, str(b.buyer.name))
        p.drawString(300, y, f"{paid}")
        p.drawString(380, y, f"{pending}")
        y -= 15

        if y < 50:  # Auto new page
            p.showPage()
            y = 800

    p.save()
    return response

def daily_report(request):
    # Get selected date or default to today
    date_str = request.GET.get("date")
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    # ✅ Expenses for the day
    daily_expenses = Expense.objects.filter(date=selected_date)
    total_expenses = daily_expenses.aggregate(total=Sum("amount"))["total"] or 0

    # ✅ Sales (Bookings) for the day (down payments)
    daily_bookings = Booking.objects.filter(start_date=selected_date)
    total_booking_income = (
        daily_bookings.aggregate(total=Sum("down_payment_amount"))["total"] or 0
    )

    # ✅ Payments marked as paid on selected date (Installments)
    daily_installments = Payment.objects.filter(
        is_paid=True, paid_date=selected_date
    ).select_related("booking")
    total_installment_income = (
        daily_installments.aggregate(total=Sum("amount"))["total"] or 0
    )

    # ✅ Combine totals
    total_income = total_booking_income + total_installment_income
    net_profit = total_income - total_expenses

    context = {
        "selected_date": selected_date,
        "daily_expenses": daily_expenses,
        "daily_bookings": daily_bookings,
        "daily_installments": daily_installments,
        "total_expenses": total_expenses,
        "total_income": total_income,
        "total_booking_income": total_booking_income,
        "total_installment_income": total_installment_income,
        "net_profit": net_profit,
    }

    return render(request, "reports/daily_report.html", context)

