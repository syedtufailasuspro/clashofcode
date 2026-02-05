from django.urls import path
from . import views

urlpatterns = [
    path('run_code/', views.run_code, name='run_code'), 
    path('submit_code/', views.submit_code, name="submit_code"),   
]