# Generated by Django 4.2 on 2023-12-04 09:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userapp', '0013_alter_dailyfoodchoice_entry_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmissionGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('petrol_goal', models.FloatField(blank=True, null=True)),
                ('diesel_goal', models.FloatField(blank=True, null=True)),
                ('electricity_goal', models.FloatField(blank=True, null=True)),
                ('food_goal', models.FloatField(blank=True, null=True)),
                ('total_goal', models.FloatField(blank=True, null=True)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='emission_goal', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
