# Generated by Django 5.1.7 on 2025-03-19 17:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=128, unique=True)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
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
                ('team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='home_matches', to='Match_Ready.team')),
                ('team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='away_matches', to='Match_Ready.team')),
            ],
        ),
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Match_Ready.user')),
                ('team', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='manager', to='Match_Ready.team')),
            ],
            bases=('Match_Ready.user',),
        ),
        migrations.CreateModel(
            name='Fan',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Match_Ready.user')),
                ('favourite_teams', models.ManyToManyField(related_name='fans', to='Match_Ready.team')),
            ],
            bases=('Match_Ready.user',),
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Match_Ready.user')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='Match_Ready.team')),
            ],
            bases=('Match_Ready.user',),
        ),
    ]
