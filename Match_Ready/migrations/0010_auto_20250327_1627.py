# Generated by Django 2.2.28 on 2025-03-27 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Match_Ready', '0009_auto_20250327_1555'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='attendies',
            new_name='attendees',
        ),
    ]
