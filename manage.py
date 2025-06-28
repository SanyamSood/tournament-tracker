#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TournamentTracker.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Auto-create a superuser if none exist
    if os.environ.get('RENDER_SUPERUSER_ONCE') == 'true':
        import django
        django.setup()
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
            print("✅ Superuser created")
        else:
            print("⚠️ Superuser already exists")

    main()
