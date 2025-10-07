from django.db import models

from accounts.models import Buyer
from plots.models import Plot
from django.db.models import Sum


class Booking(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="bookings")
    plot = models.OneToOneField(Plot, on_delete=models.CASCADE)
    installment_months = models.IntegerField(default=24)
    down_payment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_installment = models.DecimalField(max_digits=12, decimal_places=2)
    commission_paid = models.DecimalField(
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
        verbose_name="Commission Paid",
    )
    start_date = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.buyer.name} - {self.plot.title}"

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


class Payment(models.Model):
    # ToDo: create first installment when booking is created and auto add installments on the basis of pervious installments and remaining month.
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.booking.plot.title} - {self.amount} - {'Paid' if self.is_paid else 'Pending'}"
