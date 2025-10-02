import os

from django.contrib.auth.management.commands import createsuperuser

from django.contrib.auth import get_user_model


class Command(createsuperuser.Command):

    def handle(self, *args, **options):
        if not options["interactive"]:
            # Check if the user already exists
            User = get_user_model()
            email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.SUCCESS(f"init-superuser: Superuser {email} already exists. Skipping."))
                return

        super().handle(*args, **options)
