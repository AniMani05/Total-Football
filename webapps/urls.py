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
from totalfootball.views import login_action, register_action, homepage_action, logout_action, profile_action

urlpatterns = [
    path('', login_action, name='home'),
    path('login', login_action, name="login"),
    path('register', register_action, name="register"),
    path('homepage', homepage_action, name="homepage"),
    path('logout', logout_action, name="logout"),
    path('profile/<int:user_id>', profile_action, name="profile")
]
