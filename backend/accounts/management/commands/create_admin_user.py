"""
Create a superuser for the admin dashboard from .env or environment.
Usage: python manage.py create_admin_user

Put in backend/.env:
  ADMIN_EMAIL=admin@example.com
  ADMIN_PASSWORD=your-secure-password
  ADMIN_FULL_NAME=Admin Name  (optional)
"""
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def load_dotenv():
    """Load .env from project root (backend/) into os.environ."""
    env_path = Path(settings.BASE_DIR) / '.env'
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


class Command(BaseCommand):
    help = "Create superuser from ADMIN_EMAIL and ADMIN_PASSWORD (and optional ADMIN_FULL_NAME)."

    def handle(self, *args, **options):
        load_dotenv()
        email = os.environ.get('ADMIN_EMAIL', '').strip()
        password = os.environ.get('ADMIN_PASSWORD', '')
        full_name = os.environ.get('ADMIN_FULL_NAME', 'Admin').strip()

        if not email or not password:
            self.stderr.write(
                self.style.ERROR(
                    'Set ADMIN_EMAIL and ADMIN_PASSWORD in .env (or environment), then run:\n'
                    '  python manage.py create_admin_user'
                )
            )
            return

        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(self.style.WARNING(f'User with email {email} already exists. Skipped.'))
            return

        User.objects.create_superuser(email=email, password=password, full_name=full_name)
        self.stdout.write(self.style.SUCCESS(f'Superuser created: {email}'))
