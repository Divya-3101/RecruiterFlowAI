from django.urls import path
from .views import *

urlpatterns = [
    path('create-job/', create_job, name='create_job'),
    path('jobs/', job_list, name='job_list'),
    path('update-job/<int:job_id>/', update_job, name='update_job'),
    path('delete-job/<int:job_id>/', delete_job, name='delete_job'),
]