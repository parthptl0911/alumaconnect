from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    path('', views.index, name='index'),
    path('request/<int:mentor_id>/', views.send_request, name='send_request'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request'),
    path('delete/<int:request_id>/', views.delete_mentorship, name='delete'),
]
