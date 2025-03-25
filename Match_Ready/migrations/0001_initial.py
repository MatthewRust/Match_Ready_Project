# Generated by Django 2.2.28 on 2025-03-25 18:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('team_id', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_date', models.DateTimeField()),
                ('team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_matches', to='Match_Ready.Team')),
                ('team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_matches', to='Match_Ready.Team')),
            ],
            options={
                'verbose_name_plural': 'Matches',
            },
        ),
        migrations.CreateModel(
            name='DefaultUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('defaultuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Match_Ready.DefaultUser')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='Match_Ready.Team')),
            ],
            bases=('Match_Ready.defaultuser',),
        ),
        migrations.CreateModel(
            name='Fan',
            fields=[
                ('defaultuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Match_Ready.DefaultUser')),
                ('favourite_team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fans', to='Match_Ready.Team')),
            ],
            bases=('Match_Ready.defaultuser',),
        ),
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('defaultuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Match_Ready.DefaultUser')),
                ('team', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='coach', to='Match_Ready.Team')),
            ],
            options={
                'verbose_name_plural': 'Coaches',
            },
            bases=('Match_Ready.defaultuser',),
        ),
    ]
