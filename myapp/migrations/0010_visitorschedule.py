# Generated by Django 5.1.3 on 2024-12-07 05:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_remove_visitor_attendee_availability_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VisitorSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Rescheduled', 'Rescheduled')], default='Pending', max_length=50)),
                ('rescheduled_date', models.DateField(blank=True, null=True)),
                ('rescheduled_time', models.TimeField(blank=True, null=True)),
                ('visitor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='myapp.visitor')),
            ],
        ),
    ]
