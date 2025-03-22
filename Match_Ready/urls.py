from django.urls import path
from Match_Ready import views
from django.urls import include
from django.contrib import admin 



app_name = 'Match_Ready'

urlpatterns = [
    path('', views.index, name ='index'),
    path('about/', views.about, name='about'),
    #path('announcements/', views.announcements, name='announcements'),
    path('create_team/', views.create_team, name='create_team'),
    path('find_team/', views.find_team, name='find_team'),
    path('login/', views.user_login, name='login'),
    #path('make_team/', views.make_team, name='make_team'),
    path('matches/', views.fixtures, name='matches'),
    path('my_team/', views.my_team, name='my_team'),
    path('signup/', views.user_register, name='signup'),
    path('team_info/', views.team_info, name='team_info'),
]