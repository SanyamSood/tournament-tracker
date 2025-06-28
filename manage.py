#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TournamentTracker.settings')

    # ✅ Auto-create a superuser if needed
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

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
