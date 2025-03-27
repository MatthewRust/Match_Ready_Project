from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse # Added JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.views.decorators.http import require_POST # Added require_POST

#create team, create match, find team, tests, ajax, javascript

from Match_Ready.models import Fan, Player,Coach, Match, Team #Team sheets, announcements

from Match_Ready.forms import UserForm, FindTeamForm, NewTeamForm, AddMatch

# --- Existing Views ---

def index (request):
    if request.user.is_authenticated:
        user_name = request.user.username
    else:
        user_name = "Guest"
    context_dic = {}
    context_dic['name'] = user_name
    return render(request, 'Match_Ready/index.html', context=context_dic)


def about (request):
    return render(request, 'Match_Ready/about.html')

def contact(request):
    superusers = User.objects.filter(is_superuser=True)
    return render(request,'Match_Ready/contact.html', context={'superusers':superusers})


def add_match(request):
    context = {}
    if request.method == "POST":
        team1_id = request.POST.get("team1")
        team2_id = request.POST.get("team2")
        date_str = request.POST.get("match_date")

        errors = {}
        team1 = None
        team2 = None

        # Validate Team 1
        if not team1_id:
             errors['teams'] = "Team 1 ID is required."
        else:
            try:
                team1 = Team.objects.get(team_id=team1_id.strip())
            except Team.DoesNotExist:
                errors['teams'] = f"Team with ID '{team1_id}' does not exist."
            except ValueError:
                 errors['teams'] = "Invalid format for Team 1 ID."

        # Validate Team 2 (only if Team 1 was valid or ID was provided)
        if team1_id and not errors.get('teams'): # Check team1 ID was provided and no error yet
            if not team2_id:
                errors.setdefault('teams', '') # Initialize if not set
                errors['teams'] += " Team 2 ID is required."
            else:
                try:
                    team2 = Team.objects.get(team_id=team2_id.strip())
                    if team1 and team1 == team2: # Check if teams are the same
                         errors.setdefault('teams', '')
                         errors['teams'] += " A team cannot play against itself."
                except Team.DoesNotExist:
                     errors.setdefault('teams', '')
                     errors['teams'] += f" Team with ID '{team2_id}' does not exist."
                except ValueError:
                     errors.setdefault('teams', '')
                     errors['teams'] += " Invalid format for Team 2 ID."

        # Validate Date
        if not date_str:
            errors['date'] = "Date is required."
        # Optional: Add validation for date format if needed (though datetime-local helps)

        if errors:
            context['errors'] = errors
            # Add form data back to context to repopulate form on error
            context['form_data'] = request.POST
        else:
            # Create the match only if both teams were found and are different
            if team1 and team2 and team1 != team2:
                Match.objects.create(
                    team1=team1,
                    team2=team2,
                    match_date=date_str
                )
                messages.success(request, "Match added successfully!")
                return redirect("Match_Ready:index") # Or redirect to fixtures page
            else:
                # This case should ideally be caught by the validation above, but as a fallback:
                 if not errors: # If no specific error was set, add a generic one
                      context['errors'] = {'teams': 'Could not create match due to team issues.'}

    return render(request, 'Match_Ready/add_match.html', context)


def user_register(request):
    registered = False

    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']

            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose another.")
                # Pass the form back to the template to show errors and retain data
                return render(request, 'Match_Ready/signup.html', {'form': form, 'registered': registered})
            else:
                user = User.objects.create_user(username=username, password=password)

                if role == 'fan':
                    Fan.objects.create(user=user)
                elif role == 'coach':
                    Coach.objects.create(user=user)
                elif role == 'player':
                    Player.objects.create(user=user)

                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user:
                    login(request, authenticated_user)
                    messages.success(request, f"Welcome, {username}! Registration successful.")
                    return redirect('Match_Ready:index')

                registered = True # Should technically not be reached if login is successful
        else:
            # Form is not valid, print errors to console and re-render form
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserForm()

    return render(request, 'Match_Ready/signup.html', {'form': form, 'registered': registered})

def user_login(request):
    if request.user.is_authenticated:
         messages.info(request, "You are already logged in.")
         return redirect('Match_Ready:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
             messages.error(request, "Both username and password are required.")
             return render(request, 'Match_Ready/login.html') # Re-render with error

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            # Redirect to the page the user was trying to access, or index
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect(reverse('Match_Ready:index'))
        else:
            messages.error(request, "Invalid username or password.")
            # Don't redirect here, re-render the login page with the error
            return render(request, 'Match_Ready/login.html')

    # For GET requests
    return render(request, 'Match_Ready/login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect(reverse('Match_Ready:index'))

def fixtures(request):
    # Get all upcoming matches
    all_upcoming_matches = Match.objects.filter(match_date__gte=timezone.now()).order_by('match_date')[:25] # Limit display

    # Check if user is logged in and has a team to compare against their matches
    user_team = None
    user_attending_match_ids = set()
    if request.user.is_authenticated:
        role = find_default_user(request, request.user)
        if role and hasattr(role, 'team') and role.team:
            user_team = role.team
        # Get IDs of matches the user is attending
        user_attending_match_ids = set(request.user.match_set.filter(match_date__gte=timezone.now()).values_list('id', flat=True))


    context_dict = {
        'upcoming_matches': all_upcoming_matches,
        'user_team': user_team,
        'user_attending_match_ids': user_attending_match_ids,
        }
    return render(request,'Match_Ready/fixtures.html',context=context_dict)


@login_required
def my_team(request):
    user = request.user
    # No need for if user is None check because of @login_required
    role = find_default_user(request, user)
    if role is None:
        # This shouldn't happen for a logged-in user if signup creates roles correctly
        messages.error(request, "User role not found. Please contact support.")
        return redirect('Match_Ready:index')

    if not hasattr(role, 'team') or role.team is None:
        messages.info(request, "You need to join or create a team first.")
        return redirect('Match_Ready:find_team')

    team_name = role.team.name
    context_dict = {'team_name': team_name, 'team': role.team} # Pass the team object too
    return render(request,'Match_Ready/my_team.html',context=context_dict)


@login_required
def find_team(request):
    user = request.user
    role = find_default_user(request,user)

    if role is None:
        messages.error(request, "User role not found. Please contact support.")
        return redirect(reverse('Match_Ready:index'))

    form = FindTeamForm(request.POST or None) # Initialize with POST data or empty

    if request.method=='POST':
        if form.is_valid():
            team_id = form.cleaned_data.get('team_id')
            try:
                team = Team.objects.get(team_id=team_id.strip())
                # Check if the role allows joining a team (e.g., Player or Fan)
                if isinstance(role, (Player, Fan)):
                    # Check if user is already in a team
                    if role.team and role.team != team:
                         # Optional: Ask for confirmation before switching
                         # For now, just switch
                         old_team_name = role.team.name
                         role.team = team
                         role.save()
                         messages.success(request, f"You have switched from {old_team_name} to {team.name}.")
                    elif not role.team:
                         role.team = team
                         role.save()
                         messages.success(request, f"You have successfully joined {team.name}.")
                    else: # User is trying to join the team they are already in
                         messages.info(request, f"You are already a member of {team.name}.")

                    return redirect(reverse('Match_Ready:my_team'))

                elif isinstance(role, Coach):
                    # Decide coach logic: Can a coach join a team this way?
                    # Maybe only if they don't already manage one?
                    if not role.team:
                        role.team = team
                        role.save()
                        messages.success(request, f"You are now associated with {team.name}.")
                        return redirect(reverse('Match_Ready:my_team'))
                    else:
                        messages.error(request, f"As a coach, you already manage {role.team.name}. You might need to leave it first or use a different mechanism.")

                else:
                     messages.error(request, "Your user role cannot join teams this way.")

            except Team.DoesNotExist:
                messages.error(request, f"No team found with ID '{team_id}'.")
                # No redirect here, show the error on the same page
        else:
            # Form is invalid (though FindTeamForm is simple, good practice)
            messages.error(request, "Invalid input.")


    context_dict = {'form':form,'user':user, 'role': role}
    return render(request,'Match_Ready/find_team.html',context=context_dict)

@login_required
def create_team(request):
    context_dict = {}
    role = find_default_user(request, request.user)

    # Check if user is a Coach
    if not isinstance(role, Coach):
        messages.error(request, "Only coaches can create new teams.")
        return redirect('Match_Ready:index')

    # Check if the coach already manages a team
    if hasattr(role, 'team') and role.team is not None:
        messages.warning(request, f"You already manage team '{role.team.name}'. You cannot create another.")
        return redirect('Match_Ready:my_team') # Redirect to their current team page

    if request.method == "POST":
        team_name = request.POST.get("team_name", "").strip()
        team_ID = request.POST.get("team_ID", "").strip() # gets the team_id and name

        errors = {}

        if not team_name:
            errors['team_name'] = "Team name is required."
        if not team_ID:
            errors['team_ID'] = "A unique Team ID is required."
        elif Team.objects.filter(team_id=team_ID).exists():
            errors['team_ID'] = "This Team ID is already taken. Please choose another."
        # Basic validation: Check if team_ID contains spaces or special chars you want to avoid
        elif not team_ID.isalnum(): # Example: Only allow alphanumeric
             errors['team_ID'] = "Team ID can only contain letters and numbers."

        if errors:
            context_dict['errors'] = errors
            context_dict['form_data'] = request.POST # Repopulate form
        else:
            try:
                new_team = Team.objects.create(name=team_name, team_id = team_ID)
                # Assign this coach to the newly created team
                role.team = new_team
                role.save()
                messages.success(request, f"Team '{team_name}' created successfully! You are now managing it.")
                return redirect("Match_Ready:my_team") # Redirect to the new team's page
            except Exception as e:
                 # Catch potential database errors during creation
                 messages.error(request, f"An error occurred while creating the team: {e}")
                 context_dict['errors'] = {'general': 'Could not create team.'}
                 context_dict['form_data'] = request.POST


    return render(request,'Match_Ready/create_team.html',context=context_dict)


@login_required
def player_list(request):
    user = request.user
    role = find_default_user(request,user)

    if role is None or not hasattr(role, 'team') or role.team is None:
        messages.warning(request, "You need to be part of a team to view its members.")
        return redirect('Match_Ready:find_team')

    team = role.team
    # Get players, coach, and fans associated with the team
    list_of_players = Player.objects.filter(team=team)
    team_coach = Coach.objects.filter(team=team).first() # Use first() as team is OneToOne for coach
    list_of_fans = Fan.objects.filter(team=team)

    context_dict = {
        'list_of_players': list_of_players,
        'team_coach': team_coach,
        'list_of_fans': list_of_fans,
        'team': team
        }

    return render(request,'Match_Ready/list_of_players.html',context=context_dict)


@login_required
def upcoming_matches(request):
    user = request.user
    role = find_default_user(request, user)

    if role is None or not hasattr(role, 'team') or role.team is None:
        messages.warning(request, "You need to be part of a team to view its upcoming matches.")
        return redirect('Match_Ready:find_team')

    now = timezone.now()
    user_team = role.team

    home_matches = Match.objects.filter(team1=user_team, match_date__gte=now).order_by('match_date')[:10]
    away_matches = Match.objects.filter(team2=user_team, match_date__gte=now).order_by('match_date')[:10]

    # Get IDs of matches the user is attending
    user_attending_match_ids = set(user.match_set.filter(
        models.Q(team1=user_team) | models.Q(team2=user_team), # Filter for user's team matches
        match_date__gte=now
        ).values_list('id', flat=True))

    context_dict={
        'home_matches': home_matches,
        'away_matches': away_matches,
        'team': user_team,
        'user_attending_match_ids': user_attending_match_ids
        }
    # Ensure the correct template name is used
    return render(request,'Match_Ready/upcoming_matches.html', context=context_dict)

# --- AJAX View ---
@login_required # Ensure user is logged in
@require_POST   # Ensure this view only accepts POST requests
def attend_match_ajax(request):
    match_id = request.POST.get('match_id')
    user = request.user

    if not match_id:
        return JsonResponse({'status': 'error', 'message': 'Missing match ID'}, status=400)

    try:
        # Ensure the match ID is an integer before querying
        match = Match.objects.get(id=int(match_id))
    except Match.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Match not found'}, status=404)
    except (ValueError, TypeError): # Handle non-integer or non-numeric IDs
         return JsonResponse({'status': 'error', 'message': 'Invalid match ID format'}, status=400)

    # Check if user is already attending
    if user in match.attendees_list.all():
         return JsonResponse({
             'status': 'error',
             'message': 'You are already marked as attending.',
             'already_attending': True # Flag for JS
             }, status=400) # Bad Request - already done

    # Add the attendee using the model method
    try:
        match.add_attendee(user)
        return JsonResponse({
            'status': 'success',
            'message': 'You are now attending!',
            'new_count': match.attendees # Send back the updated count
        })
    except Exception as e:
        # Log the exception for debugging
        print(f"Error adding attendee: {e}")
        return JsonResponse({'status': 'error', 'message': 'An internal error occurred.'}, status=500)


# --- Helper Function ---
def find_default_user(request, user):
    """ Finds the role (Player, Coach, Fan) associated with a User """
    # Use related names if available, otherwise filter directly
    if hasattr(user, 'player'):
        return user.player
    if hasattr(user, 'coach'):
        return user.coach
    if hasattr(user, 'fan'):
        return user.fan

    # Fallback if related names aren't set up or used consistently
    user_role = Player.objects.filter(user=user).first() or \
                Coach.objects.filter(user=user).first() or \
                Fan.objects.filter(user=user).first()
    return user_role

# --- Deprecated/Placeholder Views (Review if needed) ---
def make_team(request):
    # This view seems duplicative of create_team and might not be used.
    # If it's meant for something else, clarify its purpose.
    # If not needed, consider removing it.
    role = find_default_user(request, request.user)
    if not isinstance(role, Coach):
        messages.error(request, "Only coaches can perform this action.")
        return redirect('Match_Ready:index')
    # Assuming this was a placeholder:
    messages.info(request, "'Make Team' view needs implementation or removal.")
    # Original had render('Match_Ready/make_team.html') but path might be wrong
    return render(request, 'Match_Ready/make_team.html') # Ensure this template exists