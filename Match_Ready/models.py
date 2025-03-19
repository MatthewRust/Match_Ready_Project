from django.db import models

class User(models.Model):
    user_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name
    

class Team(models.Model):
    name = models.CharField(max_length=128)
    team_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name
    
class Manager(User):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="manager")

class Player(User):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")

class Fan(User):
    favourite_teams = models.ManyToManyField(Team, related_name="fans")

class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    match_date = models.DateTimeField()

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} on {self.match_date.strftime('%Y-%m-%d %H:%M')}"

