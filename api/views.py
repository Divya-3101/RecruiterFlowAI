from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from jobs.models import Job
from .serializers import ApplicationSerializer,JobSerializer
from .permissions import IsJobOwnerOrReadOnly

from applications.models import Application
from .serializers import ApplicationSerializer
from .permissions import IsCandidate, IsRecruiter


@permission_classes([IsAuthenticated])
class JobListAPI(APIView):

    permission_classes = [IsJobOwnerOrReadOnly]

    def get(self, request):

        jobs = Job.objects.all().order_by('-created_at')

        serializer = JobSerializer(
            jobs,
            many=True
        )

        return Response(serializer.data)

    def post(self, request):

        if request.user.role != 'recruiter':
            return Response(
                {
                    'error': 'Only recruiters can create jobs.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = JobSerializer(
            data=request.data
        )

        if serializer.is_valid():

            job = serializer.save(
                recruiter=request.user
            )

            return Response(
                JobSerializer(job).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class JobDetailAPI(APIView):

    permission_classes = [IsJobOwnerOrReadOnly]

    def get_object(self, job_id):

        try:
            return Job.objects.get(id=job_id)

        except Job.DoesNotExist:
            return None

    def get(self, request, job_id):

        job = self.get_object(job_id)

        if job is None:
            return Response(
                {'error': 'Job not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(
            request,
            job
        )

        serializer = JobSerializer(job)

        return Response(serializer.data)

    def put(self, request, job_id):

        job = self.get_object(job_id)

        if job is None:
            return Response(
                {'error': 'Job not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(
            request,
            job
        )

        serializer = JobSerializer(
            job,
            data=request.data
        )

        if serializer.is_valid():

            updated_job = serializer.save()

            return Response(
                JobSerializer(updated_job).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, job_id):

        job = self.get_object(job_id)

        if job is None:
            return Response(
                {'error': 'Job not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(
            request,
            job
        )

        job.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class ApplicationListAPI(APIView):

    permission_classes = [IsCandidate]

    def get(self, request):

        applications = Application.objects.filter(
            candidate=request.user
        ).select_related(
            'job'
        ).order_by('-applied_at')

        serializer = ApplicationSerializer(
            applications,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    def post(self, request):

        serializer = ApplicationSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():

            application = serializer.save(
                candidate=request.user
            )

            from applications.matching_service import evaluate_application
            evaluate_application(application)

            return Response(
                ApplicationSerializer(
                    application,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class RecruiterApplicationListAPI(APIView):

    permission_classes = [IsRecruiter]

    def get(self, request):

        applications = Application.objects.filter(
            job__recruiter=request.user
        ).select_related(
            'candidate',
            'job'
        ).order_by('-applied_at')

        serializer = ApplicationSerializer(
            applications,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

class ApplicationDetailAPI(APIView):

    def get_object(self, request, application_id):

        try:
            return Application.objects.select_related(
                'candidate',
                'job'
            ).get(
                id=application_id
            )

        except Application.DoesNotExist:
            return None

    def get(self, request, application_id):

        application = self.get_object(
            request,
            application_id
        )

        if application is None:

            return Response(
                {'error': 'Application not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user.role == 'candidate':

            if application.candidate != request.user:

                return Response(
                    {'error': 'You can only view your own application.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        elif request.user.role == 'recruiter':

            if application.job.recruiter != request.user:

                return Response(
                    {'error': 'You can only view applications for your jobs.'},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = ApplicationSerializer(
            application,
            context={'request': request}
        )

        return Response(serializer.data)

    def patch(self, request, application_id):

        application = self.get_object(
            request,
            application_id
        )

        if application is None:

            return Response(
                {'error': 'Application not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user.role != 'recruiter':

            return Response(
                {'error': 'Only recruiters can update status.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if application.job.recruiter != request.user:

            return Response(
                {'error': 'You cannot modify this application.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if set(request.data.keys()) - {'status'}:

            return Response(
                {'error': 'Only status can be updated.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ApplicationSerializer(
            application,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                ApplicationSerializer(
                    application,
                    context={'request': request}
                ).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class RecalculateAIMatchAPI(APIView):
    permission_classes = [IsRecruiter]

    def post(self, request, application_id):
        try:
            application = Application.objects.select_related('job', 'candidate').get(
                id=application_id,
                job__recruiter=request.user
            )
        except Application.DoesNotExist:
            return Response(
                {'error': 'Application not found or unauthorized.'},
                status=status.HTTP_404_NOT_FOUND
            )

        from applications.matching_service import evaluate_application
        result = evaluate_application(application)

        return Response({
            'message': 'AI match recalculated successfully.',
            'application': ApplicationSerializer(application, context={'request': request}).data,
            'result': result
        })


class APIRoot(APIView):

    def get(self, request):

        return Response({
            'message': 'Welcome to RecruiterFlowAI REST API',
            'endpoints': {
                'jobs': '/api/jobs/',
                'applications': '/api/applications/',
                'recruiter_applications': '/api/recruiter-applications/',
                'schema': '/api/schema/',
                'swagger_docs': '/api/docs/',
            }
        })