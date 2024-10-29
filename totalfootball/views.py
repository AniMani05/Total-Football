from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.contrib import messages


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import User, Player, Team
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, ProfileForm, LineupSelectionForm

def homepage_action(request):
    return render(request, "homepage.html")

def login_action(request):
    if request.user.is_authenticated:
        return render (request, "homepage.html")

    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'start.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'start.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('homepage'))

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

    if request.method == "POST":
        # Extract player and captain IDs from POST data
        player_ids = request.POST.getlist('players')
        captain_id = request.POST.get('captain')

        # Ensure player IDs and captain ID are valid
        if not player_ids or not captain_id:
            messages.error(request, "You must select players and a captain.")
            return redirect('select_lineup')

        players_selected = Player.objects.filter(player_id__in=player_ids)
        captain = Player.objects.filter(player_id=captain_id).first()

        # Validate the lineup
        if len(players_selected) != 11:
            messages.error(request, "You must select exactly 11 players.")
            return redirect('select_lineup')

        if not captain or captain not in players_selected:
            messages.error(request, "The captain must be one of the selected players.")
            return redirect('select_lineup')

        # Save the lineup and captain
        team.starting_lineup.set(players_selected)
        team.captain = captain
        team.save()

        messages.success(request, "Your lineup has been saved successfully!")
        return redirect('homepage')

    context = {
        'players_by_position': players_by_position,
    }

    return render(request, 'select_lineup.html', context)