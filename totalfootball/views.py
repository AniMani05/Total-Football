from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Sum, Case, When, F, IntegerField, Value, Subquery, OuterRef

import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import User, Player, Team, League, LeagueTeam
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, ProfileForm, JoinLeagueForm, CreateLeagueForm

import requests

API_URL = "https://api-football-v1.p.rapidapi.com/v3"
API_KEY = "f718776270mshdd18e7b443cbdc3p18da49jsn5614850c11a8"

HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY,
}

def fetch_past_player_stats(player_id, season):
    """
    Fetch past stats for a player for a specific season.
    """
    url = f"{API_URL}/players"
    params = {
        "id": player_id,
        "season": season,  # Specify the past season (e.g., "2022")
    }
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 200:
        data = response.json()
        # Debug: Print the raw API response
        print(f"API Response for Player {player_id} (Season {season}): {data}")
        if data['response']:
            # Extract relevant stats
            stats = data['response'][0]['statistics'][0]
            return {
                "goals": stats['goals']['total'] or 0,
                "assists": stats['goals']['assists'] or 0,
                "matches_played": stats['games']['appearances'] or 0,
                "clean_sheets": stats.get('clean_sheet', 0)  # Some APIs may have clean sheet data
            }
    else:
        print(f"Error fetching stats for player {player_id}: {response.status_code}")
    return None

def fetch_player_stats(player_ids):
    """
    Fetch live stats for a list of player IDs.
    """
    url = f"{API_URL}/players"
    player_stats = {}

    for player_id in player_ids:
        params = {"id": player_id, "season": "2023"}
        response = requests.get(url, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data['response']:
                stats = data['response'][0]['statistics'][0]
                player_stats[player_id] = {
                    "goals": stats['goals']['total'],
                    "assists": stats['goals']['assists'],
                    "matches_played": stats['games']['appearances'],
                    # Add more fields if needed
                }
        else:
            print(f"Error fetching stats for player {player_id}: {response.status_code}")
    
    return player_stats

def homepage_action(request):
    top_players = Player.objects.order_by('-points')[:10]

    teams = Team.objects.all()
    team_points = []

    for team in teams:
        captain_points = 0
        non_captain_points = 0
        
        if team.captain:
            captain_points = (team.captain.points or 0) * 2
        
        non_captain_points = team.players.exclude(id=team.captain_id).aggregate(
            total=Sum('points')
        )['total'] or 0

        total_points = captain_points + non_captain_points

        team_points.append({
            'username': team.user.username,
            'total_points': total_points,
        })

    top_users = sorted(team_points, key=lambda x: x['total_points'], reverse=True)[:10]

    context = {
        'top_players': top_players,
        'top_users': top_users,
    }

    return render(request, 'homepage.html', context)

def login_action(request):
    if request.user.is_authenticated:
        return redirect('homepage')

    context = {}

    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'start.html', context)

    form = LoginForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'start.html', context)

    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    new_user = authenticate(username=username, password=password)

    if new_user is None:
        messages.error(request, "Invalid username or password.")
        return render(request, 'start.html', context)

    login(request, new_user)
    return redirect('homepage')

def register_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegisterForm()
        print("Returning form")
        return render(request, 'register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'register.html', context)
    
    if form.cleaned_data['password1'] != form.cleaned_data['password2']:
        context['error'] = 'Passwords do not match.'
        print("Password error")
        return render(request, 'register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.is_active = True
    new_user.save()
    
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])

    if new_user:
        login(request, new_user)
        print("Finished logging in, trying to go to global stream")
        return redirect(reverse('homepage'))
    else:
        print("Authentication failed.")
        return render(request, 'register.html', {'form': form, 'error': 'Authentication failed.'})

def logout_action(request):
    logout(request)
    
    return redirect('login')

def profile_action(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {}

    context['other'] = user_id != request.user.id

    if not context['other']:
        print("User is viewing their own profile")

        if request.method == "GET":
            form = ProfileForm(initial={
                'team_name': request.user.team_name,
                'profile_image': request.user.profile_image
            })
            context['form'] = form
            return render(request, 'profile.html', context)

        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            request.user.team_name = form.cleaned_data['team_name']
            if 'profile_image' in request.FILES:
                request.user.profile_image = form.cleaned_data['profile_image']
            request.user.save()

            return redirect('profile', user_id=request.user.id)
        else:
            context['form'] = form
            return render(request, 'profile.html', context)

    else:
        context['form'] = None
        context['otherUser'] = user

    return render(request, "profile.html", context)

@login_required
def get_profile_picture(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if not user.profile_image:
        raise Http404("No profile image found for this user.")

    try:
        with open(user.profile_image.path, 'rb') as f:
            image_data = f.read()
    except FileNotFoundError:
        raise Http404("Profile image file not found.")

    return HttpResponse(image_data, content_type='image/jpeg')

@login_required
def select_lineup(request):
    team, created = Team.objects.get_or_create(user=request.user)

    players_by_position = {
        'Goalkeepers': Player.objects.filter(position='Goalkeeper').order_by('name'),
        'Defenders': Player.objects.filter(position='Defender').order_by('name'),
        'Midfielders': Player.objects.filter(position='Midfielder').order_by('name'),
        'Forwards': Player.objects.filter(position='Forward').order_by('name'),
    }

    if request.method == "POST":
        if request.content_type == "application/json":
            data = json.loads(request.body)
            player_ids = data.get('players')
            captain_id = data.get('captain_id')
        else:
            player_ids = request.POST.getlist('players')
            captain_id = request.POST.get('captain')

        if not player_ids or not captain_id:
            if request.content_type == "application/json":
                return JsonResponse({'error': "You must select players and a captain."}, status=400)
            else:
                messages.error(request, "You must select players and a captain.")
                return redirect('select_lineup')

        players_selected = Player.objects.filter(id__in=player_ids)
        captain = Player.objects.filter(id=captain_id).first()

        if len(players_selected) != 11:
            if request.content_type == "application/json":
                print(players_selected)
                return JsonResponse({'error': "You must select exactly 11 players."}, status=400)
            else:
                messages.error(request, "You must select exactly 11 players.")
                return redirect('select_lineup')

        if not captain or captain not in players_selected:
            if request.content_type == "application/json":
                return JsonResponse({'error': "The captain must be one of the selected players."}, status=400)
            else:
                messages.error(request, "The captain must be one of the selected players.")
                return redirect('select_lineup')

        team.starting_lineup.set(players_selected)
        team.captain = captain
        team.save()

        if request.content_type == "application/json":
            return JsonResponse({'message': "Your lineup has been saved successfully!"})
        else:
            messages.success(request, "Your lineup has been saved successfully!")
            return redirect('homepage')

    context = {
        'players_by_position': players_by_position,
    }
    return render(request, 'select_lineup.html', context)

# @login_required
# def my_team_view(request):
#     try:
#         team = Team.objects.get(user=request.user)
#         players = team.starting_lineup.all()
#         captain = team.captain
#     except Team.DoesNotExist:
#         messages.error(request, "You haven't selected a team yet.")
#         return redirect('select_lineup')

#     context = {
#         'team': team,
#         'players': players,
#         'captain': captain,
#     }

#     return render(request, 'my_team.html', context)

def calculate_past_points(stats, position):
    """
    Calculate points for past stats based on goals, assists, matches, and position.
    """
    points = 0

    # Points for goals
    points += stats.get("goals", 0) * 4

    # Points for assists
    points += stats.get("assists", 0) * 3

    # Points for matches played
    points += stats.get("matches_played", 0) * 1

    # Additional points for clean sheets (only defenders and goalkeepers)
    if position in ['Defender', 'Goalkeeper'] and stats.get("clean_sheets", 0):
        points += 4

    return points

def calculate_points(stats, position):
    """
    Calculate points for a player based on live stats and their position.
    """
    points = 0

    # Points for goals
    points += stats.get("goals", 0) * 4

    # Points for assists
    points += stats.get("assists", 0) * 3

    # Points for matches played
    points += stats.get("matches_played", 0) * 1

    # Additional points for clean sheets (only defenders and goalkeepers)
    if position in ['Defender', 'Goalkeeper'] and stats.get("clean_sheets", 0):
        points += 4

    return points

# @login_required
# def my_team_view(request):
#     try:
#         team = Team.objects.get(user=request.user)
#         players = team.starting_lineup.all()
#         captain = team.captain

#         # Get player IDs
#         player_ids = [player.api_football_id for player in players if player.api_football_id]
#         player_stats = fetch_player_stats(player_ids)

#         # Attach live stats to players and update points
#         for player in players:
#             stats = player_stats.get(player.api_football_id, {})
#             player.live_stats = stats
#             player.points = calculate_points(stats, player.position)  # Update points
            
#             # Print player details for debugging
#             print(f"Player: {player.name}")
#             print(f"Live Stats: {stats}")
#             print(f"Calculated Points: {player.points}")
            
#             player.save()  # Save updated points to the database

#     except Team.DoesNotExist:
#         messages.error(request, "You haven't selected a team yet.")
#         return redirect('select_lineup')

#     context = {
#         'team': team,
#         'players': players,
#         'captain': captain,
#     }

#     return render(request, 'my_team.html', context)

@login_required
def my_team_view(request):
    try:
        team = Team.objects.get(user=request.user)
        players = team.starting_lineup.all()
        captain = team.captain

        # Get player IDs
        player_ids = [player.api_football_id for player in players if player.api_football_id]

        # Fetch live stats and past stats
        live_player_stats = fetch_player_stats(player_ids)
        past_season = "2022"  # Example of a past season
        for player in players:
            stats = live_player_stats.get(player.api_football_id, {})
            past_stats = fetch_past_player_stats(player.api_football_id, past_season)

            # Update live points
            player.live_stats = stats
            player.points = calculate_points(stats, player.position)

            # Update past points
            if past_stats:
                player.past_points = calculate_past_points(past_stats, player.position)
            else:
                player.past_points = 0  # Default to 0 if no past stats available
            
            # Print debugging information
            print(f"Player: {player.name}")
            print(f"Live Stats: {stats}")
            print(f"Past Stats: {past_stats}")
            print(f"Live Points: {player.points}")
            print(f"Past Points: {player.past_points}")

            player.save()  # Save updated points to the database

    except Team.DoesNotExist:
        messages.error(request, "You haven't selected a team yet.")
        return redirect('select_lineup')

    context = {
        'team': team,
        'players': players,
        'captain': captain,
    }

    return render(request, 'my_team.html', context)


@login_required
def create_league(request):
    if request.method == 'POST':
        form = CreateLeagueForm(request.POST)
        if form.is_valid():
            league = form.save(commit=False)
            league.creator = request.user
            league.save()
            
            league.members.add(request.user)
            
            LeagueTeam.objects.create(user=request.user, league=league)
            
            return redirect('league_details', league_id=league.id)
    else:
        form = CreateLeagueForm()
    return render(request, 'create_league.html', {'form': form})

@login_required
def join_league(request):
    if request.method == 'POST':
        form = JoinLeagueForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                league = League.objects.get(code=code)
                
                if request.user not in league.members.all():
                    league.members.add(request.user)
                
                league_team, created = LeagueTeam.objects.get_or_create(user=request.user, league=league)
                
                return redirect('league_details', league_id=league.id)
                
            except League.DoesNotExist:
                form.add_error('code', 'Invalid league code.')
    else:
        form = JoinLeagueForm()
    return render(request, 'join_league.html', {'form': form})

@login_required
def league_details(request, league_id):
    league = get_object_or_404(League, id=league_id)
    
    league_teams = league.league_teams.all()
    
    teams_with_players = league_teams.filter(players__isnull=False).distinct()

    show_members_for_draft = not teams_with_players.exists()
    
    return render(request, 'league_details.html', {
        'league': league,
        'league_teams': league_teams,
        'show_members_for_draft': show_members_for_draft,
    })