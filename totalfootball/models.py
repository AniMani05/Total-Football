import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

class User(AbstractUser):
    email = models.EmailField(unique=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    leagues = models.ManyToManyField('League', related_name='members', blank=True)

    def __str__(self):
        return self.username


class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    league = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.team})"


class League(models.Model):
    name = models.CharField(max_length=100)
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_leagues', null=True, blank=True)

    def __str__(self):
        return f"{self.name} (Draft)"


class Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teams')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams', 
                               null=True, blank=True)
    players = models.ManyToManyField(Player, related_name='teams')
    captain = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, 
                                related_name='captain_teams')
    starting_lineup = models.ManyToManyField(Player, related_name='starting_lineups', blank=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'league'], name='unique_user_league')
        ]


    @property
    def calculated_points(self):
        # Handle the captain's double points
        captain_points = self.captain.points * 2 if self.captain else 0

        # Sum points of other players
        other_points = (
            self.players.exclude(id=self.captain.id)
            .aggregate(total=Sum('points'))['total'] or 0
        )

        return captain_points + other_points

    def __str__(self):
        if self.league:
            return f"{self.user.username}'s Team in {self.league.name}"
        return f"{self.user.username}'s Global Team"
    
class LeagueTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='league_teams')
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='league_teams')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    players = models.ManyToManyField(Player, related_name='league_teams')
    captain = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='league_team_captain')
    starting_lineup = models.ManyToManyField(Player, related_name='league_team_starting_lineup', blank=True)

    @property
    def calculated_points(self):
        # Handle the captain's double points
        captain_points = self.captain.points * 2 if self.captain else 0

        # Sum points of other players
        other_points = (
            self.players.exclude(id=self.captain.id)
            .aggregate(total=Sum('points'))['total'] or 0
        )

        return captain_points + other_points

    def __str__(self):
        return f"{self.user.username}'s Team in {self.league.name}"

class Match(models.Model):
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    score = models.CharField(max_length=20, blank=True, null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.team_1} vs {self.team_2} on {self.date}"
