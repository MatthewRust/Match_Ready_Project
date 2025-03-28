import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Match_Ready_Project.settings')

import django
django.setup()
from django.contrib.auth.models import User
# Import specific role models directly if needed, or access via user object
from Match_Ready.models import Team, DefaultUser, Coach, Player, Fan, Match
from django.utils import timezone
from django.db import IntegrityError # Import IntegrityError

import sys


def create_teams():
    print("--- Creating/Checking Teams ---")
    teams_data = [
        {"name": "Team A", "team_id": "team_a"},
        {"name": "Team B", "team_id": "team_b"},
        {"name": "Team C", "team_id": "team_c"},
        {"name": "Team D", "team_id": "team_d"},
    ]

    created_teams = {}

    for team_data in teams_data:
        team, created = Team.objects.get_or_create(
            team_id=team_data["team_id"],
            defaults={"name": team_data["name"]}
        )

        if created:
            print(f"Created team: {team.name} ({team.team_id})")
        else:
            print(f"Team already exists: {team.name} ({team.team_id})")

        created_teams[team.team_id] = team

    return created_teams


def create_users(created_teams):
    print("\n--- Creating/Checking Users ---")
    default_password = "password123"

    for team_id, team in created_teams.items():
        print(f"\nProcessing users for {team.name} ({team.team_id})...")

        coach_username = f"{team.team_id}_coach"
        coach_user = None
        try:
            coach_user, user_created = User.objects.get_or_create(username=coach_username)
            if user_created:
                coach_user.set_password(default_password)
                coach_user.save()
                coach = Coach.objects.create(user = coach_user)
                coach.team = team
                coach.save()
                print(f"  Created User: {coach_username}")
            else:
                print(f"  User already exists: {coach_username}")

        except Exception as e: # Catch other potential errors
            print(f"  Unexpected error processing coach {coach_username}: {e}")


        # --- Players ---
        for i in range(12):
            player_username = f"{team.team_id}_player{i+1}"
            player_user = None
            try:
                player_user, user_created = User.objects.get_or_create(username=player_username)
                if user_created:
                    player_user.set_password(default_password)
                    player_user.save()
                    player = Player.objects.create(user = player_user)
                    player.team = team
                    player.save()
                    print(f"  Created User: {player_username}")
                else:
                    print(f"  User already exists: {player_username}")

            except Exception as e: # Catch other potential errors
                print(f"  Unexpected error processing coach {player_username}: {e}")


        # --- Fans ---
        for i in range(5):
            fan_username = f"{team.team_id}_fan{i+1}"
            fan_user = None
            try:
                fan_user, user_created = User.objects.get_or_create(username=fan_username)
                if user_created:
                    fan_user.set_password(default_password)
                    fan_user.save()
                    fan = Fan.objects.create(user = fan_user)
                    fan.team = team
                    fan.save()
                    print(f"  Created User: {fan_username}")
                else:
                    print(f"  User already exists: {fan_username}")

            except Exception as e: # Catch other potential errors
                print(f"  Unexpected error processing coach {fan_username}: {e}")


def create_matches(created_teams):
    print("\n--- Creating/Checking Matches ---")

    matches_to_create = []
    team_ids = list(created_teams.keys())
    current_date = timezone.now()

    for i in range(0, len(team_ids), 2):
        if i + 1 < len(team_ids):
            team1_id = team_ids[i]
            team2_id = team_ids[i+1]

            team1 = created_teams[team1_id]
            team2 = created_teams[team2_id]

            match_date = current_date + timezone.timedelta(days=i*3 + 7) # Spread out dates more

            match, created = Match.objects.get_or_create(
                team1=team1,
                team2=team2,
                match_date=match_date,
            )
            if created:
                print(f"  Created Match: {match}")
            else:
                print(f"  Match already exists: {match}")
        else:
            print(f"  Skipping match creation for {created_teams[team_ids[i]].name} - odd number of teams.")


def populate():
    print('Starting population script...')
    teams = create_teams()
    create_users(teams)
    create_matches(teams)
    print('\nPopulation script finished.')

if __name__ == '__main__':
    populate()