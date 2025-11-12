from django.db import models

from accounts.models import Buyer
from plots.models import Plot
from django.db.models import Sum

from datetime import date


class Booking(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="bookings")
    plot = models.OneToOneField(Plot, on_delete=models.CASCADE)
    installment_months = models.IntegerField(default=24)
    down_payment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.ForeignKey(
        "bookings.PaymentSource",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
        verbose_name="Payment Source",
    )
    monthly_installment = models.DecimalField(max_digits=12, decimal_places=2)
    commission_paid = models.DecimalField(
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name="Commission Paid",
    )
    start_date = models.DateField(default=date.today)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.buyer.name} - {self.plot.title}"

    def save(self, *args, **kwargs):
        created = self.pk is None  # Check if this is a new Booking
        super().save(*args, **kwargs)
        if created:
            self.plot.status = "sold"  # or Plot.STATUS_SOLD if using choices constant
            self.plot.save()

    @property
    def total_paid_amount(self):
        total = (
            self.payments.filter(is_paid=True).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        if self.down_payment_amount:
            total += self.down_payment_amount
        return total

    @property
    def plot_price(self):
        return self.plot.price if self.plot else 0

    @property
    def paid_installments(self):
        return self.payments.filter(is_paid=True).count()

    @property
    def remaining_installments(self):
        return self.installment_months - self.paid_installments


class PaymentSource(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Payment Source"
        verbose_name_plural = "Payment Sources"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Payment(models.Model):
    RECEIVER_CHOICES = [
        ("tasawur", "Tasawur"),
        ("abdul_ghafoor", "Abdul Ghafoor"),
    ]
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.ForeignKey(
        PaymentSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Payment Source",
    )
    due_date = models.DateField()
    received_by = models.CharField(
        max_length=50, choices=RECEIVER_CHOICES, default="abdul_ghafoor"
    )
    paid_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.booking.plot.title} - {self.amount} - {'Paid' if self.is_paid else 'Pending'}"

    @property
    def is_next_due(self):
        unpaid_payments = self.booking.payments.filter(is_paid=False).order_by(
            "due_date"
        )
        return unpaid_payments.exists() and unpaid_payments.first().id == self.id
