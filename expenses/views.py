from django.shortcuts import render, redirect
from django.db.models import Sum
from django.forms import modelformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, ExpenseCategoryForm

from bookings.models import PaymentSource

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime


@login_required
def expense_list(request):
    expenses = Expense.objects.select_related("category", "source").order_by("-date")

    # Filters
    category_id = request.GET.get("category")
    source_id = request.GET.get("source")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if category_id:
        expenses = expenses.filter(category_id=category_id)

    if source_id:
        expenses = expenses.filter(source_id=source_id)

    if date_from:
        expenses = expenses.filter(date__gte=date_from)

    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    # Compute totals by type: treat 'expense' and 'debit' as debits, 'credit' as credits
    debit_total = (
        expenses.filter(type__in=["expense", "debit"]).aggregate(total=Sum("amount"))[
            "total"
        ]
        or 0
    )
    credit_total = (
        expenses.filter(type="credit").aggregate(total=Sum("amount"))["total"] or 0
    )
    total_expense = debit_total - credit_total

    context = {
        "expenses": expenses,
        "total_expense": total_expense,
        "selected_category": int(category_id) if category_id else None,
        "selected_source": int(source_id) if source_id else None,
        "date_from": date_from,
        "date_to": date_to,
        "categories": ExpenseCategory.objects.all(),
        "sources": PaymentSource.objects.filter(is_active=True),
    }

    return render(request, "expenses/expense_list.html", context)


def download_expenses_pdf(request):
    expenses = Expense.objects.select_related("category", "source").order_by("-date")

    # Apply filters safely
    category_id = request.GET.get("category")
    source_id = request.GET.get("source")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    # ✅ Filter: Category
    if category_id and category_id.isdigit():
        expenses = expenses.filter(category_id=int(category_id))

    # ✅ Filter: Payment Source
    if source_id and source_id.isdigit():
        expenses = expenses.filter(source_id=int(source_id))

    # ✅ Filter: Date Range
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    # ---------- PDF GENERATION ----------
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=Expenses_Report.pdf"

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 60

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, y, "💸 Expense Report")
    y -= 25
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, y, "Abrar Green City — Generated Report")
    y -= 30

    # Filters summary
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Filters Applied:")
    p.setFont("Helvetica", 9)
    filters = []

    if category_id and category_id.isdigit():
        filters.append(f"Category ID: {category_id}")

    if source_id and source_id.isdigit():
        src = PaymentSource.objects.filter(id=int(source_id)).first()
        filters.append(f"Source: {src.name if src else '—'}")

    if date_from:
        filters.append(f"From: {date_from}")
    if date_to:
        filters.append(f"To: {date_to}")

    p.drawString(140, y, ", ".join(filters) if filters else "None")
    y -= 30

    # Table Header
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Date")
    p.drawString(110, y, "Title")
    p.drawString(250, y, "Category")
    p.drawString(320, y, "Type")
    p.drawString(400, y, "Source")
    p.drawString(470, y, "Amount")
    y -= 15
    p.line(50, y, 550, y)
    y -= 10

    # Table Rows
    p.setFont("Helvetica", 9)
    total_amount = 0

    for exp in expenses:
        if y < 60:
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 9)

        category_name = exp.category.name if exp.category else "—"
        source_name = exp.source.name if getattr(exp, "source", None) else "—"
        p.drawString(50, y, str(exp.date))
        p.drawString(110, y, exp.title[:25])
        p.drawString(250, y, category_name[:15])
        p.drawString(320, y, exp.get_type_display()[:8])
        p.drawString(400, y, source_name[:15])
        # Show amount and adjust total based on type
        display_amount = f"Rs {exp.amount}"
        p.drawRightString(540, y, display_amount)
        y -= 15
        if exp.type in ("expense", "debit"):
            total_amount += exp.amount or 0
        else:
            total_amount -= exp.amount or 0

    # Total
    y -= 15
    p.line(50, y, 550, y)
    y -= 20
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(540, y, f"Total: Rs {total_amount:.2f}")

    p.showPage()
    p.save()
    return response


def manage_expenses(request):
    ExpenseFormSet = modelformset_factory(
        Expense,
        form=ExpenseForm,
        extra=3,
        can_delete=False,
    )

    payment_sources = PaymentSource.objects.filter(is_active=True)

    if request.method == "POST":
        # --- Add new category ---
        if "add_category" in request.POST:
            category_form = ExpenseCategoryForm(request.POST)
            formset = ExpenseFormSet(queryset=Expense.objects.none())
            if category_form.is_valid():
                category_form.save()
                messages.success(request, "✅ New category added successfully.")
                return redirect("manage_expenses")

        # --- Save expenses ---
        elif "save_expenses" in request.POST:
            category_form = ExpenseCategoryForm()
            formset = ExpenseFormSet(request.POST, queryset=Expense.objects.none())

            valid_forms = []
            for form in formset:
                if form.is_valid():
                    title = form.cleaned_data.get("title")
                    amount = form.cleaned_data.get("amount")
                    if title or amount:
                        valid_forms.append(form)

            if valid_forms:
                for form in valid_forms:
                    form.save()
                messages.success(request, "💾 Expenses saved successfully.")
                return redirect("expense_list")
            else:
                messages.warning(
                    request, "Please fill at least one valid expense form."
                )
    else:
        category_form = ExpenseCategoryForm()
        formset = ExpenseFormSet(queryset=Expense.objects.none())

    return render(
        request,
        "expenses/manage_expenses.html",
        {
            "category_form": category_form,
            "formset": formset,
            "payment_sources": payment_sources,
        },
    )
