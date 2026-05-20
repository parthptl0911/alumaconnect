from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.stories_list, name='stories_list'),
    path('<int:story_id>/', views.story_detail, name='detail'),
    path('submit/', views.submit_story, name='submit'),
    path('edit/<int:story_id>/', views.edit_story, name='edit_story'),
    path('delete/<int:story_id>/', views.delete_story, name='delete'),
]
