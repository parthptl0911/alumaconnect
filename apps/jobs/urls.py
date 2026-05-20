from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.jobs_list, name='jobs_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('post/', views.post_job, name='post_job'),
    path('edit/<int:job_id>/', views.edit_job, name='edit_job'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('<int:job_id>/applicants/', views.manage_applicants, name='manage_applicants'),
    path('application/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    path('delete/<int:job_id>/', views.delete_job, name='delete'),
]
