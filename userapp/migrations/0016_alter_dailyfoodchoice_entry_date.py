# Generated by Django 4.2.6 on 2023-12-07 09:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0015_alter_profile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyfoodchoice',
            name='entry_date',
            field=models.DateField(default=datetime.date(2023, 12, 7)),
        ),
    ]
