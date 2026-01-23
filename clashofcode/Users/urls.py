from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("login_user", views.login_user, name= "login"),
    path("signup_user", views.signup_user, name= "signup"),
]
