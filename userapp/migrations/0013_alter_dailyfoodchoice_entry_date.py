# Generated by Django 4.2 on 2023-12-01 09:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0012_alter_dailyfoodchoice_entry_date_favorite'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyfoodchoice',
            name='entry_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]