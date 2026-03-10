from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()

class AuthAPITestCase(APITestCase):
    def test_register_and_verify_flow(self):
        # 1. Register User (creates inactive user and sends OTP)
        register_url = reverse('register')
        register_data = {
            'email': 'test@example.com',
            'phone': '1234567890',
            'password': 'testpassword123'
        }
        res_register = self.client.post(register_url, register_data, format='json')
        self.assertEqual(res_register.status_code, status.HTTP_201_CREATED)
        self.assertIn('OTP sent successfully', res_register.data['message'])
        self.assertIn('otp', res_register.data)
        
        # Verify user was created but is inactive
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)
        
        # Get the generated OTP from the database
        otp_record = OTP.objects.get(email='test@example.com')
        
        # 2. Try to login while inactive (should fail)
        login_url = reverse('login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        res_login_inactive = self.client.post(login_url, login_data, format='json')
        self.assertEqual(res_login_inactive.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 3. Verify OTP (activates user)
        verify_url = reverse('verify-otp')
        verify_data = {
            'otp': otp_record.otp
        }
        res_verify = self.client.post(verify_url, verify_data, format='json')
        self.assertEqual(res_verify.status_code, status.HTTP_200_OK)
        self.assertIn('access', res_verify.data)
        self.assertIn('refresh', res_verify.data)
        self.assertIn('user', res_verify.data)
        self.assertEqual(res_verify.data['user']['email'], 'test@example.com')
        
        # Verify user is now active and OTP is deleted
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertFalse(OTP.objects.filter(email='test@example.com').exists())

    def test_login_user(self):
        # Create an active user first
        user = User.objects.create_user(username='login@example.com', email='login@example.com', password='loginpassword123', phone='0987654321')
        user.is_active = True
        user.save()
        
        url = reverse('login')
        data = {
            'email': 'login@example.com',
            'password': 'loginpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
