# Generated by Django 5.1.3 on 2024-12-06 11:26

import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_rename_work_email_profile_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='attendee_availability',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='visitor',
            name='rescheduled_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visitor',
            name='rescheduled_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='visitor',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Rescheduled', 'Rescheduled')], default='Pending', max_length=50),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='category',
            field=models.CharField(choices=[('student', 'Student'), ('college_staff', 'College Staff'), ('client', 'Client'), ('company_staff', 'Company Staff'), ('interview_internship', 'Interview or Internship Enquiry'), ('others', 'Others')], max_length=50),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='designated_attendee',
            field=models.CharField(choices=[('member1', 'Team Member 1'), ('member2', 'Team Member 2'), ('general', 'General')], max_length=50),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='documents/'),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='visitor_id',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=36, unique=True),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='visitor_name',
            field=models.CharField(max_length=255),
        ),
    ]
