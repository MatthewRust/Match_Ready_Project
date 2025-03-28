from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q


from Match_Ready.models import Fan, Player,Coach, Match, Team

from Match_Ready.forms import UserForm, FindTeamForm, NewTeamForm, AddMatch

# view for index page, adds username of user to context dict
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

# view for contact page, adds all superusers to context dict
def contact(request):
    superusers = User.objects.filter(is_superuser=True)
    return render(request,'Match_Ready/contact.html', context={'superusers':superusers})

# view for adding match to database
def add_match(request):
    context = {}
    if request.method == "POST":

        # input fields, team_1 correlates to a home team, team 2 is away team
        team1_id = request.POST.get("team1")
        team2_id = request.POST.get("team2")
        date_str = request.POST.get("match_date")

        errors = {}
        team1 = None
        team2 = None

        #error checking for team 1
        if not team1_id:
             errors['teams'] = "Team 1 ID is required."
        else:
            try:
                team1 = Team.objects.get(team_id=team1_id.strip())
            except Team.DoesNotExist:
                errors['teams'] = f"Team with ID '{team1_id}' does not exist."
            except ValueError:
                 errors['teams'] = "Invalid format for Team 1 ID."

        #error checking for team 2
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

        #error checking for date
        if not date_str:
            errors['date'] = "Date is required."

        if errors:
            context['errors'] = errors
            context['form_data'] = request.POST
        else:
            #check both teams are different teams
            if team1 and team2 and team1 != team2:
                Match.objects.create(
                    team1=team1,
                    team2=team2,
                    match_date=date_str
                )
                messages.success(request, "Match added successfully!")
                return redirect("Match_Ready:index")
            
    return render(request, 'Match_Ready/add_match.html', context)


def user_register(request):
    registered = False

    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            #.cleaned data used as role is not a field of user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']

            # error check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose another.")
                return render(request, 'Match_Ready/signup.html', {'form': form, 'registered': registered})
            else:
                user = User.objects.create_user(username=username, password=password)
                #create fan. coach or player corresponding to radio button click
                if role == 'fan':
                    Fan.objects.create(user=user)
                elif role == 'coach':
                    Coach.objects.create(user=user)
                elif role == 'player':
                    Player.objects.create(user=user)

                # log user in if their sign up is successful
                authenticated_user = authenticate(username=username, password=password)
                if authenticated_user:
                    login(request, authenticated_user)
                    messages.success(request, f"Welcome, {username}! Registration successful.")
                    return redirect('Match_Ready:index')
        else:
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
            return redirect(reverse('Match_Ready:index'))
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'Match_Ready/login.html')

    # this is called initially when request is GET
    return render(request, 'Match_Ready/login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect(reverse('Match_Ready:index'))

def fixtures(request):
    #retrieves next 25 or less match objects and adds to context dict
    upcoming_matches = Match.objects.filter(match_date__gte=timezone.now()).order_by('match_date')[:25]
    context_dict = {'upcoming_matches': upcoming_matches}
    return render(request,'Match_Ready/fixtures.html',context=context_dict)


@login_required
def my_team(request):
    # finds the team the user is in and passes to context dict
    user = request.user
    role = find_default_user(request, user)
    if role is None:
        messages.error(request, "Logged in as something other than a Coach, Player or Fan, try again.")
        return redirect('Match_Ready:login')

    if not hasattr(role, 'team') or role.team is None:
        messages.info(request, "You need to join or create a team first.")
        return redirect('Match_Ready:find_team')

    team_name = role.team.name
    context_dict = {'team_name': team_name, 'team': role.team} 
    return render(request,'Match_Ready/my_team.html',context=context_dict)

#gives a user a team if they dont have one or swaps their team with a new one
@login_required
def find_team(request):
    user = request.user
    role = find_default_user(request,user)

    if role is None:
        messages.error(request, "User role not found. Please contact support.")
        return redirect(reverse('Match_Ready:index'))

    form = FindTeamForm(request.POST or None) 

    if request.method=='POST':
        if form.is_valid():
            #gets new team id
            team_id = form.cleaned_data.get('team_id')
            try:
                team = Team.objects.get(team_id=team_id.strip())
                #coaches can't switch team
                if isinstance(role, (Player, Fan)):
                    #swap team
                    if role.team and role.team != team:
                         old_team_name = role.team.name
                         role.team = team
                         role.save()
                         messages.success(request, f"You have switched from {old_team_name} to {team.name}.")
                    #give user their first team
                    elif not role.team:
                         role.team = team
                         role.save()
                         messages.success(request, f"You have successfully joined {team.name}.")
                    else: 
                         messages.info(request, f"You are already a member of {team.name}.")

                    return redirect(reverse('Match_Ready:my_team'))

                elif isinstance(role, Coach):
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
        else:
            messages.error(request, "Invalid input.")


    context_dict = {'form':form,'user':user, 'role': role}
    return render(request,'Match_Ready/find_team.html',context=context_dict)

@login_required
def create_team(request):
    context_dict = {}
    role = find_default_user(request, request.user)

    # if user is a Coach they can make a team
    if not isinstance(role, Coach):
        messages.error(request, "Only coaches can create new teams.")
        return redirect('Match_Ready:index')

    # if the coach already manage a team they cant make a new one
    if hasattr(role, 'team') and role.team is not None:
        messages.warning(request, f"You already manage team '{role.team.name}'. You cannot create another.")
        return redirect('Match_Ready:my_team')

    if request.method == "POST":
        team_name = request.POST.get("team_name", "").strip()
        team_ID = request.POST.get("team_ID", "").strip() 

        errors = {}

        #error checks
        if not team_name:
            errors['team_name'] = "Team name is required."
        if not team_ID:
            errors['team_ID'] = "A unique Team ID is required."
        elif Team.objects.filter(team_id=team_ID).exists():
            errors['team_ID'] = "This Team ID is already taken. Please choose another."
        
        if errors:
            #returning all errors
            context_dict['errors'] = errors
            context_dict['form_data'] = request.POST 
            return render(request, 'Match_Ready/create_team.html', context=context_dict)
        else:
            #make the new team
            new_team = Team.objects.create(name=team_name, team_id = team_ID)
            role.team = new_team
            role.save()
            messages.success(request, f"Team '{team_name}' created successfully! You are now managing it.")
            return redirect("Match_Ready:my_team") 

    return render(request,'Match_Ready/create_team.html',context=context_dict)


@login_required
def player_list(request):
    user = request.user
    role = find_default_user(request,user)

    if role is None or not hasattr(role, 'team') or role.team is None:
        messages.warning(request, "You need to be part of a team to view its members.")
        return redirect('Match_Ready:find_team')

    team = role.team
    #get all the member of the team
    list_of_players = Player.objects.filter(team=team)
    team_coach = Coach.objects.filter(team=team).first()
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
    #find matches in the users team is playing
    home_matches = Match.objects.filter(team1=user_team, match_date__gte=now).order_by('match_date')[:10]
    away_matches = Match.objects.filter(team2=user_team, match_date__gte=now).order_by('match_date')[:10]

    context_dict={
        'home_matches': home_matches,
        'away_matches': away_matches
        }
    return render(request,'Match_Ready/upcoming_matches.html', context=context_dict)

#helper function to find the Coach, Player, Fan object associated with a certain user
def find_default_user(request, user):
    if Player.objects.filter(user=user).exists():
        return Player.objects.get(user=user)
    if Coach.objects.filter(user=user).exists():
        return Coach.objects.get(user=user)
    if Fan.objects.filter(user=user).exists():
        return Fan.objects.get(user=user)
    return None

