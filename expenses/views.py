from django.shortcuts import render
from django.db.models import Sum
from .models import Expense
from django.contrib.auth.decorators import login_required

# @login_required
def expense_list(request):
    expenses = Expense.objects.all().order_by("-date")
    total_expense = expenses.aggregate(total=Sum("amount"))["total"] or 0
    return render(request, "expenses/expense_list.html", {
        "expenses": expenses,
        "total_expense": total_expense
    })
