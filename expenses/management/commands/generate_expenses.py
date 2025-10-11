from django.core.management.base import BaseCommand
from expenses.models import Expense
from django.utils.timezone import now
from datetime import timedelta
import random

class Command(BaseCommand):
    help = "Generate dummy expense data"

    def handle(self, *args, **kwargs):
        categories = [
            "development", "marketing", "maintenance", "commission", "utility", "misc"
        ]

        titles = [
            "Website Hosting",
            "Facebook Ads Campaign",
            "Office Electricity Bill",
            "Land Development Contractor Payment",
            "Commission Paid to Agent",
            "Brochure Printing",
            "Social Media Marketing Boost",
            "Water Supply Maintenance",
            "Legal Documentation Fee",
            "Office Internet Charges",
            "Excavation Machinery Rent",
            "Pamphlet Distribution Expense",
            "Billboard Advertisement",
            "CCTV Installation",
            "Cleaning & Maintenance Crew Payment",
            "Diesel for Machinery",
            "Plot Site Security Guard Salary",
            "Canopy & Stall Setup for Marketing",
            "Travel Expense for Field Visit",
            "Fuel Expense for Site Vehicles"
        ]

        self.stdout.write(self.style.WARNING("Deleting old expenses..."))
        Expense.objects.all().delete()

        self.stdout.write(self.style.WARNING("Creating new dummy expenses..."))

        for i in range(20):
            Expense.objects.create(
                title=titles[i],
                category=random.choice(categories),
                amount=random.randint(5000, 150000),
                description="Auto-generated test expense data.",
                date=now().date() - timedelta(days=random.randint(1, 120))
            )

        self.stdout.write(self.style.SUCCESS("✅ Dummy expenses added successfully!"))
