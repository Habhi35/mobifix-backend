from django.shortcuts import render
import random
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from .serializers import UserSerializer, RegisterSerializer, OTPSerializer
from .models import OTP

User = get_user_model()

# Accounts Root API
class AccountsRootAPI(APIView):
    def get(self, request):
        return Response({
            "endpoints": {
                "send-otp": "/api/accounts/send-otp/",
                "register": "/api/accounts/register/",
                "login": "/api/accounts/login/"
            }
        })

# Send OTP API
class SendOTPAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone')
        
        # Generate a 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Save OTP to database
        otp_record = OTP.objects.create(email=email, phone=phone, otp=otp_code)
        
        # In a real app, send the OTP via SMS or Email here.
        print(f"DEBUG: Generated OTP for {email or phone}: {otp_code}")
        
        return Response({
            "message": "OTP sent successfully."
        }, status=status.HTTP_200_OK)

# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        phone = serializer.validated_data.get('phone')
        provided_otp = serializer.validated_data.get('otp')
        
        # Verify OTP
        # We find the latest OTP for this exact email and phone
        otp_record = OTP.objects.filter(email=email, phone=phone).order_by('-created_at').first()
        
        if not otp_record or otp_record.otp != provided_otp:
            return Response({"error": "Invalid or missing OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check OTP expiration (e.g., 5 minutes)
        if (timezone.now() - otp_record.created_at).total_seconds() > 300:
             return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
             
        user = serializer.save()
        
        # Cleanup used OTP
        otp_record.delete()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

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
