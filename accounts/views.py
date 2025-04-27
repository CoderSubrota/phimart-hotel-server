from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from rest_framework import permissions
from .serializers import RegisterSerializer,LoginSerializer,PasswordResetSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from rest_framework import generics
from django.utils.encoding import  force_str
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.utils.html import format_html

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    

class ActivateUserView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponse(
                format_html(
                    """
                    <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border: 1px solid #f5c6cb; border-radius: 4px;">
                        Invalid activation link
                    </div>
                    """
                ),
                status=status.HTTP_400_BAD_REQUEST
            )

        if user is not None and default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                if hasattr(user, 'is_verified'):
                    user.is_verified = True
                user.save()
                success_message = """
                    <div style="background-color: #d4edda; color: #155724; padding: 15px; border: 1px solid #c3e6cb; border-radius: 4px;">
                        Account activated successfully! <br><br>
                        <a href="http://localhost:3000/login" style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">Login Now</a>
                    </div>
                """
                return HttpResponse(format_html(success_message), status=status.HTTP_200_OK)
            else:
                already_activated_message = """
                    <div style="background-color: #cce5ff; color: #004085; padding: 15px; border: 1px solid #b8daff; border-radius: 4px;">
                        Your account is already activated. <br><br>
                        <a href="http://localhost:3000/login" style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">Login Now</a>
                    </div>
                """
                return HttpResponse(format_html(already_activated_message), status=status.HTTP_200_OK)

        return HttpResponse(
            format_html(
                """
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border: 1px solid #f5c6cb; border-radius: 4px;">
                    Invalid or expired token
                </div>
                """
            ),
            status=status.HTTP_400_BAD_REQUEST
        )
        
class VerifyTokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Token is valid", "user": str(request.user)})
    

class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if username is None or password is None:
            return Response(
                {'error': 'Please provide both username and password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)
        
        # Determine the role of the user
        if user.is_superuser:
            role = 'admin'
        elif user.is_staff:
            role = 'staff'
        else:
            role = 'normal user'

        return Response(
            {
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'balance': user.balance,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': role,  
            },
            status=status.HTTP_200_OK
        )
        
class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        form = PasswordResetForm(data=request.data)
        if not form.is_valid():
            return Response({"error": "Please enter a valid email."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=form.cleaned_data['email']).first()
        if user:
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            path = reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            reset_link = request.build_absolute_uri(path)

            # Sending email
            send_mail(
                subject="Password Reset Request",
                message=f"Hello {user.username},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, please ignore it.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response({"message": "If that email exists, we’ve sent a link."})

class PasswordResetConfirmAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = kwargs.get('uidb64')
        token = kwargs.get('token')

        if not uidb64 or not token:
            return Response(
                {"error": "Missing uid or token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Now decode & validate exactly as before:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid user identifier."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )

        form = SetPasswordForm(user, data=request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        form.save()
        return Response({"message": "Password has been reset successfully."})
