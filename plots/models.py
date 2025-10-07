from django.db import models


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
    )
    location = models.CharField(max_length=200)

    length_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    width_ft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    size_sqft = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_sqft = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    status = models.CharField(max_length=20, choices=PLOT_STATUS, default="available")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_corner = models.BooleanField(default=False)
    facing_direction = models.CharField(max_length=50, blank=True, null=True)
    block_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.plot_type} - {self.size_sqft} sqft)"
