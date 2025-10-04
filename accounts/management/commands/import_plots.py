import csv
from django.core.management.base import BaseCommand
from plots.models import Plot

class Command(BaseCommand):
    help = "Import plots from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                plot, created = Plot.objects.update_or_create(
                    title=row["title"],
                    defaults={
                        "plot_type": row["plot_type"],
                        "location": row["location"],
                        "length_ft": row.get("length_ft") or None,
                        "width_ft": row.get("width_ft") or None,
                        "size_sqft": row["size_sqft"],
                        "size_sq_yards": row.get("size_sq_yards") or None,
                        "price": row["price"],
                        "price_per_sqft": row.get("price_per_sqft") or None,
                        "status": row.get("status", "available"),
                        "is_corner": row.get("is_corner", "False").lower() in ("true", "1"),
                        "facing_direction": row.get("facing_direction") or "",
                        "block_name": row.get("block_name") or "",
                    },
                )
                count += 1
                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f"{action}: {plot}"))

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully imported {count} plots"))
