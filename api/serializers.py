from rest_framework import serializers
from applications.models import Application
from jobs.models import Job

class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job

        fields = [
            'id',
            'title',
            'company',
            'location',
            'salary',
            'description',
            'required_skills',
            'created_at',
            'recruiter',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'recruiter',
        ]

class ApplicationSerializer(
    serializers.ModelSerializer
):

    candidate_username = serializers.CharField(
        source='candidate.username',
        read_only=True
    )

    job_title = serializers.CharField(
        source='job.title',
        read_only=True
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:

        model = Application

        fields = [
            'id',
            'candidate',
            'candidate_username',
            'job',
            'job_title',
            'cover_letter',
            'resume',
            'status',
            'status_display',
            'semantic_score',
            'skill_score',
            'final_score',
            'matched_skills',
            'missing_skills',
            'applied_at'
        ]

        read_only_fields = [
            'id',
            'candidate',
            'candidate_username',
            'job_title',
            'status',
            'status_display',
            'semantic_score',
            'skill_score',
            'final_score',
            'matched_skills',
            'missing_skills',
            'applied_at'
        ]

    def validate(self, data):

        request = self.context['request']

        job = data.get('job')

        if job.recruiter == request.user:
            raise serializers.ValidationError(
                "You cannot apply to your own job."
            )

        if Application.objects.filter(
            candidate=request.user,
            job=job
        ).exists():

            raise serializers.ValidationError(
                "You have already applied for this job."
            )

        return data