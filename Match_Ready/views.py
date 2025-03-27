# Match_Ready/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, Http404, HttpResponseForbidden # Use more specific responses
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages # Use Django messages framework

from .models import Team, Match, Coach, Player, Fan, TeamSheet, PlayerAvailability, Announcement, DefaultUser # Added DefaultUser
from .forms import UserForm, NewTeamForm, AddMatchForm, FindTeamForm, AnnouncementForm, TeamSheetForm
from django.contrib.auth.models import User # Import User

# --- Basic Views ---
def index(request):
    # Maybe pass some upcoming matches or team count to the index page?
    context = {'upcoming_matches': Match.objects.filter(match_date__gte=timezone.now()).order_by('match_date')[:5]}
    return render(request, 'Match_Ready/index.html', context)

def about(request):
    return render(request, 'Match_Ready/about.html')

def contact(request):
    if request.method == 'POST':
        # Basic handling - just show a success message
        # In a real app, you'd send an email or save to DB
        email = request.POST.get('email')
        phone = request.POST.get('phone') # Optional field in template
        # print(f"Contact form submitted: Email={email}, Phone={phone}") # For debugging
        messages.success(request, "Thank you for contacting us!")
        return redirect('Match_Ready:contact') # Redirect to avoid resubmission
    return render(request, 'Match_Ready/contact.html')

# --- Authentication Views ---
def user_register(request):
    if request.user.is_authenticated:
        return redirect('Match_Ready:index') # Redirect logged-in users away

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False) # Don't save User model yet
            user.set_password(user_form.cleaned_data['password'])
            user.save() # Save User model

            # Create the corresponding DefaultUser profile first
            default_user_profile = DefaultUser.objects.create(user=user)

            # Now create the specific role profile based on form choice
            role = user_form.cleaned_data['role']
            if role == 'fan':
                Fan.objects.create(user=user) # Link directly to user
            elif role == 'coach':
                Coach.objects.create(user=user) # Link directly to user
            elif role == 'player':
                Player.objects.create(user=user) # Link directly to user

            # Authenticate and login the new user
            auth_user = authenticate(username=user.username, password=user_form.cleaned_data['password'])
            if auth_user:
                login(request, auth_user)
                messages.success(request, f"Welcome {user.username}! Registration successful.")
                return redirect('Match_Ready:index') # Redirect to index after successful signup/login
            else:
                # Should not happen if authenticate uses the correct credentials
                messages.error(request, "Registration successful, but automatic login failed. Please log in manually.")
                return redirect('Match_Ready:login')
        else:
             # Form is invalid, add error messages for display
             for field, errors in user_form.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}")
             # No need to return render here, fall through to render the form again below
    else:
        user_form = UserForm()

    return render(request, 'Match_Ready/signup.html', {'form': user_form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('Match_Ready:index') # Redirect logged-in users away

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password) # Use request object
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back {username}!")
                # Redirect to a specific page or the 'next' URL if provided
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('Match_Ready:index')
            else:
                messages.error(request, "This account is inactive.")
                return render(request, 'Match_Ready/login.html') # Show form again
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'Match_Ready/login.html') # Show form again
    else:
        # GET request, just show the login form
        return render(request, 'Match_Ready/login.html')


@login_required
def user_logout(request):
    username = request.user.username # Get username before logout
    logout(request)
    messages.info(request, f"You have been successfully logged out, {username}.")
    return redirect('Match_Ready:index')

# --- Match/Fixture Views ---
def UpcomingMatches(request):
    matches = Match.objects.filter(match_date__gte=timezone.now()).order_by('match_date')
    context = {
        'matches': matches,
        'are_matches': matches.exists() # Add boolean flag for template convenience
        }
    # The 'fixtures.html' template should be used here
    return render(request, 'Match_Ready/fixtures.html', context)

@login_required
def add_match(request):
    # Check if user is a coach using the context processor logic or direct check
    is_coach = hasattr(request.user, 'coach')
    if not is_coach:
        messages.error(request, "Only coaches can add matches.")
        return redirect('Match_Ready:index') # Or another appropriate page

    if request.method == 'POST':
        form = AddMatchForm(request.POST)
        if form.is_valid():
            match = form.save()
            messages.success(request, f"Match '{match}' added successfully.")
            return redirect('Match_Ready:UpcomingMatches') # Redirect to the fixtures list
        else:
             # Add form errors to messages
             for field, errors in form.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}")
    else:
        form = AddMatchForm()
    return render(request, 'Match_Ready/add_match.html', {'form': form})


# --- Team Management Views ---
@login_required
def my_team(request):
    team = None
    role = 'unknown'
    user_profile = None

    # Determine role and get associated team
    if hasattr(request.user, 'coach'):
        user_profile = request.user.coach
        team = user_profile.team
        role = 'coach'
    elif hasattr(request.user, 'player'):
        user_profile = request.user.player
        team = user_profile.team
        role = 'player'
    elif hasattr(request.user, 'fan'):
        user_profile = request.user.fan
        team = user_profile.favourite_team
        role = 'fan'
    # else: user might not have a role profile yet

    context = {
        'team': team,
        'role': role,
        'matches': [],
        'announcements': [],
        'team_sheets': []
    }

    if team:
        # Fetch details only if a team is associated
        context['matches'] = Match.objects.filter(
            Q(team1=team) | Q(team2=team),
            match_date__gte=timezone.now()
        ).order_by('match_date')
        context['announcements'] = Announcement.objects.filter(team=team).order_by('-date_posted')
        context['team_sheets'] = TeamSheet.objects.filter(team=team).select_related('match').order_by('-match__match_date')

    return render(request, 'Match_Ready/my_team.html', context)


@login_required
def create_team(request):
    # Only coaches can create teams
    if not hasattr(request.user, 'coach'):
        messages.error(request, "Only coaches can create teams.")
        return redirect('Match_Ready:index')

    coach_profile = request.user.coach
    # Prevent coach from creating a new team if they already manage one
    if coach_profile.team is not None:
         messages.warning(request, f"You already manage team '{coach_profile.team.name}'. You cannot create another.")
         return redirect('Match_Ready:my_team')

    if request.method == 'POST':
        form = NewTeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            # Assign the newly created team to the coach
            coach_profile.team = team
            coach_profile.save()
            messages.success(request, f"Team '{team.name}' created successfully! Team ID: {team.team_id}")
            return redirect('Match_Ready:my_team')
        else:
            for field, errors in form.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}")
    else:
        form = NewTeamForm()
    return render(request, 'Match_Ready/create_team.html', {'form': form})


@login_required
def find_team(request):
    # Coaches cannot join teams this way
    if hasattr(request.user, 'coach'):
        messages.error(request, "Coaches cannot join teams using this feature.")
        return redirect('Match_Ready:my_team')

    if request.method == 'POST':
        form = FindTeamForm(request.POST)
        if form.is_valid():
            team_uuid = form.cleaned_data['team_id']
            try:
                team_to_join = Team.objects.get(team_id=team_uuid)

                # Assign team based on user role (Player or Fan)
                if hasattr(request.user, 'player'):
                    player_profile = request.user.player
                    if player_profile.team == team_to_join:
                        messages.info(request, f"You are already a member of '{team_to_join.name}'.")
                    elif player_profile.team is not None:
                         messages.warning(request, f"You are already in team '{player_profile.team.name}'. Leave your current team first.")
                         # Add logic here to leave team if desired
                    else:
                        player_profile.team = team_to_join
                        player_profile.save()
                        messages.success(request, f"You have successfully joined team '{team_to_join.name}'!")
                    return redirect('Match_Ready:my_team')

                elif hasattr(request.user, 'fan'):
                    fan_profile = request.user.fan
                    if fan_profile.favourite_team == team_to_join:
                         messages.info(request, f"'{team_to_join.name}' is already your favourite team.")
                    else:
                        fan_profile.favourite_team = team_to_join
                        fan_profile.save()
                        messages.success(request, f"'{team_to_join.name}' is now your favourite team!")
                    return redirect('Match_Ready:my_team')

                else:
                    # User has no Player/Fan profile - should not happen if registration is correct
                    messages.error(request, "Your user profile is incomplete. Cannot join team.")
                    return redirect('Match_Ready:index')

            except Team.DoesNotExist:
                messages.error(request, "Invalid Team ID. Please check and try again.")
                # Render the form again with the error
                return render(request, 'Match_Ready/find_team.html', {'form': form})
        else:
            # Form validation failed (e.g., not a valid UUID)
            for field, errors in form.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}")
            # Render the form again
            return render(request, 'Match_Ready/find_team.html', {'form': form})

    else: # GET request
        form = FindTeamForm()
    return render(request, 'Match_Ready/find_team.html', {'form': form})


# --- Announcement Views ---
@login_required
def announcements(request, team_id):
    # Anyone associated or interested might view announcements
    team = get_object_or_404(Team, id=team_id)
    # Check if the current user has *some* relation to this team (optional, for authorization)
    # user_can_view = (hasattr(request.user, 'coach') and request.user.coach.team == team) or \
    #                 (hasattr(request.user, 'player') and request.user.player.team == team) or \
    #                 (hasattr(request.user, 'fan') and request.user.fan.favourite_team == team)
    # if not user_can_view:
    #     messages.error(request, "You do not have permission to view these announcements.")
    #     return redirect('Match_Ready:index')

    team_announcements = Announcement.objects.filter(team=team).order_by('-date_posted')
    context = {
        'team': team,
        'announcements': team_announcements
    }
    return render(request, 'Match_Ready/announcements.html', context)

@login_required
def create_announcement(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Authorization: Only the coach of *this* team can create announcements
    if not hasattr(request.user, 'coach') or request.user.coach.team != team:
        messages.error(request, "Only the coach of this team can post announcements.")
        # Redirect to team page or announcements list instead of forbidden
        return redirect('Match_Ready:announcements', team_id=team.id)

    coach_profile = request.user.coach

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.team = team
            announcement.coach = coach_profile # Link to the coach profile
            announcement.save()
            messages.success(request, f"Announcement '{announcement.title}' posted successfully.")
            return redirect('Match_Ready:announcements', team_id=team.id)
        else:
            for field, errors in form.errors.items():
                 for error in errors:
                     messages.error(request, f"{field}: {error}")
    else:
        form = AnnouncementForm()

    context = {
        'form': form,
        'team': team
    }
    return render(request, 'Match_Ready/create_announcement.html', context)


# --- Team Sheet Views ---
@login_required
def team_sheets(request, team_id):
    # View list of team sheets for a specific team
    team = get_object_or_404(Team, id=team_id)
    # Add authorization check if needed (similar to announcements)

    team_sheets_list = TeamSheet.objects.filter(team=team).select_related('match').order_by('-match__match_date')
    context = {
        'team': team,
        'team_sheets': team_sheets_list
    }
    # Ensure the template name matches: 'team_sheets.html'
    return render(request, 'Match_Ready/team_sheets.html', context)

@login_required
def create_team_sheet(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    # Authorization: Only the coach of *this* team can create team sheets
    if not hasattr(request.user, 'coach') or request.user.coach.team != team:
        messages.error(request, "Only the coach of this team can create team sheets.")
        return redirect('Match_Ready:team_sheets', team_id=team.id)

    coach_profile = request.user.coach

    if request.method == 'POST':
        # Pass the team object to the form's __init__
        form = TeamSheetForm(team, request.POST)
        if form.is_valid():
            match = form.cleaned_data['match']
            available_players_qs = form.cleaned_data['available_players'] # This is a QuerySet

            # Check if a sheet for this match and team already exists
            existing_sheet = TeamSheet.objects.filter(match=match, team=team).first()
            if existing_sheet:
                messages.warning(request, f"A team sheet for this match ({match}) already exists. You can edit it instead.")
                 # Redirect to an edit view or the detail view
                return redirect('Match_Ready:team_sheet_detail', team_sheet_id=existing_sheet.id)

            # Create the TeamSheet instance
            team_sheet = TeamSheet.objects.create(match=match, team=team)

            # Get all players belonging to the team
            all_team_players = Player.objects.filter(team=team)

            # Create PlayerAvailability entries for all players in the team
            availabilities_to_create = []
            for player in all_team_players:
                is_available = player in available_players_qs # Check if player is in the selected list
                availabilities_to_create.append(
                    PlayerAvailability(
                        team_sheet=team_sheet,
                        player=player,
                        available=is_available
                    )
                )
            # Bulk create for efficiency
            PlayerAvailability.objects.bulk_create(availabilities_to_create)

            messages.success(request, f"Team sheet created successfully for match: {match}")
            return redirect('Match_Ready:team_sheets', team_id=team.id)
        else:
            # Form is invalid
            for field, errors in form.errors.items():
                 for error in errors:
                     # Specific handling for available_players if needed
                     if field == 'available_players':
                         messages.error(request, f"Error selecting players: {error}")
                     else:
                        messages.error(request, f"{field}: {error}")
    else: # GET request
        # Pass the team object to the form's __init__
        form = TeamSheetForm(team)

    context = {
        'form': form,
        'team': team
    }
    return render(request, 'Match_Ready/create_team_sheet.html', context)

@login_required
def team_sheet_detail(request, team_sheet_id):
    # View details of a specific team sheet
    team_sheet = get_object_or_404(TeamSheet.objects.select_related('team', 'match'), id=team_sheet_id)
    # Add authorization check if needed

    # Get player availabilities for this specific sheet
    availabilities = PlayerAvailability.objects.filter(team_sheet=team_sheet).select_related('player__user').order_by('player__user__username')

    context = {
        'team_sheet': team_sheet,
        'availabilities': availabilities
    }
    return render(request, 'Match_Ready/team_sheet_detail.html', context)