import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Match_Ready_Project.settings')

import django
django.setup()
from django.contrib.auth.models import User
from Match_Ready.models import Team, DefaultUser, Coach, Player, Fan, Match

from django.utils import timezone


import sys

django.setup()

def create_teams():

    teams = [
        {"name": "Team A", "team_id": "team_a"},
        {"name": "Team B", "team_id": "team_b"},
        {"name": "Team C", "team_id": "team_c"},
        {"name": "Team D", "team_id": "team_d"},
    ]

    created_teams = {}

    for team_data in teams:
        team, created = Team.objects.get_or_create(team_id=team_data["team_id"], 
                                                   defaults={"name": team_data["name"]})

        if created:
            print(f"Created team: {team}")
        else:
            print(f"Team already exists: {team}")

        created_teams[team.team_id] = team

    return created_teams


def create_users(created_teams):
    users = []

    for team_id, team in created_teams.items():

        print(f"Creating users for {team.name} ({team.team_id})")

        coach_user = User.objects.create_user(username=f"{team.team_id}_coach", password="password123")
        coach = Coach(user=coach_user, team=team)
        users.append(coach)

        for i in range(12):  
            player_user = User.objects.create_user(username=f"{team.team_id}_player{i+1}", password="password123")
            player = Player(user=player_user, team=team)
            users.append(player)

        for i in range(5):  
            fan_user = User.objects.create_user(username=f"{team.team_id}_fan{i+1}", password="password123")
            fan = Fan(user=fan_user, team=team)
            users.append(fan)

    for user in users:
        user.save()

def create_matches(created_teams):

    matches = []
    team_ids = list(created_teams.keys())
    current_date = timezone.now()

    for i in range(0, len(team_ids), 2):

        team1_id = team_ids[i]
        if i+1 < len(team_ids):
            team2_id = team_ids[i+1]
        else:
            team2_id = team_ids[0]

        team1 = created_teams[team1_id]
        team2 = created_teams[team2_id]

        match_date = current_date + timezone.timedelta(days=i)

        match = Match(team1=team1, team2=team2, match_date=match_date)
        matches.append(match)

    for match in matches:
        match.save()

def populate():
    teams = create_teams()
    create_users(teams)
    create_matches(teams)

if __name__ == '__main__':
    print('Starting poulation now...')
    populate()
