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

def homepage_action(request):
    # Get top players ordered by points
    top_players = Player.objects.order_by('-points')[:10]

    # Prepare team points data
    teams = Team.objects.all()
    team_points = []

    for team in teams:
        captain_points = 0
        non_captain_points = 0
        
        # Calculate captain points, doubled if captain exists
        if team.captain:
            captain_points = (team.captain.points or 0) * 2  # Default to 0 if points are None
        
        # Sum points for non-captain players, defaulting to 0 if None
        non_captain_points = team.players.exclude(id=team.captain_id).aggregate(
            total=Sum('points')
        )['total'] or 0

        # Calculate total points
        total_points = captain_points + non_captain_points

        # Add team data to list
        team_points.append({
            'username': team.user.username,
            'total_points': total_points,
        })

    # Sort teams by total_points in descending order and select top 10
    top_users = sorted(team_points, key=lambda x: x['total_points'], reverse=True)[:10]

    context = {
        'top_players': top_players,
        'top_users': top_users,
    }

    return render(request, 'homepage.html', context)

def login_action(request):
    # If the user is already authenticated, redirect to the homepage.
    if request.user.is_authenticated:
        return redirect('homepage')

    context = {}

    # If the request is a GET, display the login form.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'start.html', context)

    # Creates a bound form with POST data.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validate the form data.
    if not form.is_valid():
        return render(request, 'start.html', context)

    # Authenticate the user.
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    new_user = authenticate(username=username, password=password)

    # If authentication fails, return an error message.
    if new_user is None:
        messages.error(request, "Invalid username or password.")
        return render(request, 'start.html', context)

    # Log the user in and redirect to the homepage.
    login(request, new_user)
    return redirect('homepage')

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        print("Returning form")
        return render(request, 'register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'register.html', context)
    
    if form.cleaned_data['password1'] != form.cleaned_data['password2']:
        context['error'] = 'Passwords do not match.'
        print("Password error")
        return render(request, 'register.html', context)

    # At this point, the form data is valid.  Register and login the user.
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
    # Ensure the team exists for the user
    team, created = Team.objects.get_or_create(user=request.user)

    # Group players by position
    players_by_position = {
        'Goalkeepers': Player.objects.filter(position='Goalkeeper').order_by('name'),
        'Defenders': Player.objects.filter(position='Defender').order_by('name'),
        'Midfielders': Player.objects.filter(position='Midfielder').order_by('name'),
        'Forwards': Player.objects.filter(position='Forward').order_by('name'),
    }

    # Check if the request is JSON or form-encoded
    if request.method == "POST":
        if request.content_type == "application/json":
            # Parse JSON data
            data = json.loads(request.body)
            player_ids = data.get('players')
            captain_id = data.get('captain_id')
        else:
            # Handle form-encoded data as before
            player_ids = request.POST.getlist('players')
            captain_id = request.POST.get('captain')

        # Validate the provided player IDs and captain ID
        if not player_ids or not captain_id:
            if request.content_type == "application/json":
                return JsonResponse({'error': "You must select players and a captain."}, status=400)
            else:
                messages.error(request, "You must select players and a captain.")
                return redirect('select_lineup')

        players_selected = Player.objects.filter(id__in=player_ids)
        captain = Player.objects.filter(id=captain_id).first()

        # Validate the lineup
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

        # Save the lineup and captain
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

@login_required
def my_team_view(request):
    try:
        team = Team.objects.get(user=request.user)
        players = team.starting_lineup.all()
        captain = team.captain
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
            
            # Add the creator to the league's members
            league.members.add(request.user)
            
            # Create a LeagueTeam for the creator in this new league
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
                
                # Add the user to the league's members if not already a member
                if request.user not in league.members.all():
                    league.members.add(request.user)
                
                # Check if the user already has a team in this league
                league_team, created = LeagueTeam.objects.get_or_create(user=request.user, league=league)
                
                # Redirect to the league details page
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