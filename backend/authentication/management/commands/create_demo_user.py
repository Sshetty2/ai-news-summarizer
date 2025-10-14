from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Creates a demo user for testing purposes"

    def handle(self, *args, **kwargs):
        username = "demo_user"
        password = "demo123"  # Simple password for demo purposes
        email = "demo@example.com"

        # Check if demo user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Demo user "{username}" already exists.')
            )
            return

        # Create demo user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name="Demo",
            last_name="User",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created demo user "{username}" with password "{password}"'
            )
        )
