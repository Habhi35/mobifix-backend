from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'phone', 'email', 'password', 'otp')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data.pop('otp')  # remove otp from validated_data before creating user
        user = User.objects.create_user(
            username=validated_data['email'], # use email as username
            phone=validated_data['phone'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=15, required=False)

    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError("Either email or phone is required")
        return data
