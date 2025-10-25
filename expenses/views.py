from django.shortcuts import render, redirect
from django.db.models import Sum
from django.forms import modelformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, ExpenseCategoryForm

from reportlab.pdfgen import canvas
from datetime import datetime

@login_required
def expense_list(request):
    expenses = Expense.objects.select_related("category").order_by("-date")

    # Filters
    category_id = request.GET.get("category")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if category_id:
        expenses = expenses.filter(category_id=category_id)

    if date_from:
        expenses = expenses.filter(date__gte=date_from)

    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    total_expense = expenses.aggregate(total=Sum("amount"))["total"] or 0

    context = {
        "expenses": expenses,
        "total_expense": total_expense,
        "selected_category": int(category_id) if category_id else None,
        "date_from": date_from,
        "date_to": date_to,
        "categories": ExpenseCategory.objects.all(),
    }

    return render(request, "expenses/expense_list.html", context)

def download_expenses_pdf(request):
    expenses = Expense.objects.select_related("category").order_by("-date")

    # Apply same filters to PDF too
    category_id = request.GET.get("category")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")

    if category_id and category_id != "None":
        expenses = expenses.filter(category_id=category_id)

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
        category_name = exp.category.name if exp.category else "—"
        line = f"{exp.date} - {exp.title} ({category_name}) - Rs {exp.amount}"
        p.drawString(50, y, line)

        y -= 15
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response

def manage_expenses(request):
    ExpenseFormSet = modelformset_factory(
        Expense,
        form=ExpenseForm,
        extra=3,  # show 3 blank forms
        can_delete=False,
    )

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
                # Must call is_valid() before accessing cleaned_data
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
                messages.warning(request, "Please fill at least one valid expense form.")
    else:
        category_form = ExpenseCategoryForm()
        formset = ExpenseFormSet(queryset=Expense.objects.none())

    return render(
        request,
        "expenses/manage_expenses.html",
        {"category_form": category_form, "formset": formset},
    )