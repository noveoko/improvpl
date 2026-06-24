from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events_list, name='events_list'),
    path('events/<int:event_id>/register/', views.event_register, name='event_register'),
    path('events/<int:event_id>/notify/', views.jam_notify, name='jam_notify'),
    path('polls/', views.polls_list, name='polls_list'),
]