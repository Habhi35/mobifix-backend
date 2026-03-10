from django.shortcuts import render
import random
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from .serializers import UserSerializer, RegisterSerializer, VerifyOTPSerializer
from .models import OTP

User = get_user_model()

# Accounts Root API
class AccountsRootAPI(APIView):
    def get(self, request):
        return Response({
            "endpoints": {
                "register": "/api/accounts/register/",
                "verify-otp": "/api/accounts/verify-otp/",
                "login": "/api/accounts/login/"
            }
        })

# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        # 1. Create the inactive user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        email = user.email
        phone = user.phone
        
        # 2. Generate a 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # 3. Save OTP to database
        otp_record = OTP.objects.create(email=email, phone=phone, otp=otp_code)
        
        # In a real app, send the OTP via SMS or Email here.
        print(f"DEBUG: Generated OTP for newly registered user {email}: {otp_code}")
        
        return Response({
            "message": "User registered securely. OTP sent successfully to your mobile number.",
        }, status=status.HTTP_201_CREATED)

# Verify OTP API
class VerifyOTPAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provided_otp = serializer.validated_data.get('otp')
        
        # Verify OTP is correct and exists
        otp_record = OTP.objects.filter(otp=provided_otp).order_by('-created_at').first()
        
        if not otp_record:
            return Response({"error": "Invalid or missing OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check OTP expiration (e.g., 5 minutes)
        if (timezone.now() - otp_record.created_at).total_seconds() > 300:
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
             
        # Activate the associated user
        try:
            user = User.objects.get(email=otp_record.email, phone=otp_record.phone)
        except User.DoesNotExist:
             return Response({"error": "User for this OTP not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user.is_active = True
        user.save()
        
        # Cleanup used OTP
        otp_record.delete()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

# Login API
class LoginAPI(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({"error": "Please provide both email and password"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Authenticate using email
        user = authenticate(username=email, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
