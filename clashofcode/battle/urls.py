from django.urls import path
from . import views

urlpatterns = [
    path('queue/join/', views.join_queue, name='join_queue'),
    path('queue/leave/', views.leave_queue, name='leave_queue'),
    path('queue_status/', views.queue_status, name="queue_status"),
    path('battle_status/', views.battle_status, name= "battle_status")
    #path('battle/<str:battle_id>/', views.battle_detail, name='battle_page'),
]