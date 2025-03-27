# Match_Ready/urls.py
from django.urls import path
from Match_Ready import views

app_name = 'Match_Ready'

urlpatterns = [
    # General Pages
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Authentication
    path('signup/', views.user_register, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Matches / Fixtures
    path('fixtures/', views.UpcomingMatches, name='fixtures'), # Public view
    # Renamed from UpcomingMatches to fixtures for consistency if used elsewhere
    # path('upcoming_matches/', views.UpcomingMatches, name='UpcomingMatches'), # Keep if needed, but fixtures is better

    # Team Management (Authenticated Users)
    path('my_team/', views.my_team, name='my_team'),
    path('create_team/', views.create_team, name='create_team'), # For Coaches
    path('find_team/', views.find_team, name='find_team'), # For Players/Fans

    # Coach Specific Actions
    path('add_match/', views.add_match, name='add_match'), # For Coaches to add matches

    # Team Specific Content (using team's primary key 'id')
    path('announcements/<int:team_id>/', views.announcements, name='announcements'),
    path('create_announcement/<int:team_id>/', views.create_announcement, name='create_announcement'), # Coach action
    path('team_sheets/<int:team_id>/', views.team_sheets, name='team_sheets'), # View list
    path('create_team_sheet/<int:team_id>/', views.create_team_sheet, name='create_team_sheet'), # Coach action

    # Team Sheet Detail (using team sheet's primary key 'id')
    path('team_sheet/<int:team_sheet_id>/', views.team_sheet_detail, name='team_sheet_detail'), # Renamed from team_sheet_detail for clarity
]