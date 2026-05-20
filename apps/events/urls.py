from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('<int:event_id>/', views.event_detail, name='detail'),
    path('<int:event_id>/rsvp/', views.event_rsvp, name='rsvp'),
]
