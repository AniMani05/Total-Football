from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Sum, Case, When, F, IntegerField, Value, Subquery, OuterRef
from django.utils.timezone import now
from datetime import timedelta

import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import User, Player, Team, League, LeagueTeam, DraftPick
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, ProfileForm, JoinLeagueForm, CreateLeagueForm

import requests

API_URL = "https://api-football-v1.p.rapidapi.com/v3"
API_KEY = "f718776270mshdd18e7b443cbdc3p18da49jsn5614850c11a8"

HEADERS = {
    "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
    "x-rapidapi-key": API_KEY,
}

def homepage_action(request):
    # Displays the top ten overall players on the home page
    top_players = Player.objects.order_by('-points')[:10]

    # Displays each team and their points
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

    # Sorts the teams by their total points scored
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
def update_player_stats(request, player_id):
    if request.method == "POST":
        try:
            # Fetch stats from the external API
            result = fetch_player_stats(player_id) 

            if result["success"]:
                return JsonResponse({"success": True, "message": f"Player {player_id} updated successfully."})
            else:
                return JsonResponse({"success": False, "error": result["error"]}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def draft_view(request, league_id):
    league = get_object_or_404(League, id=league_id)

    if not league.draft_started:
        league.draft_started = True
        league.save()

    # Total teams in the league
    total_teams = league.league_teams.count()

    if league.current_pick > (total_teams * 15):
        league.draft_started = False
        league.save()
        return redirect('league_details', league_id=league.id)

    # Calculate the current round number
    round_number = (league.current_pick - 1) // total_teams + 1

    # Determine the direction based on the round number
    direction = 'id' if round_number % 2 == 1 else '-id'
    teams = league.league_teams.order_by(direction)

    # Handle draft pick submission
    if request.method == 'POST':
        player_id = request.POST.get('player_id')
        player = get_object_or_404(Player, id=player_id)

        # Check if player is already picked
        if DraftPick.objects.filter(league=league, player=player).exists():
            messages.error(request, 'Player already drafted.')
        else:
            # Record the draft pick
            current_team_index = (league.current_pick - 1) % total_teams
            current_team = teams[current_team_index]
            DraftPick.objects.create(
                league=league,
                team=current_team,
                player=player,
                pick_number=league.current_pick
            )
            current_team.players.add(player)

            # Advance the draft
            league.current_pick += 1
            # if league.current_pick > league.total_picks:
            if league.current_pick > (total_teams * 15):
                league.draft_started = False
                league.save()
                return redirect('league_details', league_id=league.id)
            league.save()

    # Recalculate the current team for the updated state
    if league.current_pick <= league.total_picks:
        round_number = (league.current_pick - 1) // total_teams + 1
        direction = 'id' if round_number % 2 == 1 else '-id'
        teams = league.league_teams.order_by(direction)
        current_team_index = (league.current_pick - 1) % total_teams
        current_team = teams[current_team_index]
    else:
        current_team = None  # No current team after the draft ends

    # Get available players (not yet drafted)
    drafted_players = DraftPick.objects.filter(league=league).values_list('player_id', flat=True)
    available_players = Player.objects.exclude(id__in=drafted_players)

    # Categorize and sort players by position and points
    players_by_position = {
        "Goalkeepers": available_players.filter(position="Goalkeeper").order_by('-past_points'),
        "Defenders": available_players.filter(position="Defender").order_by('-past_points'),
        "Midfielders": available_players.filter(position="Midfielder").order_by('-past_points'),
        "Attackers": available_players.filter(position="Attacker").order_by('-past_points'),
    }

    context = {
        'league': league,
        'current_team': current_team,
        'players_by_position': players_by_position,
        'drafted_players': DraftPick.objects.filter(league=league).order_by('pick_number'),
    }

    return render(request, 'draft.html', context)

def calculate_points(goals, assists, saves, tackles, duels, position):
    # player = Player.objects.get(api_football_id=player_id)
    new_score = 0
    # position = player.position
    if position == "Goalkeeper":
        new_score += saves*0.5 + tackles*0.25 + duels*0.25
    elif position == "Defender":
        new_score += saves*0.15 + duels*0.3 + tackles*0.25 + goals*0.3
    elif position == "Midfielder":
        new_score += assists*0.3 + goals*0.3 + tackles*0.2 + duels*0.2
    elif position == "Attacker":
        new_score += assists*0.25 + goals*0.5 + tackles*0.15 + duels*0.1
    
    return new_score/2

def fetch_player_stats(player_id):
    """
    Fetch live stats for a player by their API ID and update the database if 6 hours have passed since the last update.
    """
    try:
        player = Player.objects.get(api_football_id=player_id)

        # Check if 6 hours have passed since the last update
        if player.last_updated and now() - player.last_updated < timedelta(hours=6):
            return {"success": False, "message": "Stats were recently updated. Try again later."}

        url = f"{API_URL}/players"
        params = {"id": player_id, "season": "2024"}  # Update the season dynamically as needed
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 200:
            data = response.json()
            stats = data['response'][0]['statistics'][0]

            # Calculate the difference in stats
            new_goals = stats["goals"]["total"] or 0 - player.last_goals
            new_assists = stats["goals"]["assists"] or 0 - player.last_assists
            new_tackles = stats["tackles"]["total"] or 0 - player.last_tackles
            new_saves = stats["goals"]["saves"] or 0 - player.last_saves
            new_duels = stats["duels"]["won"] or 0 - player.last_duels

            # Update stats only with the differences
            player.new_goals += max(0, new_goals)
            player.new_assists += max(0, new_assists)
            player.new_tackles += max(0, new_tackles)
            player.new_saves += max(0, new_saves)
            player.new_duels += max(0, new_duels)
            player.points += calculate_points(player.new_goals, player.new_assists, player.new_saves, player.new_tackles, player.new_duels, player.position)

            # Update the last known stats
            player.goals = stats["goals"]["total"] or 0
            player.assists = stats["goals"]["assists"] or 0
            player.tackles = stats["tackles"]["total"] or 0
            player.saves = stats["goals"]["saves"] or 0
            player.duels = stats["duels"]["won"] or 0
            player.past_points = calculate_points(player.goals, player.assists, player.saves, player.tackles, player.duels, player.position)

            # Update the last_updated timestamp
            player.last_updated = now()
            player.save()

            return {"success": True, "player": player.name, "updated_stats": stats}
        else:
            return {"success": False, "error": "API request failed."}
    except (KeyError, IndexError, Player.DoesNotExist):
        return {"success": False, "error": "Failed to update player stats."}


@login_required
def select_lineup(request):
    # This function allows users to set their lineups after drafting
    # league = get_object_or_404(League, id=league_id)

    # Checks if the user already has selected a team
    team, created = LeagueTeam.objects.get_or_create(user=request.user)

    # Filter players by those assigned to the user's team
    drafted_players = team.players.all()

    # Group players by position for better organization in the template
    players_by_position = {
        'Goalkeepers': drafted_players.filter(position='Goalkeeper').order_by('name'),
        'Defenders': drafted_players.filter(position='Defender').order_by('name'),
        'Midfielders': drafted_players.filter(position='Midfielder').order_by('name'),
        'Forwards': drafted_players.filter(position='Forward').order_by('name'),
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

        # Validate that all selected players belong to the user's drafted team
        players_selected = drafted_players.filter(id__in=player_ids)
        captain = drafted_players.filter(id=captain_id).first()

        if len(players_selected) != 11:
            if request.content_type == "application/json":
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

        # Save the selected lineup and captain
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


def fetch_past_player_points(player_id):
    player = Player.objects.get(api_football_id=player_id)
    return player.past_points

@login_required
def my_team_view(request):
    try:
        # Retrieve the user's team and its players
        team = LeagueTeam.objects.get(user=request.user)
        players = team.starting_lineup.all()  # Retrieve all players in the lineup
        captain = team.captain

        # Calculate total points including captain's bonus
        captain_points = (captain.past_points or 0) * 2 if captain else 0
        non_captain_points = sum(player.past_points for player in players if player != captain)
        total_points = captain_points + non_captain_points

        # Print debugging information for verification
        print("My Team:")
        for player in players:
            player.past_points = calculate_points(player.goals, player.assists, player.saves, player.tackles, player.duels, player.position)
            print(f"Player: {player.name}, Position: {player.position}, Points: {player.points}, Past Points: {player.past_points}")

    except LeagueTeam.DoesNotExist:
        # Handle case where the user does not have a team
        messages.error(request, "You haven't selected a team yet.")
        return redirect('select_lineup')

    context = {
        'team': team,
        'players': players,
        'captain': captain,
        'total_points': total_points,
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