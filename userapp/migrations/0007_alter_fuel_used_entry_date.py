# Generated by Django 4.2.6 on 2023-11-28 10:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0006_alter_fuel_used_entry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fuel_used',
            name='entry_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]