# Generated by Django 5.2.1 on 2025-06-07 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0003_booking_showtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='trailer_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
