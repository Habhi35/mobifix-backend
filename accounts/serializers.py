from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'], # use email as username
            phone=validated_data['phone'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        # Setting user as inactive until OTP is verified
        user.is_active = False
        user.save()
        return user

class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, required=True)

    def validate_otp(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError("OTP must be exactly 6 digits.")
        return value
