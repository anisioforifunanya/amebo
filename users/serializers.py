from rest_framework import serializers, exceptions
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from decouple import config
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
import django.contrib.auth.password_validation as validators
from django.contrib.auth.tokens import default_token_generator
from ameboConfig.common import CustomValidationError
from django.contrib.auth.hashers import check_password
import hashlib


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(style={"input_type": 'password'})

    def get_auth_user(self, email, password):
        # get the user from the db, then authenticate
        if email:
            try:
                user = User.objects.get(email__iexact=email.lower())
            except User.DoesNotExist:
                user = None
            if user is not None:
                return authenticate(self.context['request'], email=email.lower(), password=password)
        return None

    @staticmethod
    def is_user_active_or_not(user):
        if not user.is_active:
            message = _('User account has been disabled')
            raise exceptions.ValidationError(message)

    # validate method to get the inputted email and password
    def validate(self, attrs):
        email, password = attrs.get('email', None).lower(), attrs.get('password', None)
        user = self.get_auth_user(email, password)
        if not user:
            message = _('Unable to login with the provided credentials')
            raise exceptions.ValidationError(message)

        # check if the user account is active or not
        self.is_user_active_or_not(user)

        attrs['user'] = user
        return attrs

class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=500, required=True)

    def create(self, validated_data):
        refresh = validated_data.get('refresh_token')
        try:
            # generate a new access token using the refresh token
            refresh_token = RefreshToken(refresh)
            access_token = str(refresh_token.access_token)
            return access_token
        except Exception as e:
            raise Exception(str(e))

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    display_name = serializers.CharField(max_length=255, required=True)
    gender = serializers.CharField(max_length=255, required=True)
    phone_number = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(style={"input_type": 'password'})
    confirm_password = serializers.CharField(style={"input_type": 'password'})

    def validate(self, data):
        # validate the given password
        password, confirm_password = data.get('password'), data.get('confirm_password')
        try:
            validators.validate_password(password=password)
            # check if password and confirm_password are the same
        except Exception as e:
            error = CustomValidationError(e)
            raise Exception(error)

        if password != confirm_password:
            raise Exception("Invalid input, your passwords do not match")
        return super(RegistrationSerializer, self).validate(data)

class UserSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        validated_data.pop("password", None)
        validated_data.pop("email", None)
        return super().update(instance, validated_data)

    class Meta:
        model = User
        exclude = ['first_name', 'last_name', 'recent_passwords']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['date_joined', 'groups', 'user_permissions', 'last_login', 'is_active', 'is_superuser']


class AppUsersSerializer(serializers.ModelSerializer):
    email_address = serializers.SerializerMethodField()
    followed_username = serializers.CharField(max_length=500, required=False)
    unfollowed_username = serializers.CharField(max_length=500, required=False)

    def get_email_address(self, obj):
        # return the email address of the user
        return obj.owner.email

    def update(self, instance, validated_data):
        with transaction.atomic():
            # get the just followed user, and add the user's following
            followed_username = validated_data.get("followed_username")
            unfollowed_username = validated_data.get("unfollowed_username")
            if followed_username:
                if followed_username not in instance.following:
                    instance.following.append(followed_username)
                # now add the user to the list of that "followed_username" followers
                followed_user = AppUsers.objects.filter(username=followed_username).first()
                followed_user.followers.append(instance.username)
                followed_user.save()

            if unfollowed_username:
                if unfollowed_username in instance.following:
                    instance.following.remove(unfollowed_username)
                # now remove the user from the list of that "unfollowed_username" followers
                unfollowed_user = AppUsers.objects.filter(username=unfollowed_username).first()
                unfollowed_user.followers.remove(instance.username)
                unfollowed_user.save()
            return super().update(instance, validated_data)

    class Meta:
        model = AppUsers
        fields = '__all__'


class ForgetPasswordSerializer(serializers.Serializer):
    # takes the email address of the user, creates a token
    # then send a url to reset the password
    email = serializers.EmailField(max_length=255, required=True)

    def create(self, validated_data):
        try:
            # validate the given email if it exists or not
            email = validated_data.get('email')
            user = User.objects.filter(email__iexact=email).first()
            if not email:
                raise Exception("Email address not provided, enter a valid email address")
            # check if the email exists in db
            if not user:
                raise Exception("Invalid input, email address does not exist")
            # create the user token
            token = default_token_generator.make_token(user)
            # save the token to db
            ResetPasswordTokens.objects.create(user=user, token=token)
            # f"http://localhost:3000/auth/reset-password?id={user.id}&token={token}"
            print('..--..', user.id, token)
            return validated_data
        except Exception as e:
            return ValidationError(message=str(e))

class PasswordForgetSerializer(serializers.Serializer):
    # it takes the generated token, email address and new password of the user
    user_id = serializers.CharField(max_length=255, required=True)
    token = serializers.CharField(max_length=500, required=True)
    password = serializers.CharField(style={"input_type": 'password'})
    confirm_password = serializers.CharField(style={"input_type": 'password'})

    def validate(self, data):
        # validate the given password
        password, confirm_password = data.get('password'), data.get('confirm_password')
        try:
            validators.validate_password(password=password)
            # check if password and confirm_password are the same
        except Exception as e:
            error = CustomValidationError(e)
            raise Exception(error)

        if password != confirm_password:
            raise Exception("The new password and confirm password do not match")
        return super(PasswordForgetSerializer, self).validate(data)

    def create(self, validated_data):
        # validate the given token with the respective user
        user_id, token, password = validated_data.get('user_id'), validated_data.get('token'), validated_data.get('password')
        user = User.objects.filter(id=user_id).first()
        # check if the email exists in db
        if not user:
            raise ValidationError("User not found")
        if not default_token_generator.check_token(user, token):
            raise ValidationError("Token is invalid or has expired, kindly request for another reset linK")

        # encode new password
        encode_password = password.encode()
        # hash new password
        hash_password = hashlib.sha256(encode_password).hexdigest()
        # Check if new password is different from the last three passwords
        if hash_password in user.recent_passwords:
            raise Exception('Kindly change the new password, as it has been previously used.')
        else:
            # Remove redundant password if the password list contains more than three passwords
            if len(user.recent_passwords) == 3:
                user.recent_passwords.pop(0)
            user.recent_passwords.append(hash_password)  # add the new password to the list of recent passwords
        user.set_password(password)  # Set new password for the user
        user.save()
        # delete the token after it has been used
        used_token = ResetPasswordTokens.objects.filter(user=user, token=token)
        used_token.first().delete()

        return validated_data
