# Generated by Django 5.1.3 on 2024-12-09 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_visitor_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitor',
            name='status',
        ),
    ]
