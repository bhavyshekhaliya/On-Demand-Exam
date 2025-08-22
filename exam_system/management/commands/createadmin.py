from django.core.management.base import BaseCommand
from exam_system.models import Admin

class Command(BaseCommand):
    help = 'Create an admin user'

    def handle(self, *args, **options):
        try:
            admin = Admin.objects.create(
                username="admin",
                password="admin@123",
                name="System Admin",
                email="admin@example.com",
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS('Successfully created admin user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to create admin user: {str(e)}'))
