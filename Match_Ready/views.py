from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Q


from Match_Ready.models import User, Player,Coach, Match, Team

from Match_Ready.forms import NewTeamForm, FindTeamForm, UserForm

def index (request):
    return render(request, 'Match_Ready/index.html')

def about (request):
    return render(request, 'Match_Ready/about.html')

def contact(request):
    return render(request,'Match_Ready/contact.html')

def user_register(request):
    registered = False
    
    if request.method == 'POST':
        print("--------post---------")
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            print("--------is valid----------")
            registered = register(request, user_form)
    else:
        user_form = UserForm()

    return render(request, 'Match_Ready/signup.html', {
        'user_form': user_form,
        'registered': registered
    })

def register(request, user_form):
    user = user_form.save()
    user.save()

    return True

def user_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('Match_Ready:home'))
            else:
                return HttpResponse("Your Match_Ready account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'Match_Ready/login.html')
    
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('Match_Ready:home'))

def fixtures(request):
    now = datetime.now()
    fixtures = Match.objects.filter(match_date__gte=now).order_by('match_date')[:15]
    context_dict = {'upcoming_matches':fixtures}
    return render(request,'Match_Ready/matches.html',context=context_dict)

@login_required
def my_team(request,user_id):
    user = User.objects.get(id=user_id)
    team = user.team.all()
    context_dict = {'team':team}
    return render(request,'Match_Ready/my_team.html',context=context_dict)

@login_required
def find_team(request,user_id):
    user = get_object_or_404(User,id=user_id)

    if user is None:
        return redirect(reverse('Match_Ready:home'))
    
    form = FindTeamForm()

    if request.method=='POST':
        form = FindTeamForm(request.POST)
        if form.is_valid():
            if user:
                team_id = form.cleaned_data['team_id']
                try:
                    team = Team.objects.get(id=team_id)  # Fetch the team instance
                    user.teams.add(team)
                    return redirect(reverse('Match_Ready:my_team',kwargs={'user_id':user_id}))
                except Team.DoesNotExist:
                    return HttpResponse("Team ID is incorrect")
            else:
                print(form.errors)
    context_dict = {'form':form,'user':user}
    return render(request,'Match_Ready/find_team.html',context=context_dict)

@login_required
def create_team(request):
    context_dict = {}
    registered = False
    if request.method == 'POST':
            team_form = NewTeamForm(request.POST)

            if team_form.is_valid():
                team = team_form.save()
                team.save()
                registered = True
                return redirect(reverse('Match_Ready:home'))

    else:
        user_form = NewTeamForm()
    return render(request,'Match_Ready/create_team.html',context=context_dict)

#@login_required
#def create_announcement(request,team_id):
 #   try:
  #      team = Team.objects.get(id=team_id)
   # except Team.DoesNotExist:
    #    team = None

    #if team is None:
     #   return redirect(reverse('Match_Ready:home'))
    
   # form = AnnouncementForm()
    
    #if request.method == 'POST':
     #   form = AnnouncementForm(request.POST)
      #  if form.is_valid():
       #     form.save(commit=True)
        #    return redirect(reverse('Match_Ready:home'))
        #else:
         #   print(form.errors)
          #  return render(request, "Match_Ready/create_announcements.html", {"form": form, "errors": form.errors})  
    #return render(request, 'Match_Ready/create_announcements.html',{'form':form}) 

@login_required
def team_info(request, team_id):
    team = Team.objects.get(id=team_id)
    players = Player.objects.filter(team_id=team_id)
    context_dict = {'players':players}
    return render(request,'Match_Ready/team_detail.html',context=context_dict)

@login_required
def team_fixtures(request, team_id):
    now = datetime.now()
    team_fixtures = Match.objects.filter(Q(team1__id=team_id) | Q(team2__id=team_id),match_date__gte=now).order_by('match_date')[:10]    
    context_dict={'team_fixtures':team_fixtures}
    return render(request,'Match_Ready/announcements.html',context=context_dict)