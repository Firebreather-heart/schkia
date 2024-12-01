from datetime import datetime
from django.core.management.base import BaseCommand
from results.models import ClassRoom 


class Command(BaseCommand):
    help = 'Populate classes'

    

    def handle(self, *args, **kwargs):
        NAME_CHOICES = (
            ('N1', 'Nursery 1'),
            ('N2', 'Nursery 2'),
            ('PG1', 'Playgroup 1'),
            ('PG2', 'Playgroup 2'),
            ('Y1', 'Year 1'),
            ('Y2', 'Year 2'),
            ('Y3', 'Year 3'),
            ('Y4', 'Year 4'),
            ('Y5', 'Year 5'),
            ('Y6', 'Year 6'),
        )
        classnames = [i[0] for i in NAME_CHOICES]
        for name in classnames:
            classroom = ClassRoom.objects.create(
                name = name
            )
            self.stdout.write(str(classroom))
