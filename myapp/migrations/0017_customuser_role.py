# Generated by Django 5.1.3 on 2025-01-29 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_alter_visitorschedule_in_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Team Member 1', 'Team Member 1'), ('Team Member 2', 'Team Member 2')], default='Admin', max_length=50),
        ),
    ]
