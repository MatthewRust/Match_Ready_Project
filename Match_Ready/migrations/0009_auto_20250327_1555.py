# Generated by Django 2.2.28 on 2025-03-27 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Match_Ready', '0008_match_attendies'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='attendies',
        ),
        migrations.AddField(
            model_name='match',
            name='attendies',
            field=models.IntegerField(default=0),
        ),
    ]
