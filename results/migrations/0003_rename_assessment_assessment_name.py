# Generated by Django 5.1.3 on 2024-12-01 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assessment',
            old_name='assessment',
            new_name='name',
        ),
    ]