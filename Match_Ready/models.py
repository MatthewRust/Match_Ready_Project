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
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
<<<<<<< HEAD

=======
    
    
>>>>>>> 1c0304f99693c9ab95a0484d9660ebb4fed39580
class Coach(DefaultUser):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="coach", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Coaches'

class Player(DefaultUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players", null=True, blank=True)

class Fan(DefaultUser):
<<<<<<< HEAD
    favourite_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="fans", null=True, blank=True)
=======
    team = models.ForeignKey(Team, related_name="fans", on_delete=models.CASCADE, null=True,blank=True)
>>>>>>> 1c0304f99693c9ab95a0484d9660ebb4fed39580

class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    match_date = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'Matches'

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} on {self.match_date.strftime('%Y-%m-%d %H:%M')}"

class TeamSheet(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f"TeamSheet for {self.team.name} in match {self.match}"

class PlayerAvailability(models.Model):
    team_sheet = models.ForeignKey(TeamSheet, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('team_sheet', 'player')

class Announcement(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title