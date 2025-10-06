from django.db import models

from accounts.models import Buyer
from plots.models import InstallmentPlan, Plot

# Create your models here.

class Booking(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="bookings")
    plot = models.OneToOneField(Plot, on_delete=models.CASCADE)  # One plot → One booking
    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE)
    down_payment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_installment = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.buyer.username} - {self.plot.title}"
    
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.booking.plot.title} - {self.amount} - {'Paid' if self.is_paid else 'Pending'}"

