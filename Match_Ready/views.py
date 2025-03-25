from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from datetime import datetime



from Match_Ready.models import User,Fan, Player,Coach, Match, Team #Team sheets, announcements

from Match_Ready.forms import UserForm, FindTeamForm, NewTeamForm, AddMatch

def index (request):
    return render(request, 'Match_Ready/index.html')

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
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']

            if user_form.cleaned_data['role'] == 'player':
                user = Player(username=username)
            elif user_form.cleaned_data['role'] == 'coach':
                user = Coach(username=username)
            elif user_form.cleaned_data['role'] == 'fan':
                user = Fan(username=username)

            user.set_password(password)
            user.save()

            return redirect('Match_Ready:login')
    else:
        user_form = UserForm()

    return render(request, 'Match_Ready/signup.html', {
        'user_form': user_form,
        'form': user_form,
        'registered': registered
    })

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
    return render(request,'Match_Ready/UpcomingMatches.html',context=context_dict)

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

#temperarrilly changed to see the working create team form

@login_required
def create_team(request):
    context_dict = {}
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
def ListOfPlayers(request, team_id):
    team = Team.objects.get(id=team_id)
    context_dict = {'team_detail':'pass'}
    #
    #
    return render(request,'Match_Ready/team_detail.html',context=context_dict)


@login_required
def fixtures(request, team_id):
    fixtures = fixtures.objects.filter(id=team_id).order_by('post_date')[:10]
    context_dict={'fixtures':fixtures}
    return render(request,'Match_Ready/fixtures.html',context=context_dict)
 









# @login_required
# def add_page(request, category_name_slug):
#     try:
#         category = Category.objects.get(slug=category_name_slug)
#     except Category.DoesNotExist:
#         category=None

#     if category is None:
#         return redirect(reverse('Match_Ready:home'))
    
#     form = PageForm()

#     if request.method == 'POST':
#         form = PageForm(request.POST)
#         if form.is_valid():
#             if category:
#                 page = form.save(commit=False)
#                 page.category = category
#                 page.views = 0
#                 page.save()
#                 return redirect(reverse('Match_Ready:show_category',kwargs={'category_name_slug':category_name_slug}))
#             else:
#                 print(form.errors)
#     context_dict = {'form': form,'category': category}
#     return render(request, 'Match_Ready/add_page.html', context=context_dict)


# def show_category(request, category_name_slug):
#     context_dict={}

#     try:
#         category = Category.objects.get(slug=category_name_slug)
#         pages = Page.objects.filter(category=category)
#         context_dict['pages'] = pages
#         context_dict['category'] = category
#     except Category.DoesNotExist:
#         context_dict['pages']=None
#         context_dict['category']=None
#     return render(request, 'Match_Ready/category.html', context=context_dict)

# @login_required
# def add_category(request):
#     form = CategoryForm()
    
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save(commit=True)
#             return redirect(reverse('Match_Ready:home'))
#         else:
#             print(form.errors)
#             return render(request, "Match_Ready/add_category.html", {"form": form, "errors": form.errors})  
#     return render(request, 'Match_Ready/add_category.html',{'form':form}) 