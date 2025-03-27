from django.db import models
from django.contrib.auth.models import User

    
class Team(models.Model):
    name = models.CharField(max_length=128)
    team_id = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name
    

class DefaultUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
    
    
class Coach(DefaultUser):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name="coach", null=True,blank=True)

    class Meta:
        verbose_name_plural = 'Coaches'

class Player(DefaultUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players", null=True,blank=True)

class Fan(DefaultUser):
    team = models.ForeignKey(Team, related_name="fans", on_delete=models.CASCADE, null=True,blank=True)

class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    match_date = models.DateTimeField()
    attendees = models.IntegerField(default=0)
    attendees_list = models.ManyToManyField(User, blank=True)

    def add_attendee(self, user):
        if user not in self.attendees_list.all():
            self.attendees += 1
            self.attendees_list.add(user)
            self.save()

    class Meta:
        verbose_name_plural = 'Matches'

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name} on {self.match_date.strftime('%Y-%m-%d %H:%M')}"