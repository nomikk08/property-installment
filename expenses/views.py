from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from .models import Expense
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from datetime import datetime

@login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by("-date")

    # Filters
    category = request.GET.get("category")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if category:
        expenses = expenses.filter(category=category)

    if date_from:
        expenses = expenses.filter(date__gte=date_from)

    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    total_expense = expenses.aggregate(total=Sum("amount"))["total"] or 0

    context = {
        "expenses": expenses,
        "total_expense": total_expense,
        "selected_category": category,
        "date_from": date_from,
        "date_to": date_to,
        "categories": Expense.CATEGORY_CHOICES,
    }
    return render(request, "expenses/expense_list.html", context)

def download_expenses_pdf(request):
    expenses = Expense.objects.all().order_by("-date")

    # Apply same filters to PDF too
    category = request.GET.get("category")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if category and category != "None":
        expenses = expenses.filter(category=category)

    if date_from and date_from != "None":
        expenses = expenses.filter(date__gte=date_from)

    if date_to and date_to != "None":
        expenses = expenses.filter(date__lte=date_to)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=Expenses_Report.pdf"

    p = canvas.Canvas(response)
    y = 800

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Expense Report")
    y -= 40

    for exp in expenses:
        p.setFont("Helvetica", 10)
        p.drawString(
            50,
            y,
            f"{exp.date} - {exp.title} ({exp.get_category_display()}) - Rs {exp.amount}"
        )
        y -= 15
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response
