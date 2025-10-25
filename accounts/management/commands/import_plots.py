import random
from django.core.management.base import BaseCommand
from plots.models import Plot

class Command(BaseCommand):
    help = "Generate 242 sample plots with random details"

    def handle(self, *args, **kwargs):
        price_per_sqft = 2500
        total_created = 0

        directions = ["North", "South", "East", "West", "North-East", "South-West"]
        blocks = ["A", "B", "C", "D", "E"]
        locations = [
            "Main Boulevard", "Park View", "Corner Street", "Lake View", "Central Avenue",
            "Sunset Road", "Hill View", "Green Block", "Market Road", "Riverside Lane"
        ]

        self.stdout.write(self.style.WARNING("Deleting all existing plots..."))
        deleted_count, _ = Plot.objects.all().delete()
        self.stdout.write(self.style.WARNING(f"🗑️ Deleted {deleted_count} existing plots."))

        def create_plots(count, plot_type, length, width):
            nonlocal total_created
            for i in range(1, count + 1):
                size_sqft = length * width
                price = size_sqft * price_per_sqft
                Plot.objects.create(
                    title=f"{plot_type.capitalize()} Plot {total_created + 1}",
                    plot_type=plot_type,
                    location=random.choice(locations),
                    length_ft=length,
                    width_ft=width,
                    size_sqft=size_sqft,
                    price=price,
                    price_per_sqft=price_per_sqft,
                    status="available",
                    is_corner=random.choice([True, False]),
                    facing_direction=random.choice(directions),
                    block_name=random.choice(blocks),
                )
                total_created += 1

        # Commercial plots
        create_plots(3, "commercial", 36, 100)   # 3600 sqft
        create_plots(7, "commercial", 30, 100)   # 3000 sqft
        create_plots(7, "commercial", 30, 50)    # 1500 sqft
        
        create_plots(1, "commercial", 40, 100)   # 4000 sqft
        create_plots(1, "commercial", 50, 80)    # 4000 sqft
        create_plots(1, "commercial", 45, 90)    # 4050 sqft

        # Residential plots
        create_plots(16, "residential", 30, 50)  # 1500 sqft
        create_plots(18, "residential", 27, 50)  # 1350 sqft
        create_plots(17, "residential", 30, 45)  # 1350 sqft
        create_plots(27, "residential", 30, 40)  # 1200 sqft
        create_plots(31, "residential", 24, 45)  # 1080 sqft
        create_plots(58, "residential", 20, 36)  # 720 sqft

        # Remaining 58th batch – random sizes to complete 242
        for _ in range(55):
            l = random.choice([18, 20, 22, 25, 28, 30])
            w = random.choice([30, 32, 35, 36, 38])
            size_sqft = l * w
            price = size_sqft * price_per_sqft
            Plot.objects.create(
                title=f"Residential Plot {total_created + 1}",
                plot_type="residential",
                location=random.choice(locations),
                length_ft=l,
                width_ft=w,
                size_sqft=size_sqft,
                price=price,
                price_per_sqft=price_per_sqft,
                status="available",
                is_corner=random.choice([True, False]),
                facing_direction=random.choice(directions),
                block_name=random.choice(blocks),
            )
            total_created += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully created {total_created} plots"))
