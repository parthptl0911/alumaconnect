from django.urls import path
from . import views

app_name = 'fundraising'

urlpatterns = [
    path('', views.fundraising_list, name='list'),
    path('campaign/<int:campaign_id>/', views.campaign_detail, name='detail'),
    path('campaign/<int:campaign_id>/initiate/', views.initiate_donation, name='initiate_donation'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
]
