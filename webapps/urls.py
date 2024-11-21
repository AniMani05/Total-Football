"""
URL configuration for webapps project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from totalfootball.views import get_all_player_ids, update_player_stats, draft_view, login_action, register_action, homepage_action, logout_action, profile_action, get_profile_picture, select_lineup, my_team_view, create_league, join_league, league_details

urlpatterns = [
    path('', login_action, name='home'),
    path('login', login_action, name="login"),
    path('register', register_action, name="register"),
    path('homepage', homepage_action, name="homepage"),
    path('logout', logout_action, name="logout"),
    path('profile/<int:user_id>', profile_action, name="profile"),
    path('photo/<int:user_id>/', get_profile_picture, name="photo"),
    path('select-lineup/', select_lineup, name='select_lineup'),
    path('my-team/', my_team_view, name='my_team'),
    path('create-league/', create_league, name='create_league'),
    path('join-league/', join_league, name='join_league'),
    path('league/<int:league_id>/', league_details, name='league_details'),
    path('draft/<int:league_id>/', draft_view, name='draft'),
    path('update-stats/<int:player_id>/', update_player_stats, name='update_player_stats'),
    path('get-all-player-ids/', get_all_player_ids, name='get_all_player_ids')
]
