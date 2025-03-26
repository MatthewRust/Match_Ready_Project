from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib import messages

from datetime import datetime
#create team, create match, find team, tests, ajax, javascript

from Match_Ready.models import Fan, Player,Coach, Match, Team #Team sheets, announcements

from Match_Ready.forms import UserForm, FindTeamForm, NewTeamForm, AddMatch

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
    return render(request,'Match_Ready/contact.html')

def add_match(request):
    return render(request, 'Match_Ready/add_match.html')

def UpcomingMatches(request):
    return render(request, 'Match_Ready/upcoming_matches.html')


def user_register(request):
    registered = False

    if request.method == 'POST':
        form = UserForm(request.POST)  
        
        if form.is_valid():
            # Create User
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            
            user = User.objects.create_user(username=username, password=password)
            
            if role == 'fan':
                Fan.objects.create(user=user)
            elif role == 'coach':
                Coach.objects.create(user=user)
            elif role == 'player':
                Player.objects.create(user=user)
            
            # Authenticate and login
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                return redirect('Match_Ready:index') 

            registered = True
        else:
            print(form.errors)  
    else:
        form = UserForm()

    return render(request, 'Match_Ready/signup.html', {'form': form, 'registered': registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse('Match_Ready:index'))
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('Match_Ready:login') 

    return render(request, 'Match_Ready/login.html')



@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('Match_Ready:index'))

def fixtures(request):
    next_matches = Match.objects.filter(finished=False).order_by('match_day')[:15]
    context_dict = {'upcoming_matches':next_matches}
    return render(request,'Match_Ready/UpcomingMatches.html',context=context_dict)


@login_required
def my_team(request):
    user = request.user
    if user is None:
        return redirect('Match_Ready:login')
    role = find_default_user(request,user)
    if role is None:
        return redirect('Match_Ready:login')
    if role.team is None:
        return redirect('Match_Ready:find_team')
    team_name = role.team.name
    context_dict = {'team_name':team_name}
    return render(request,'Match_Ready/my_team.html',context=context_dict)


@login_required
def find_team(request):
    user = request.user

    if user is None:
        return redirect(reverse('Match_Ready:index'))
    role = find_default_user(request,user)

    form = FindTeamForm()

    if request.method=='POST':
        form = FindTeamForm(request.POST)
        if form.is_valid():
            if role:
                team_id = form.cleaned_data['team_id']
                try:
                    team = Team.objects.get(id=team_id)  
                    role.team = team
                    role.save()
                    return redirect(reverse('Match_Ready:my_team',kwargs={'username':user.username}))
                except Team.DoesNotExist:
                    return HttpResponse("Team ID is incorrect")
            else:
                print(form.errors)
    context_dict = {'form':form,'user':user, 'role': role}
    return render(request,'Match_Ready/find_team.html',context=context_dict)

#temperarrilly changed to see the working create team form

@login_required
def create_team(request):
    context_dict = {}
    role = find_default_user(request,request.user)
    if not isinstance(role, Coach):
        messages.error(request, "Must be a coach to make a new team")
        return redirect('Match_Ready:index')

    # registered = False
    # if request.method == 'POST':
    #         team_form = NewTeamForm(request.POST)

    #         if team_form.is_valid():
    #             team = team_form.save()
    #             team.save()
    #             registered = True
    #             return redirect(reverse('Match_Ready:home'))

    # else:
    #     user_form = NewTeamForm()
    return render(request,'Match_Ready/create_team.html',context=context_dict)


@login_required
def player_list(request):
    user = request.user
    if user is None:
        return redirect(reverse('Match_Ready:index'))
    role = find_default_user(request,user)

    team = role.team
    list_of_players = Player.objects.filter(team=team)
    context_dict = {'list_of_players':list_of_players, 'team':team}
    
    return render(request,'Match_Ready/list_of_players.html',context=context_dict)


@login_required
def upcoming_matches(request):
    user = request.user
    if user is None:
        return redirect('Match_Ready:login')
    role = find_default_user(request, user)
    if role is None:
        return redirect('Match_Ready:login')
    if role.team is None:
        return redirect('Match_Ready:find_team')
    
    home_matches = Match.objects.filter(team1=role.team, match_date__gte=datetime.now()).order_by('match_date')[:10]
    away_matches = Match.objects.filter(team2=role.team, match_date__gte=datetime.now()).order_by('match_date')[:10]
    context_dict={'home_matches':home_matches,'away_matches':away_matches}
    return render(request,'Match_Ready/upcoming_matches.html',context=context_dict)


def find_default_user(request, user):

    print(get_user_model())


    print(f"Checking for user: {user.username} (ID: {user.id})")  # Debugging

    user_role = Player.objects.filter(user=user).first() or \
                Coach.objects.filter(user=user).first() or \
                Fan.objects.filter(user=user).first()

    if user_role:
        print(f"User role found: {user_role.__class__.__name__}")
        return user_role

    print("User is not a Fan, Coach, or Player")
    return None

def make_team(request):
    role = find_default_user(request,request.user)
    if not isinstance(role, Coach):
        messages.error(request, "Must be a coach to make a new match")
        return redirect('Match_Ready:index')
    return render('Match_Ready/make_team.html')