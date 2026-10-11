from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from .models import Job


class JobModelTests(TestCase):

    def setUp(self):

        self.recruiter = User.objects.create_user(
            username='recruiter1',
            password='Test@12345',
            role='recruiter'
        )

    def test_job_creation(self):

        job = Job.objects.create(
            recruiter=self.recruiter,
            title='Python Developer',
            company='ABC Technologies',
            location='Ahmedabad',
            salary=700000,
            description='Django developer required',
            required_skills='Python,Django,MySQL'
        )

        self.assertEqual(
            job.title,
            'Python Developer'
        )

        self.assertEqual(
            job.recruiter,
            self.recruiter
        )


class JobViewTests(TestCase):

    def setUp(self):

        self.recruiter = User.objects.create_user(
            username='recruiter1',
            password='Test@12345',
            role='recruiter'
        )

        self.client.login(
            username='recruiter1',
            password='Test@12345'
        )

    def test_create_job_page(self):

        response = self.client.get(
            reverse('create_job')
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_job_create(self):

        response = self.client.post(
            reverse('create_job'),
            {
                'title': 'Django Developer',
                'company': 'Tech Company',
                'location': 'Ahmedabad',
                'salary': 700000,
                'description': 'Django developer',
                'required_skills': 'Python,Django'
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertTrue(
            Job.objects.filter(
                title='Django Developer'
            ).exists()
        )