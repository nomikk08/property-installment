from django.db import models

# Create your models here.


class Plot(models.Model):
    PLOT_STATUS = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("sold", "Sold"),
    ]

    PLOT_TYPE = [
        ("commercial", "Commercial"),
        ("residential", "Residential"),
    ]

    title = models.CharField(max_length=100)
    plot_type = models.CharField(
        max_length=20, choices=PLOT_TYPE, default="residential"
    )  # Commercial or Residential
    location = models.CharField(max_length=200)

    # Dimensions
    length_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    width_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    size_sqft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # For "1500 SFT" etc.
    size_sq_yards = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_sqft = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # Availability
    status = models.CharField(max_length=20, choices=PLOT_STATUS, default="available")

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Extra
    is_corner = models.BooleanField(
        default=False
    )  # corner plots often have higher value
    facing_direction = models.CharField(
        max_length=50, blank=True, null=True
    )  # e.g. "North", "East"
    block_name = models.CharField(
        max_length=50, blank=True, null=True
    )  # e.g. "Block A"

    def __str__(self):
        return f"{self.title} ({self.plot_type} - {self.size_sqft} sqft)"


class InstallmentPlan(models.Model):
    name = models.CharField(max_length=50)
    down_payment_percent = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # e.g. 20% down
    duration_months = models.IntegerField()  # e.g. 24 months

    def __str__(self):
        return f"{self.name} - {self.duration_months} months"
