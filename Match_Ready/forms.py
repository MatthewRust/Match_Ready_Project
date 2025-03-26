from django import forms
from django.contrib.auth.models import User
from .models import Team, Match, Announcement, Player, Coach, Fan

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    ROLE_CHOICES = [
        ('player', 'Player'),
        ('coach', 'Coach'),
        ('fan', 'Fan'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ('username', 'password')

class NewTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('name', 'description', 'location', 'sport')

class AddMatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ('team1', 'team2', 'match_date')
        widgets = {
            'match_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class FindTeamForm(forms.Form):
    team_id = forms.UUIDField(label='Team ID')

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'content')

class TeamSheetForm(forms.Form):
    match = forms.ModelChoiceField(queryset=Match.objects.none())
    available_players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.utils import timezone
        from django.db.models import Q
        self.fields['match'].queryset = Match.objects.filter(
            Q(team1=team) | Q(team2=team),
            match_date__gte=timezone.now()
        )
        self.fields['available_players'].queryset = team.players.all()