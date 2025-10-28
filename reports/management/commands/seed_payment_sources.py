# transactions/management/commands/seed_payment_sources.py

from django.core.management.base import BaseCommand
from reports.models import PaymentSource


class Command(BaseCommand):
    help = "Seed default payment sources such as Cash and bank accounts"

    DEFAULT_SOURCES = [
        {"name": "Cash", "description": "Cash transactions"},
        {"name": "Meezan Bank", "description": "Meezan Bank Main Account"},
        {"name": "HBL", "description": "Habib Bank Limited Business Account"},
        {"name": "Bank Al Habib", "description": "Bank Al Habib Account"},
        {"name": "UBL", "description": "United Bank Limited Account"},
        {"name": "JazzCash", "description": "Mobile wallet account"},
        {"name": "EasyPaisa", "description": "Mobile wallet account"},
    ]

    def handle(self, *args, **options):
        created_count = 0
        for source_data in self.DEFAULT_SOURCES:
            obj, created = PaymentSource.objects.get_or_create(
                name=source_data["name"],
                defaults={"description": source_data["description"], "is_active": True},
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ Already exists: {obj.name}"))

        self.stdout.write(
            self.style.SUCCESS(f"\n🎉 Done! {created_count} new sources added.")
        )
