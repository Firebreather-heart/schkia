# Generated by Django 5.1.3 on 2024-12-03 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parent',
            name='student',
        ),
        migrations.AddField(
            model_name='parent',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='parents', to='results.student'),
        ),
    ]
