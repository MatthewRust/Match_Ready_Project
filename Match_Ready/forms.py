# Match_Ready/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Team, Match, Announcement, Player, Coach, Fan, TeamSheet # Added TeamSheet
from django.utils import timezone
from django.db.models import Q

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput()) # Add confirmation
    ROLE_CHOICES = [
        ('player', 'Player'),
        ('coach', 'Coach'),
        ('fan', 'Fan'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        label="Register as a:", # Improved label
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password') # Removed email for simplicity unless needed
        help_texts = {
            'username': None, # Hide default help text if desired
        }

    # Add validation for password confirmation
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password do not match."
            )

class NewTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        # Exclude team_id as it's auto-generated
        fields = ('name', 'description', 'location', 'sport')

class AddMatchForm(forms.ModelForm):
    # Make fields required if necessary
    team1 = forms.ModelChoiceField(queryset=Team.objects.all(), label="Home Team")
    team2 = forms.ModelChoiceField(queryset=Team.objects.all(), label="Away Team")
    match_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Match Date and Time"
    )
    location = forms.CharField(max_length=255, required=False) # Added location

    class Meta:
        model = Match
        fields = ('team1', 'team2', 'match_date', 'location')

    # Add validation: team1 != team2
    def clean(self):
        cleaned_data = super().clean()
        team1 = cleaned_data.get("team1")
        team2 = cleaned_data.get("team2")
        if team1 and team2 and team1 == team2:
            raise forms.ValidationError("Home team and Away team cannot be the same.")
        return cleaned_data


class FindTeamForm(forms.Form):
    # Input field for the user-friendly Team ID (UUID)
    team_id = forms.UUIDField(label='Enter Team ID')

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'content')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}), # Make textarea bigger
        }

class TeamSheetForm(forms.Form):
    # Select a future match involving the coach's team
    match = forms.ModelChoiceField(
        queryset=Match.objects.none(), # Initial empty queryset
        label="Select Match"
    )
    # Select players from the coach's team who are available
    available_players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.none(), # Initial empty queryset
        widget=forms.CheckboxSelectMultiple,
        required=False, # Allow submitting with no players selected (maybe)
        label="Select Available Players"
    )

    def __init__(self, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if team: # Ensure team is provided
            # Filter matches: Must involve this team and be in the future
            self.fields['match'].queryset = Match.objects.filter(
                Q(team1=team) | Q(team2=team),
                match_date__gte=timezone.now()
            ).order_by('match_date') # Order for easier selection

            # Filter players: Must belong to this team
            self.fields['available_players'].queryset = Player.objects.filter(team=team).select_related('user').order_by('user__username')
        else:
            # Handle case where team is None, maybe disable fields
            self.fields['match'].disabled = True
            self.fields['available_players'].disabled = True