from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password','balance']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"https://phimart-hotel-server.onrender.com/api/accounts/activate/{uid}/{token}/"
        send_mail('Activate your account', f'Click on this url to verify your account or copy and paste it to your browser: {activation_link}', 'noreply@hotelbooking.com', [user.email])
        return user
    
class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username',  'password']
        extra_kwargs = {'password': {'write_only': True}}

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
