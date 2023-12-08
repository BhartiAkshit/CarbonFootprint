# Generated by Django 4.2 on 2023-12-01 06:21

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('adminapp', '0004_emissionreductiontip'),
        ('userapp', '0011_alter_dailyfoodchoice_entry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyfoodchoice',
            name='entry_date',
            field=models.DateField(default=datetime.date(2023, 12, 1)),
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminapp.emissionreductiontip')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]