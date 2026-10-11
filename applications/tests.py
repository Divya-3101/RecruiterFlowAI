from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from jobs.models import Job
from .models import Application, SavedJob


class ApplicationTests(TestCase):

    def setUp(self):

        self.recruiter = User.objects.create_user(
            username='recruiter1',
            password='Test@12345',
            role='recruiter'
        )

        self.candidate = User.objects.create_user(
            username='candidate1',
            password='Test@12345',
            role='candidate'
        )

        self.job = Job.objects.create(
            recruiter=self.recruiter,
            title='Python Developer',
            company='ABC Technologies',
            location='Ahmedabad',
            salary=700000,
            description='Python developer',
            required_skills='Python,Django,MySQL'
        )

        self.client.login(
            username='candidate1',
            password='Test@12345'
        )

    def test_application_creation(self):

        application = Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            cover_letter='I am interested.',
            resume='applications/test.pdf'
        )

        self.assertEqual(
            application.status,
            'applied'
        )

        self.assertEqual(
            application.candidate,
            self.candidate
        )

        self.assertEqual(
            application.job,
            self.job
        )

    def test_duplicate_application_blocked(self):

        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            cover_letter='First application',
            resume='applications/test.pdf'
        )

        with self.assertRaises(Exception):

            Application.objects.create(
                candidate=self.candidate,
                job=self.job,
                cover_letter='Second application',
                resume='applications/test2.pdf'
            )

    def test_save_job(self):

        saved = SavedJob.objects.create(
            user=self.candidate,
            job=self.job
        )

        self.assertEqual(
            saved.job,
            self.job
        )

    def test_saved_job_duplicate_blocked(self):

        SavedJob.objects.create(
            user=self.candidate,
            job=self.job
        )

        with self.assertRaises(Exception):

            SavedJob.objects.create(
                user=self.candidate,
                job=self.job
            )

class RolePermissionTests(TestCase):

    def setUp(self):

        self.recruiter = User.objects.create_user(
            username='recruiter1',
            password='Test@12345',
            role='recruiter'
        )

        self.candidate = User.objects.create_user(
            username='candidate1',
            password='Test@12345',
            role='candidate'
        )

        self.job = Job.objects.create(
            recruiter=self.recruiter,
            title='Python Developer',
            company='ABC',
            location='Ahmedabad',
            salary=700000,
            description='Python job',
            required_skills='Python,Django'
        )

    def test_candidate_cannot_create_job(self):

        self.client.login(
            username='candidate1',
            password='Test@12345'
        )

        response = self.client.get(
            reverse('create_job')
        )

        self.assertNotEqual(
            response.status_code,
            200
        )

    def test_recruiter_can_create_job_page(self):

        self.client.login(
            username='recruiter1',
            password='Test@12345'
        )

        response = self.client.get(
            reverse('create_job')
        )

        self.assertEqual(
            response.status_code,
            200
        )


class AIMatcherAndServiceTests(TestCase):

    def test_job_skills_list(self):
        recruiter = User.objects.create_user(
            username='recruiter_test',
            password='Password@123',
            role='recruiter'
        )
        job = Job.objects.create(
            recruiter=recruiter,
            title='Full Stack Developer',
            company='InnoTech',
            location='Remote',
            salary=900000,
            description='Web app developer',
            required_skills='Python, Django; React, PostgreSQL'
        )
        skills = job.get_skills_list()
        self.assertIn('Python', skills)
        self.assertIn('Django', skills)
        self.assertIn('React', skills)
        self.assertIn('PostgreSQL', skills)

    def test_skill_matcher_with_aliases(self):
        from applications.skill_matcher import calculate_resume_match
        resume_text = "Experienced in python, js, reactjs, and postgres database design."
        result = calculate_resume_match(
            resume_text=resume_text,
            candidate_skills="FastAPI",
            required_skills="Python, JavaScript, React, PostgreSQL, Docker"
        )
        self.assertGreaterEqual(result["score"], 60.0)
        self.assertIn("python", result["matched_skills"])
        self.assertIn("javascript", result["matched_skills"])
        self.assertIn("docker", result["missing_skills"])

    def test_fallback_semantic_score(self):
        from applications.ai_matcher import fallback_text_similarity
        score = fallback_text_similarity(
            "Experienced Django developer with REST API experience",
            "Looking for backend developer skilled in Django and REST APIs"
        )
        self.assertGreater(score, 0.4)