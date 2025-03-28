from django.urls import path
from Match_Ready import views
# Removed unused imports: include, admin

app_name = 'Match_Ready'

urlpatterns = [
    path('', views.index, name ='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('fixtures/', views.fixtures, name='fixtures'),
    path('signup/', views.user_register, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('create_team/', views.create_team, name='create_team'),
    path('find_team/', views.find_team, name='find_team'),
    path('my_team/', views.my_team, name='my_team'),
    path('my_team/players/', views.player_list, name='player_list'),
    path('add_match/', views.add_match, name='add_match' ),
    path('upcoming_matches/', views.upcoming_matches, name='upcoming_matches'),
]