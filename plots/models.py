from django.db import models

# Create your models here.

class Plot(models.Model):
    PLOT_STATUS = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("sold", "Sold"),
    ]
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    size_sq_yards = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PLOT_STATUS, default="available")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.location}"

class InstallmentPlan(models.Model):
    name = models.CharField(max_length=50)
    down_payment_percent = models.DecimalField(max_digits=5, decimal_places=2)  # e.g. 20% down
    duration_months = models.IntegerField()  # e.g. 24 months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # optional

    def __str__(self):
        return f"{self.name} - {self.duration_months} months"
