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

# django.setup() # No need to call setup twice

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

        # --- Coach ---
        coach_username = f"{team.team_id}_coach"
        coach_user = None
        try:
            # Try to get or create the User
            coach_user, user_created = User.objects.get_or_create(username=coach_username)
            if user_created:
                coach_user.set_password(default_password)
                coach_user.save()
                print(f"  Created User: {coach_username}")
            else:
                print(f"  User already exists: {coach_username}")

            # Get or create the Coach role associated with the user
            coach_profile, coach_created = Coach.objects.get_or_create(
                user=coach_user,
                defaults={'team': team} # Assign team only if creating coach profile
            )
            if coach_created:
                 print(f"    Created Coach profile for {coach_username}")
                 # If user existed but profile didn't, ensure team is set
                 if coach_profile.team != team:
                     coach_profile.team = team
                     coach_profile.save()
                     print(f"    Associated Coach {coach_username} with {team.name}")
            else:
                 print(f"    Coach profile already exists for {coach_username}")
                 # Optional: ensure coach is still linked to the correct team if script logic changes
                 if coach_profile.team != team:
                     print(f"    WARNING: Coach {coach_username} currently linked to {coach_profile.team}, not updating to {team.name} in this script.")
                     # Or uncomment to force update:
                     # coach_profile.team = team
                     # coach_profile.save()
                     # print(f"    Re-associated Coach {coach_username} with {team.name}")


        except IntegrityError as e:
            print(f"  Error processing coach {coach_username}: {e}")
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
                    print(f"  Created User: {player_username}")
                # else: # Optional: Print if user existed
                #     print(f"  User already exists: {player_username}")

                # Get or create the Player role
                player_profile, player_created = Player.objects.get_or_create(
                    user=player_user,
                    defaults={'team': team}
                )
                # Optional: print if profile created/existed

            except IntegrityError as e:
                print(f"  Error processing player {player_username}: {e}")
            except Exception as e:
                print(f"  Unexpected error processing player {player_username}: {e}")


        # --- Fans ---
        for i in range(5):
            fan_username = f"{team.team_id}_fan{i+1}"
            fan_user = None
            try:
                fan_user, user_created = User.objects.get_or_create(username=fan_username)
                if user_created:
                    fan_user.set_password(default_password)
                    fan_user.save()
                    print(f"  Created User: {fan_username}")
                # else: # Optional: Print if user existed
                #     print(f"  User already exists: {fan_username}")

                # Get or create the Fan role
                fan_profile, fan_created = Fan.objects.get_or_create(
                    user=fan_user,
                    defaults={'team': team}
                )
                # Optional: print if profile created/existed

            except IntegrityError as e:
                 print(f"  Error processing fan {fan_username}: {e}")
            except Exception as e:
                print(f"  Unexpected error processing fan {fan_username}: {e}")


def create_matches(created_teams):
    print("\n--- Creating/Checking Matches ---")
    # Clear existing matches to avoid duplicates if needed (Use with caution!)
    # Match.objects.all().delete()
    # print("  Cleared existing matches.")

    matches_to_create = []
    team_ids = list(created_teams.keys())
    current_date = timezone.now()

    # Create pairings (simple example: T1 vs T2, T3 vs T4)
    for i in range(0, len(team_ids), 2):
        if i + 1 < len(team_ids): # Ensure there's a pair
            team1_id = team_ids[i]
            team2_id = team_ids[i+1]

            team1 = created_teams[team1_id]
            team2 = created_teams[team2_id]

            # Make match date unique enough to check with get_or_create if desired
            # Using timedelta based on index 'i'
            match_date = current_date + timezone.timedelta(days=i*3 + 7) # Spread out dates more

            # Use get_or_create for matches to avoid duplicates if script is rerun
            match, created = Match.objects.get_or_create(
                team1=team1,
                team2=team2,
                match_date=match_date,
                # Add defaults if needed, e.g., defaults={'location': 'Default Venue'}
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