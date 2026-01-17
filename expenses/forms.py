from django import forms
from .models import Expense, ExpenseCategory
from bookings.models import PaymentSource


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "title",
            "category",
            "type",
            "amount",
            "source",
            "date",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "border rounded p-2 w-full"}),
            "category": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "type": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "amount": forms.NumberInput(attrs={"class": "border rounded p-2 w-full"}),
            "source": forms.Select(attrs={"class": "border rounded p-2 w-full"}),
            "date": forms.DateInput(
                attrs={"type": "date", "class": "border rounded p-2 w-full"}
            ),
            "description": forms.Textarea(
                attrs={"rows": 1, "class": "border rounded p-2 w-full"}
            ),
        }


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "border rounded p-2 w-full"}),
        }
