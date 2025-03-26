from django.urls import path
from Match_Ready import views

app_name = 'Match_Ready'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('fixtures/', views.UpcomingMatches, name='fixtures'),  # Fixed typo from 'fixtues'
    path('upcoming_matches/', views.UpcomingMatches, name='UpcomingMatches'),
    path('signup/', views.user_register, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my_team/', views.my_team, name='my_team'),
    path('create_team/', views.create_team, name='create_team'),
    path('find_team/', views.find_team, name='find_team'),
    path('add_match/', views.add_match, name='add_match'),
    path('announcements/<int:team_id>/', views.announcements, name='announcements'),
    path('create_announcement/<int:team_id>/', views.create_announcement, name='create_announcement'),
    path('team_sheets/<int:team_id>/', views.team_sheets, name='team_sheets'),
    path('create_team_sheet/<int:team_id>/', views.create_team_sheet, name='create_team_sheet'),
    path('team_sheet_detail/<int:team_sheet_id>/', views.team_sheet_detail, name='team_sheet_detail'),
]