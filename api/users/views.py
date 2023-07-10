import uuid
import requests

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.middleware import csrf
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException

from . import serializers
from .utils import check_password_strength

from api.permissions import IsAccountOwner, IsNotAuthenticated
from api.users.exceptions import PasswordsDoNotMatch, WrongToken, PasswordTooWeak
from vegan_recipes.settings import EMAIL_HOST_USER
from users.models import Profile


class CreateUserView(generics.CreateAPIView):
    """
    Registration form
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserRegisterSerializer
    permission_classes = [IsNotAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        user = authenticate(
            username=request.data['username'], password=request.data['password']
        )
        login(request, user)
        # Url to send mail with email confirmation api
        url_path = reverse('send-mail-confirm-email')
        full_url = request.scheme + '://' + request.get_host() + url_path

        session_id = request.session.session_key
        headers = {
            'Cookie': f'sessionid={session_id}',
            'X-CSRFToken': csrf.get_token(request),
        }
        r = requests.get(full_url, headers=headers)

        return response


class ListUserView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'


class RetrieveUpdateDestroyUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserDetailSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    lookup_url_kwarg = 'username'

    def get_permissions(self):
        """
        Ensure that user who's not the owner of this account can't make
        any changes to it
        """
        permission_classes = []
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            permission_classes = [IsAccountOwner]
        return [permission() for permission in permission_classes]


class ChangePasswordView(APIView):
    """
    Change the current user's password by getting the current password and a new password
    """
    serializer_class = serializers.ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user

        if not user.check_password(data['current_password']):
            raise ValidationError("The current password is invalid.")

        if data['new_password'] != data['repeat_new_password']:
            raise PasswordsDoNotMatch()

        if check_password_strength(data['new_password']) == 'Weak':
            raise PasswordTooWeak()

        user.set_password(data['new_password'])
        user.save()

        return Response(
            data={"detail": "Password has been successfully updated!"},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    """
    Sends a message with a link with the valid token on the user's email
    typed by them in the form
    """
    serializer_class = serializers.EmailSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=user_email)
        except:
            return Response(
                data={
                    'detail': "User with given email address does not exist!",
                    'code': 'user_with_email_doesnotexist',
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Token needed for password reseting process
        token = uuid.uuid4().__str__()

        # Url from where user can complete reseting their password
        url_path = reverse('reset-password-complete', args=[token])
        full_url = request.scheme + '://' + request.get_host() + url_path

        # Token expires after one hour
        cache.set(token, user.pk, 3600)

        subject = "Reset your password on veganrecipes.com"
        message = f"Click on this link to reset your password: {full_url}"

        send_mail(subject, message, EMAIL_HOST_USER, [user_email], fail_silently=False)

        return Response(
            data={
                'detail': "Email with further instructions was succesfully sent!",
                'code': 'email_sent',
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordComplete(APIView):
    """
    Shows the form to enter new password after clicking the link sent on the email 
    of the user who forgot their password with the valid token
    """
    serializer_class = serializers.NewPasswordSerializer

    def post(self, request, token, format=None):
        user_pk = cache.get(token)

        if not user_pk:
            raise WrongToken()

        cache.delete(token)

        user = get_object_or_404(User, pk=user_pk)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        if data['new_password'] != data['repeat_new_password']:
            raise PasswordsDoNotMatch()

        if check_password_strength(data['new_password']) == 'Weak':
            raise PasswordTooWeak()

        user.set_password(data['new_password'])
        user.save()

        return Response(
            data={
                'detail': "Password has been successfully updated!",
                'code': 'password_updated',
            },
            status=status.HTTP_200_OK,
        )


class CheckPasswordStrength(APIView):
    """
    View constructed for checking password strength in real time,
    e.g. while typing
    """

    serializer_class = serializers.PasswordSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']

        password_strength = check_password_strength(password)
        return Response(
            data={'strength': password_strength},
            status=status.HTTP_200_OK,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def send_msg_confirm_email(request):
    """
    Sends a link with the token to confirm user's password with the next view
    """
    if request.user.profile.email_confirmed:
        return Response(
            data={
                'detail': "This email was already confirmed",
                'code': 'email_already_confirmed',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_email = request.user.email

    token = uuid.uuid4().__str__()
    cache.set(token, request.user.pk, 3600)

    # Url by which clicking user will confirm their email
    url_path = reverse('confirm-email', args=[token])
    full_url = request.scheme + '://' + request.get_host() + url_path

    title = "Confirm your email"
    subject = f"Confirm your email by clicking this link: {full_url}"

    send_mail(title, subject, EMAIL_HOST_USER, [user_email])

    return Response(
        data={'detail': "Message with link for the email confirmation was sent"},
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
def confirm_email(request, token):
    """
    Confirm user's password just by clicking the link sent with the previous view    
    """
    if not cache.get(token):
        raise WrongToken()

    user_pk = cache.get(token)
    cache.delete(token)
    user = get_object_or_404(User, pk=user_pk)

    user.profile.email_confirmed = True
    user.profile.save()

    return Response(
        data={'detail': "The email was confirmed!", 'code': 'email_confirmed'},
        status=status.HTTP_200_OK,
    )
