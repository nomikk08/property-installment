from django.db import models
from django.utils import timezone

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("development", "Development Cost"),
        ("marketing", "Marketing & Ads"),
        ("maintenance", "Maintenance"),
        ("commission", "Agent Commission"),
        ("utility", "Utility Bills"),
        ("misc", "Miscellaneous"),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="misc")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"
