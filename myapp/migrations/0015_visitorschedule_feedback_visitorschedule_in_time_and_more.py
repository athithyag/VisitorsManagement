# Generated by Django 5.1.3 on 2024-12-12 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_visitorschedule_verification_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitorschedule',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visitorschedule',
            name='in_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visitorschedule',
            name='out_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visitorschedule',
            name='total_duration',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
