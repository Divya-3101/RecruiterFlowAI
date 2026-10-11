from django.urls import path
from .views import *
urlpatterns = [
    path('apply/<int:job_id>/',apply_job,name='apply_job'),
    path('recruiter-applications/',recruiter_applications,name='recruiter_applications'),
    path('dashboard/',dashboard,name='dashboard'),
    path('application/<int:application_id>/status/',update_application_status,name='update_application_status'),
    path('my-applications/',my_applications,name='my_applications'),
    path('save-job/<int:job_id>/',save_job,name='save_job'),
    path('my-saved-jobs/',my_saved_jobs,name='my_saved_jobs'),
    path('candidate-dashboard/',candidate_dashboard,name='candidate_dashboard'),
    path('application/<int:application_id>/recalculate/',recalculate_ai_match,name='recalculate_ai_match'),
    path('application/<int:application_id>/',application_detail,name='application_detail'),
]