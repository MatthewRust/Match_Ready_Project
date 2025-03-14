from django.shortcuts import render
from django.http import HttpResponse

def base(request):
    return render(request, '/base.html') 

def about(request):
    return render(request, 'Match_Ready/about.html')

def index(request):
    return render(request, 'Match_Ready/index.html')

def announcements(request):
    return render(request, 'Match_Ready/announcements.html')

def create_team(request):
    return render(request, 'Match_Ready/create_team.html')

def find_team(request):
    return render(request, 'Match_Ready/find_team.html')

def login(request):
    return render(request, 'Match_Ready/login.html')

def make_team(request):
    return render(request, 'Match_Ready/make_team.html')

def matches(request):
    return render(request, 'Match_Ready/matches.html')

def my_team(request):
    return render(request, 'Match_Ready/my_team.html')

def signup(request):
    return render(request, 'Match_Ready/signup.html')

def team_info(request):
    return render(request, 'Match_Ready/team_info.html')
