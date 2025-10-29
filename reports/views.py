from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

from bookings.models import Booking, Payment, PaymentSource
from plots.models import Plot
from expenses.models import Expense
from .models import Transaction  # ✅ NEW


# ------------------------------------------------
# Utility
# ------------------------------------------------
def parse_flexible_date(date_str):
    """Try parsing date in multiple formats."""
    if not date_str:
        return timezone.now().date()

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b. %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return timezone.now().date()


# ------------------------------------------------
# Earnings Overview (Using Transactions)
# ------------------------------------------------
def earnings_page(request):
    # ✅ Parse start/end date & source filters
    start_date = parse_flexible_date(request.GET.get("start_date"))
    end_date = parse_flexible_date(request.GET.get("end_date"))
    source_id = request.GET.get("source")

    # ✅ Base queryset
    transactions_qs = Transaction.objects.select_related("source").all()

    # ✅ Apply date range filter
    if start_date and end_date:
        transactions_qs = transactions_qs.filter(date__range=[start_date, end_date])

    # ✅ Apply payment source filter (only if valid numeric)
    if source_id and source_id.isdigit():
        transactions_qs = transactions_qs.filter(source_id=int(source_id))

    # ✅ Calculate debit, credit and balance
    debit_total = (
        transactions_qs.filter(type="debit").aggregate(total=Sum("amount"))["total"]
        or 0
    )
    credit_total = (
        transactions_qs.filter(type="credit").aggregate(total=Sum("amount"))["total"]
        or 0
    )
    balance = credit_total - debit_total

    # ✅ Context metrics
    total_plot_value = (
        Plot.objects.filter(status="sold").aggregate(total=Sum("price"))["total"] or 0
    )
    total_pending = (
        Payment.objects.filter(is_paid=False).aggregate(total=Sum("amount"))["total"]
        or 0
    )

    # ✅ Recent transactions
    transactions = transactions_qs.order_by("-date")[:50]

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "selected_source": (
            int(source_id) if source_id and source_id.isdigit() else None
        ),
        "sources": PaymentSource.objects.filter(is_active=True).order_by("name"),
        "total_plot_value": total_plot_value,
        "total_received": credit_total,
        "total_expenses": debit_total,
        "net_profit": balance,
        "total_pending": total_pending,
        "transactions": transactions,
    }

    return render(request, "reports/earnings_page.html", context)


# ------------------------------------------------
# Download Earnings PDF
# ------------------------------------------------
def download_earnings_pdf(request):
    # ✅ Parse filters safely
    start_date = parse_flexible_date(request.GET.get("start_date"))
    end_date = parse_flexible_date(request.GET.get("end_date"))
    source_id = request.GET.get("source")

    transactions_qs = Transaction.objects.select_related("source").all()

    # ✅ Apply date filters individually (not only if both provided)
    if start_date:
        transactions_qs = transactions_qs.filter(date__gte=start_date)
    if end_date:
        transactions_qs = transactions_qs.filter(date__lte=end_date)

    # ✅ Apply source filter
    if source_id and source_id.isdigit():
        transactions_qs = transactions_qs.filter(source_id=int(source_id))

    # ✅ Totals
    debit_total = (
        transactions_qs.filter(type="debit").aggregate(total=Sum("amount"))["total"]
        or 0
    )
    credit_total = (
        transactions_qs.filter(type="credit").aggregate(total=Sum("amount"))["total"]
        or 0
    )
    balance = credit_total - debit_total

    total_plot_value = (
        Plot.objects.filter(status="sold").aggregate(total=Sum("price"))["total"] or 0
    )

    # ✅ Setup PDF
    response = HttpResponse(content_type="application/pdf")
    filename = f"Earnings_Report_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
    response["Content-Disposition"] = f"attachment; filename={filename}"

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - inch

    # --- HEADER ---
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "Abrar Green City — Earnings Report")
    y -= 20

    p.setFont("Helvetica", 10)
    filter_text = f"Generated: {timezone.now().strftime('%b %d, %Y, %I:%M %p')}"
    if start_date:
        filter_text += f" | From: {start_date}"
    if end_date:
        filter_text += f" | To: {end_date}"
    if source_id and source_id.isdigit():
        src = PaymentSource.objects.filter(id=source_id).first()
        if src:
            filter_text += f" | Source: {src.name}"
    p.drawCentredString(width / 2, y, filter_text)
    y -= 40

    # --- SUMMARY ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "📊 Summary")
    y -= 20
    p.setFont("Helvetica", 10)
    for label, value in [
        ("Total Plot Sales Value", total_plot_value),
        ("Total Credit (Income)", credit_total),
        ("Total Debit (Expenses)", debit_total),
        ("Net Balance", balance),
    ]:
        p.drawString(60, y, f"{label}: Rs {value}")
        y -= 15

    y -= 25
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "🧾 Filtered Transactions")
    y -= 20

    # --- TABLE HEADERS ---
    p.setFont("Helvetica-Bold", 9)
    p.drawString(50, y, "Date")
    p.drawString(110, y, "Type")
    p.drawString(160, y, "Amount")
    p.drawString(230, y, "Source")
    p.drawString(320, y, "Description")
    y -= 10
    p.line(50, y, 550, y)
    y -= 10

    # --- TRANSACTION ROWS ---
    p.setFont("Helvetica", 8)
    for t in transactions_qs.order_by("-date")[:100]:
        if y < 60:
            p.showPage()
            y = height - inch
            p.setFont("Helvetica", 8)

        p.drawString(50, y, t.date.strftime("%Y-%m-%d"))
        p.drawString(110, y, t.type.upper())
        p.drawString(160, y, f"Rs {t.amount}")
        p.drawString(230, y, t.source.name if t.source else "—")
        p.drawString(320, y, (t.description or "-")[:45])
        y -= 12

    p.showPage()
    p.save()
    return response


# ------------------------------------------------
# Daily Report (Debit/Credit Version)
# ------------------------------------------------
def daily_report(request):
    # ✅ Selected date (default = today)
    selected_date = parse_flexible_date(request.GET.get("date"))

    # ✅ Transactions for that date
    transactions = (
        Transaction.objects.filter(date=selected_date)
        .select_related("related_booking", "related_expense", "source")
        .order_by("id")
    )

    # ✅ Overall totals
    total_credit = (
        transactions.filter(type="credit").aggregate(total=Sum("amount"))["total"] or 0
    )
    total_debit = (
        transactions.filter(type="debit").aggregate(total=Sum("amount"))["total"] or 0
    )
    closing_balance = total_credit - total_debit

    # ✅ Group summary by payment source
    source_summaries = (
        transactions.values("source__name")
        .annotate(
            credit_total=Sum("amount", filter=Q(type="credit")),
            debit_total=Sum("amount", filter=Q(type="debit")),
        )
        .order_by("source__name")
    )

    # Remove any sources where both credit and debit are None (no transactions)
    source_summaries = [
        s for s in source_summaries if (s["credit_total"] or s["debit_total"])
    ]

    context = {
        "selected_date": selected_date,
        "transactions": transactions,
        "total_credit": total_credit,
        "total_debit": total_debit,
        "closing_balance": closing_balance,
        "source_summaries": source_summaries,
    }

    return render(request, "reports/daily_report.html", context)


# ------------------------------------------------
# Download Daily Report PDF
# ------------------------------------------------
def download_daily_report_pdf(request):
    selected_date = parse_flexible_date(request.GET.get("date"))

    transactions = (
        Transaction.objects.filter(date=selected_date)
        .select_related("source")
        .order_by("type", "id")
    )

    # ✅ Separate credits and debits
    daily_credits = transactions.filter(type="credit")
    daily_debits = transactions.filter(type="debit")

    total_credit = daily_credits.aggregate(total=Sum("amount"))["total"] or 0
    total_debit = daily_debits.aggregate(total=Sum("amount"))["total"] or 0
    net_balance = total_credit - total_debit

    # ✅ Source Summary
    source_summary = (
        transactions.values("source__name")
        .annotate(
            credit_total=Sum("amount", filter=Q(type="credit")),
            debit_total=Sum("amount", filter=Q(type="debit")),
        )
        .order_by("source__name")
    )

    response = HttpResponse(content_type="application/pdf")
    filename = f"Daily_Report_{selected_date}.pdf"
    response["Content-Disposition"] = f"attachment; filename={filename}"

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - inch

    # --- HEADER ---
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "Abrar Green City — Daily Report")
    y -= 25
    p.setFont("Helvetica", 11)
    p.drawCentredString(
        width / 2,
        y,
        f"Date: {selected_date} | Generated: {timezone.now().strftime('%b %d, %Y, %I:%M %p')}",
    )
    y -= 40

    # --- CREDITS (INCOME) ---
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "💰 Credits (Income)")
    y -= 20
    p.setFont("Helvetica", 10)
    for t in daily_credits:
        src = t.source.name if t.source else "—"
        desc = t.description or "Credit"
        p.drawString(60, y, f"{desc} — {src} — Rs {t.amount}")
        y -= 15
        if y < 60:
            p.showPage()
            y = height - inch
            p.setFont("Helvetica", 10)
    y -= 10
    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, y, f"Total Credit: Rs {total_credit}")
    y -= 30

    # --- DEBITS (EXPENSES) ---
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, y, "💸 Debits (Expenses)")
    y -= 20
    p.setFont("Helvetica", 10)
    for t in daily_debits:
        src = t.source.name if t.source else "—"
        desc = t.description or "Debit"
        p.drawString(60, y, f"{desc} — {src} — Rs {t.amount}")
        y -= 15
        if y < 60:
            p.showPage()
            y = height - inch
            p.setFont("Helvetica", 10)
    y -= 10
    p.setFont("Helvetica-Bold", 11)
    p.drawString(60, y, f"Total Debit: Rs {total_debit}")
    y -= 40

    # --- SOURCE SUMMARY ---
    if source_summary:
        p.setFont("Helvetica-Bold", 13)
        p.drawString(50, y, "🏦 Source Summary")
        y -= 20
        p.setFont("Helvetica-Bold", 10)
        p.drawString(60, y, "Source")
        p.drawString(220, y, "Credit")
        p.drawString(320, y, "Debit")
        p.drawString(420, y, "Net")
        y -= 10
        p.line(50, y, 550, y)
        y -= 10
        p.setFont("Helvetica", 9)
        for s in source_summary:
            src_name = s["source__name"] or "—"
            credit = s["credit_total"] or 0
            debit = s["debit_total"] or 0
            net = credit - debit
            p.drawString(60, y, src_name[:25])
            p.drawString(220, y, f"Rs {credit}")
            p.drawString(320, y, f"Rs {debit}")
            color = "green" if net >= 0 else "red"
            p.drawString(420, y, f"Rs {net}")
            y -= 15
            if y < 60:
                p.showPage()
                y = height - inch
                p.setFont("Helvetica", 9)
        y -= 30

    # --- SUMMARY ---
    p.setFont("Helvetica-Bold", 13)
    label = "Profit" if net_balance >= 0 else "Loss"
    p.drawString(50, y, f"Net {label}: Rs {net_balance}")

    p.showPage()
    p.save()
    return response
