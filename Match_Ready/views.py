from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from .models import Team, Match, Coach, Player, Fan, TeamSheet, PlayerAvailability, Announcement
from .forms import UserForm, NewTeamForm, AddMatchForm, FindTeamForm, AnnouncementForm, TeamSheetForm

def index(request):
    return render(request, 'Match_Ready/index.html')

def about(request):
    return render(request, 'Match_Ready/about.html')

def contact(request):
    return render(request, 'Match_Ready/contact.html')

def user_register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            role = user_form.cleaned_data['role']
            if role == 'fan':
                Fan.objects.create(user=user)
            elif role == 'coach':
                Coach.objects.create(user=user)
            elif role == 'player':
                Player.objects.create(user=user)
            auth_user = authenticate(username=user.username, password=user_form.cleaned_data['password'])
            login(request, auth_user)
            return redirect('Match_Ready:index')
    else:
        user_form = UserForm()
    return render(request, 'Match_Ready/signup.html', {'form': user_form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('Match_Ready:index')
        return HttpResponse("Invalid login details.")
    return render(request, 'Match_Ready/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('Match_Ready:index')

def UpcomingMatches(request):
    matches = Match.objects.filter(match_date__gte=timezone.now()).order_by('match_date')
    return render(request, 'Match_Ready/upcoming_matches.html', {'matches': matches})

@login_required
def my_team(request):
    default_user = request.user.defaultuser
    team = None
    if isinstance(default_user, Player):
        team = default_user.team
    elif isinstance(default_user, Coach):
        team = default_user.team
    elif isinstance(default_user, Fan):
        team = default_user.favourite_team
    matches = Match.objects.filter(
        Q(team1=team) | Q(team2=team),
        match_date__gte=timezone.now()
    ).order_by('match_date') if team else []
    announcements = Announcement.objects.filter(team=team).order_by('-date_posted') if team else []
    team_sheets = TeamSheet.objects.filter(team=team) if team else []
    return render(request, 'Match_Ready/my_team.html', {
        'team': team,
        'matches': matches,
        'announcements': announcements,
        'team_sheets': team_sheets
    })

@login_required
def create_team(request):
    default_user = request.user.defaultuser
    if not isinstance(default_user, Coach):
        return HttpResponse("Only coaches can create teams.")
    if request.method == 'POST':
        form = NewTeamForm(request.POST)
        if form.is_valid():
            team = form.save()
            default_user.team = team
            default_user.save()
            return redirect('Match_Ready:my_team')
    else:
        form = NewTeamForm()
    return render(request, 'Match_Ready/create_team.html', {'form': form})

@login_required
def find_team(request):
    default_user = request.user.defaultuser
    if isinstance(default_user, Coach):
        return HttpResponse("Coaches cannot join other teams.")
    if request.method == 'POST':
        form = FindTeamForm(request.POST)
        if form.is_valid():
            team_id = form.cleaned_data['team_id']
            try:
                team = Team.objects.get(team_id=team_id)
                if isinstance(default_user, Player):
                    default_user.team = team
                elif isinstance(default_user, Fan):
                    default_user.favourite_team = team
                default_user.save()
                return redirect('Match_Ready:my_team')
            except Team.DoesNotExist:
                return HttpResponse("Team ID is incorrect.")
    else:
        form = FindTeamForm()
    return render(request, 'Match_Ready/find_team.html', {'form': form})

@login_required
def add_match(request):
    default_user = request.user.defaultuser
    if not isinstance(default_user, Coach):
        return HttpResponse("Only coaches can add matches.")
    if request.method == 'POST':
        form = AddMatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('Match_Ready:UpcomingMatches')
    else:
        form = AddMatchForm()
    return render(request, 'Match_Ready/add_match.html', {'form': form})

@login_required
def announcements(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    announcements = Announcement.objects.filter(team=team).order_by('-date_posted')
    return render(request, 'Match_Ready/announcements.html', {'team': team, 'announcements': announcements})

@login_required
def create_announcement(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    default_user = request.user.defaultuser
    if not isinstance(default_user, Coach) or default_user.team != team:
        return HttpResponse("Only the coach of this team can post announcements.")
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.team = team
            announcement.coach = default_user
            announcement.save()
            return redirect('Match_Ready:announcements', team_id=team_id)
    else:
        form = AnnouncementForm()
    return render(request, 'Match_Ready/create_announcement.html', {'form': form, 'team': team})

@login_required
def team_sheets(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    team_sheets = TeamSheet.objects.filter(team=team)
    return render(request, 'Match_Ready/team_sheets.html', {'team': team, 'team_sheets': team_sheets})

@login_required
def create_team_sheet(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    default_user = request.user.defaultuser
    if not isinstance(default_user, Coach) or default_user.team != team:
        return HttpResponse("Only the coach of this team can create team sheets.")
    if request.method == 'POST':
        form = TeamSheetForm(team, request.POST)
        if form.is_valid():
            match = form.cleaned_data['match']
            available_players = form.cleaned_data['available_players']
            team_sheet = TeamSheet.objects.create(match=match, team=team)
            for player in team.players.all():
                PlayerAvailability.objects.create(
                    team_sheet=team_sheet,
                    player=player,
                    available=player in available_players
                )
            return redirect('Match_Ready:team_sheets', team_id=team_id)
    else:
        form = TeamSheetForm(team)
    return render(request, 'Match_Ready/create_team_sheet.html', {'form': form, 'team': team})

@login_required
def team_sheet_detail(request, team_sheet_id):
    team_sheet = get_object_or_404(TeamSheet, id=team_sheet_id)
    availabilities = PlayerAvailability.objects.filter(team_sheet=team_sheet)
    return render(request, 'Match_Ready/team_sheet_detail.html', {
        'team_sheet': team_sheet,
        'availabilities': availabilities
    })