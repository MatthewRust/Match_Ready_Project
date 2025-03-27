# Match_Ready/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=128)
    team_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=128, blank=True)
    sport = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class DefaultUser(models.Model):
    # Link to the built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='defaultuser')
    # No team link here, keep it in subclasses

    def __str__(self):
        return self.user.username

class Coach(DefaultUser):
    # A Coach manages one Team. Use OneToOneField if a team has only one coach.
    # Use ForeignKey if a team can have multiple coaches (adjust related_name if needed).
    # Allowing null=True, blank=True means a Coach can exist without a team initially.
    team = models.OneToOneField(Team, on_delete=models.SET_NULL, related_name="coach_profile", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Coaches'

    def __str__(self):
        return f"Coach: {self.user.username}" + (f" (Team: {self.team.name})" if self.team else " (No Team)")


class Player(DefaultUser):
    # A Player belongs to one Team.
    # Allowing null=True, blank=True means a Player can exist without a team initially.
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="players", null=True, blank=True)

    def __str__(self):
        return f"Player: {self.user.username}" + (f" (Team: {self.team.name})" if self.team else " (No Team)")


class Fan(DefaultUser):
    # A Fan can follow one Team.
    # Allowing null=True, blank=True means a Fan can exist without a favorite team initially.
    favourite_team = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name="fans", null=True, blank=True)

    def __str__(self):
       return f"Fan: {self.user.username}" + (f" (Following: {self.favourite_team.name})" if self.favourite_team else " (No Favourite Team)")


class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    match_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, default="TBC")

    class Meta:
        verbose_name_plural = 'Matches'
        ordering = ['match_date']

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} on {self.match_date.strftime('%Y-%m-%d %H:%M')}"

class TeamSheet(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='team_sheets')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_sheets')
    # Add created/published timestamps if needed
    # created_at = models.DateTimeField(auto_now_add=True)
    # published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"TeamSheet for {self.team.name} - Match on {self.match.match_date.strftime('%Y-%m-%d')}"

class PlayerAvailability(models.Model):
    team_sheet = models.ForeignKey(TeamSheet, on_delete=models.CASCADE, related_name='player_availabilities')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='availabilities')
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('team_sheet', 'player') # Ensures one entry per player per sheet
        verbose_name_plural = 'Player Availabilities'

    def __str__(self):
        status = "Available" if self.available else "Not Available"
        return f"{self.player.user.username} - {status} for Sheet {self.team_sheet.id}"


class Announcement(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='announcements')
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE) # Assuming only coaches post
    title = models.CharField(max_length=128)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_posted'] # Show newest first

    def __str__(self):
        return f"'{self.title}' for {self.team.name}"