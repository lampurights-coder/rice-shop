from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo staff user (09120000000 / staffpass1)"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="09120000000",
            defaults={"is_staff": True, "is_superuser": True},
        )
        user.is_staff = True
        user.is_superuser = True
        user.set_password("staffpass1")
        user.save()
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} staff user 09120000000 / staffpass1"))
