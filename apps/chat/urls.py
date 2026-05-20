from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_index, name='index'),
    path('start/<int:user_id>/', views.start_conversation, name='start'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
]
