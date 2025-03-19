from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime



from Match_Ready.models import Team, User, Player, Fan, Coach, Match #Team sheets, announcements

#from Match_Ready.forms import NewTeamForm, FindTeamForm, PlayerForm, FanForm, CoachForm, UserProfileForm, AnnouncementForm

def home (request):
    return render(request, 'Match_Ready/home.html')

def about (request):
    return render(request, 'Match_Ready/about.html')

def contact(request):
    return render(request,'Match_Ready/contact.html')

def user_register(request, user_type):
    registered = False
    form_types = {'player_form':PlayerForm,'coach_form':CoachForm,'fan_form':FanForm}

    if user_type not in form_types:
        return render(request, 'Match_Ready/register.html', {'error': 'Not a valid user type'})
    
    selected_form = form_types[user_type]
    if request.method == 'POST':
        user_form = selected_form(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            registered = register(request, profile_form, user_form)
    else:
        user_form = selected_form()
        profile_form = UserProfileForm()

    return render(request, 'Match_Ready/register.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered,
        'user_type': user_type  
    })

def register(request, profile_form,user_form):
    user = user_form.save()
    user.save()

    profile = profile_form.save(commit=False)
    profile.user = user

    if 'picture' in request.FILES:
        profile.picture = request.FILES['picture']
    
    profile.save()

    return True

def user_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
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

def display_matches(request):
    next_matches = Match.objects.filter(finished=False).orderby('match_day')[:15]
    context_dict = {'upcoming_matches':next_matches}
    return render(request,'Match_Ready/matches.html',context=context_dict)

@login_required
def my_team(request,user_id):
    user = User.objects.get(id=user_id)
    teams = User.teams.all()
    context_dict = {'teams':teams}
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

@login_required
def create_announcement(request,team_id):
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        team = None

    if team is None:
        return redirect(reverse('Match_Ready:home'))
    
    form = AnnouncementForm()
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('Match_Ready:home'))
        else:
            print(form.errors)
            return render(request, "Match_Ready/create_announcements.html", {"form": form, "errors": form.errors})  
    return render(request, 'Match_Ready/create_announcements.html',{'form':form}) 

@login_required
def team_info(request, team_id):
    team = Team.objects.get(id=team_id)
    context_dict = {'team_detail':'pass'}
    #
    #
    return render(request,'Match_Ready/team_detail.html',context=context_dict)

@login_required
def announcements(request, team_id):
    announcements = Announcement.objects.filter(id=team_id).order_by('post_date')[:10]
    context_dict={'announcements':announcements}
    return render(request,'Match_Ready/announcements.html',context=context_dict)
 









@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category=None

    if category is None:
        return redirect(reverse('Match_Ready:home'))
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('Match_Ready:show_category',kwargs={'category_name_slug':category_name_slug}))
            else:
                print(form.errors)
    context_dict = {'form': form,'category': category}
    return render(request, 'Match_Ready/add_page.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict={}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages']=None
        context_dict['category']=None
    return render(request, 'Match_Ready/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('Match_Ready:home'))
        else:
            print(form.errors)
            return render(request, "Match_Ready/add_category.html", {"form": form, "errors": form.errors})  
    return render(request, 'Match_Ready/add_category.html',{'form':form}) 