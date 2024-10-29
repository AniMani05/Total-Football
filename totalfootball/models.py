from django.contrib.auth.models import AbstractUser
from django.db import models

# User Model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    team_name = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

class Player(models.Model):
    player_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    league = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    points = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.team})"

class League(models.Model):
    LEAGUE_TYPE_CHOICES = [
        ('global', 'Global'),
        ('custom', 'Custom'),
    ]
    league_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=LEAGUE_TYPE_CHOICES)
    members = models.ManyToManyField(User, related_name='leagues')

    def __str__(self):
        return self.name

class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team')
    players = models.ManyToManyField(Player, related_name='teams')
    starting_lineup = models.ManyToManyField(Player, related_name='starting_lineups')
    captain = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='captain_teams')
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Team"


class Match(models.Model):
    match_id = models.AutoField(primary_key=True)
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    score = models.CharField(max_length=20)  # e.g., '2-1'
    date = models.DateField()

    def __str__(self):
        return f"{self.team_1} vs {self.team_2} on {self.date}"
