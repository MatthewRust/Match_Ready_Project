from django import forms 
from django.contrib.auth.models import User
from .models import User, Player, Fan, Team, Coach, Match 


class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=128)
    password = forms.CharField(widget=forms.PasswordInput())

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

    class Meta:
        model = Match
        fields = ('team1', 'team2', 'match_date')


# class PLayerForm(forms.ModelForm):
#     class Meta:
#         model = UserForm
#         fields = ('player')



# class CoachForm(forms.ModelForm):
#     class Meta:
#         model = UserForm
#         fields = ('coach')


# class FanForm(forms.ModelForm):
#     class Meta:
#         model = UserForm
#         fields = ('fan')

class FindTeamForm(forms.ModelForm):
    teamID = forms.IntegerField()
    class Meta:
        model = Team
        fields = ('teamID',)




#class AnnouncementForm(forms.ModelForm):
 #   teamID = forms.IntegerField()
  #  info = forms.CharField()
   # class Meta:
    #    model = Announcement
     #   fields = ('teamID', 'info')











