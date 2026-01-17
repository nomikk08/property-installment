from django.db import models
from django.utils import timezone
from decimal import Decimal
from bookings.models import PaymentSource


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name


class Expense(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE, related_name="expenses"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    TYPE_CHOICES = [
        ("expense", "Expense"),
        ("debit", "Debit"),
        ("credit", "Credit"),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="expense")
    source = models.ForeignKey(
        PaymentSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
        help_text="Select how this expense was paid (e.g., Cash, Bank)",
    )
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"

    @property
    def signed_amount(self):
        """Return amount with sign according to `type`.

        - `expense`/`debit` are treated as positive debits (outflow)
        - `credit` is treated as positive credit (inflow)

        Callers can compute net by subtracting credits from debits.
        """
        if self.type == "credit":
            return Decimal(self.amount)
        return Decimal(self.amount)
