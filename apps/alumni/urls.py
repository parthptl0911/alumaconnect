from django.urls import path
from . import views

app_name = 'alumni'

urlpatterns = [
    path('', views.alumni_list, name='alumni_list'),
]
