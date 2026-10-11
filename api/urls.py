from django.urls import path
from .views import (
    APIRoot,
    JobListAPI,
    JobDetailAPI,
    ApplicationListAPI,
    ApplicationDetailAPI,
    RecruiterApplicationListAPI,
    RecalculateAIMatchAPI,
)

urlpatterns = [
    path('jobs/', JobListAPI.as_view(), name='job_list_api'),
    path('jobs/<int:job_id>/', JobDetailAPI.as_view(), name='job_detail_api'),
    path('applications/', ApplicationListAPI.as_view(), name='application_list_api'),
    path('recruiter-applications/', RecruiterApplicationListAPI.as_view(), name='recruiter_application_list_api'),
    path('applications/<int:application_id>/', ApplicationDetailAPI.as_view(), name='application_detail_api'),
    path('applications/<int:application_id>/recalculate/', RecalculateAIMatchAPI.as_view(), name='api_recalculate_ai_match'),
    path('', APIRoot.as_view(), name='api_root'),
]