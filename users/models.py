from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from django.utils import timezone
from datetime import date
from decouple import config
from django.core.serializers.json import DjangoJSONEncoder
from events.models import Events

class UserProfileManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Kindly enter an email address for this user.")

        # now create the user, using the given email and password
        user = self.model(
            email=self.normalize_email(email.lower()),
            username=self.normalize_email(email.lower()),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email=None, password=None, **extra_fields):
        if password is None:
            raise ValueError("Kindly enter a valid password for this superuser.")

        # now create the superuser, using the given email and password
        user = self.create_user(email, password)
        user.is_superuser, user.is_staff = True, True
        user.save()
        return user

class User(AbstractUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    recent_passwords = models.JSONField(encoder=DjangoJSONEncoder, default=list, null=True, blank=True)
    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Users'


class AppUsers(models.Model):
    gender_options= (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    user_type_options= (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(max_length=1500, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    user_type = models.CharField('User Type', choices=user_type_options, max_length=255, default='user')
    gender = models.CharField('Gender', choices=gender_options, max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.CharField(max_length=255, null=True, blank=True)
    following = models.JSONField(encoder=DjangoJSONEncoder, default=list)
    followers = models.JSONField(encoder=DjangoJSONEncoder, default=list)
    coordinates = models.CharField(max_length=2000, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    filled_all_info = models.BooleanField(default=False)
    profile_pic_url = models.URLField(max_length=1000, null=True, blank=True)
    other_pics = models.JSONField(encoder=DjangoJSONEncoder, default=list)
    verify_pic_url = models.URLField(max_length=1000, null=True, blank=True)
    social_links = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)
    work_experience = models.TextField(max_length=1500, null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
    user_events = models.ManyToManyField(Events, blank=True) # holds all the user has/will attend(ed)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name}"

    class Meta:
        verbose_name = 'AppUsers'


class ResetPasswordTokens(models.Model):
    token = models.CharField(max_length=500, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
