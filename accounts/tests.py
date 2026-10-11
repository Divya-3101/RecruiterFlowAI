from django.test import TestCase
from django.urls import reverse

from .models import User


class UserTests(TestCase):

    def test_user_creation(self):

        user = User.objects.create_user(
            username='testcandidate',
            email='test@example.com',
            password='Test@12345',
            role='candidate'
        )

        self.assertEqual(
            user.username,
            'testcandidate'
        )

        self.assertEqual(
            user.role,
            'candidate'
        )

        self.assertTrue(
            user.check_password('Test@12345')
        )


class AuthenticationTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username='candidate1',
            password='Test@12345',
            role='candidate'
        )

    def test_login_success(self):

        response = self.client.post(
            reverse('login'),
            {
                'username': 'candidate1',
                'password': 'Test@12345'
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

    def test_login_failure(self):

        response = self.client.post(
            reverse('login'),
            {
                'username': 'candidate1',
                'password': 'WrongPassword'
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )