import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from results.models import ClassRoom, Student


class Command(BaseCommand):
    help = 'Import students from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str,
                            help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='') as file:
            reader = csv.reader(file, delimiter=',')
            next(reader)  # Skip the header row
            for row in reader:
                fullname = row[0].strip()
                roll_id = row[1].strip()
                number = row[2].strip()
                phone_number = row[3].strip()
                class_name = row[4].strip().upper()
                gender = row[5].strip().upper()
                hostel = row[6].strip() if row[6].strip() != 'N/A' else None
                date_of_birth = row[7].strip()

                # Ensure gender matches the choices
                if gender == 'MALE':
                    gender = 'M'
                elif gender == 'FEMALE':
                    gender = 'F'
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Invalid gender for student {fullname}, skipping row'))
                    gender = 'NA'

                # Ensure class_name matches the choices
                class_name_map = {
                    'Nursery ONE': 'N1',
                    'NURSERY ONE': 'N1',
                    'Nursery one': 'N1',
                    'Nursery TWO': 'N2',
                    'Nursery Two': 'N2',
                    'NURSERY TWO': 'N2',

                    'PLAYGROUP ONE': 'PG1',
                    'PLAYGROUP TWO': 'PG2',
                    'YEAR ONE': 'Y1',
                    'YEAR TWO': 'Y2',
                    'YEAR THREE': 'Y3',
                    'YEAR FOUR': 'Y4',
                    'YEAR FIVE': 'Y5',
                    'YEAR SIX': 'Y6',
                }
                class_name = class_name_map.get(class_name)
                try:
                    class_name = ClassRoom.objects.get(name=class_name)
                    print(class_name)
                except Exception as e:
                    break
                if not class_name:
                    self.stdout.write(self.style.WARNING(
                        f'Invalid class name for student {fullname}, skipping row'))
                    continue

                # Convert date_of_birth to a date object
                try:
                    if date_of_birth:
                        date_of_birth = datetime.strptime(
                            date_of_birth, '%Y-%m-%d %H:%M:%S').date()
                    else:
                        date_of_birth = None
                except ValueError:
                    self.stdout.write(self.style.WARNING(
                        f'Invalid date format for student {fullname}, skipping row'))
                    continue

                # Update or create the student object
                student, created = Student.objects.update_or_create(
                    roll_id=roll_id,
                    defaults={
                        'fullname': fullname,
                        'number': number,
                        'phone_number': phone_number,
                        'classroom': class_name,
                        'gender': gender,
                        'hostel': hostel,
                        'date_of_birth': date_of_birth
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully created student {fullname}'))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully updated student {fullname}'))

        self.stdout.write(self.style.SUCCESS('Import completed'))
