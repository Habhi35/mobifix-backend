from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()

class AuthAPITestCase(APITestCase):
    def test_send_otp(self):
        url = reverse('send-otp')
        data = {
            'email': 'test@example.com',
            'phone': '1234567890'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(OTP.objects.filter(email='test@example.com').exists())

    def test_register_user_with_otp(self):
        # First create an OTP
        OTP.objects.create(email='test@example.com', phone='1234567890', otp='123456')
        
        url = reverse('register')
        data = {
            'email': 'test@example.com',
            'phone': '1234567890',
            'password': 'testpassword123',
            'otp': '123456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        # Ensure OTP was deleted
        self.assertFalse(OTP.objects.filter(email='test@example.com').exists())

    def test_login_user(self):
        # Create a user first
        user = User.objects.create_user(username='login@example.com', email='login@example.com', password='loginpassword123', phone='0987654321')
        
        url = reverse('login')
        data = {
            'email': 'login@example.com',
            'password': 'loginpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
