from django.core.management.base import BaseCommand
from django.core.management import call_command
from results.models import GradeType
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Sets up initial school data - classrooms, students, and grade types'

    def handle(self, *args, **kwargs):
        try:
            # Populate classrooms
            self.stdout.write('Creating classrooms...')
            call_command('populate_classes')
            self.stdout.write(self.style.SUCCESS(
                'Classrooms created successfully'))

            # Import students
            self.stdout.write('Importing students...')
            call_command('import_students', 'students.csv')
            self.stdout.write(self.style.SUCCESS(
                'Students imported successfully'))

            # Create grade types
            self.stdout.write('Creating grade types...')
            default_grades = [
                ('EX', 'Excellent', True),
                ('VG', 'Very Good', False),
                ('G', 'Good', False),
                ('W.I.P', 'Work in Progress', False),
                ('NA', 'Not Applicable', False),
            ]

            for code, label, is_default in default_grades:
                GradeType.objects.get_or_create(
                    code=code,
                    defaults={
                        'label': label,
                        'is_default': is_default
                    }
                )
            self.stdout.write(self.style.SUCCESS(
                'Grade types created successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Error during setup: {str(e)}'))
            raise

        CustomUser.objects.create_superuser( #type:ignore
            username='sitemaker',
            password = 'sitepass',
        )

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str,
                            help='Path to students CSV file')
