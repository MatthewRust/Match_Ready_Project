from django import forms 
from django.contrib.auth.models import User
from .models import User, Player, Fan, Team, Coach, Match, DefaultUser 


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=128)
    password = forms.CharField(widget=forms.PasswordInput())
    ROLE_CHOICES = [
        ('player', 'Player'),
        ('coach', 'Coach'),
        ('fan','Fan'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ('username', 'password')



class NewTeamForm(forms.ModelForm):
    name = forms.CharField(max_length=128)
    #not sure if team_id is auto incrementing and if so and input would not be required
    class Meta:
        model = Team
        fields = ('name', 'team_id')


class AddMatch(forms.ModelForm):
    team1 = forms.IntegerField()
    team2 = forms.IntegerField()
    match_date = forms.DateTimeField()
    attendies = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    class Meta:
        model = Match
        fields = ('team1', 'team2', 'match_date')


class FindTeamForm(forms.Form):
    team_id = forms.CharField()










