from django.db import models
from django.db.models import Sum
from django.utils import timezone
from bookings.models import Booking, Payment, PaymentSource
from expenses.models import Expense


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]

    date = models.DateField(default=timezone.now)
    type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    source = models.ForeignKey(
        PaymentSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    related_payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    related_booking = models.ForeignKey(
        Booking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    related_expense = models.ForeignKey(
        Expense,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.date} — {self.type.upper()} — Rs {self.amount}"

    @classmethod
    def get_summary(cls, start_date=None, end_date=None):
        qs = cls.objects.all()
        if start_date and end_date:
            qs = qs.filter(date__range=[start_date, end_date])

        debit_total = (
            qs.filter(type="debit").aggregate(total=Sum("amount"))["total"] or 0
        )
        credit_total = (
            qs.filter(type="credit").aggregate(total=Sum("amount"))["total"] or 0
        )
        balance = credit_total - debit_total
        return {
            "debit_total": debit_total,
            "credit_total": credit_total,
            "balance": balance,
        }
