# Generated by Django 4.2.6 on 2023-11-29 06:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0009_dailystreak'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyfoodchoice',
            name='entry_date',
            field=models.DateField(default=datetime.date(2023, 11, 29)),
        ),
    ]
