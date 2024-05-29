from rest_framework import serializers, exceptions
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from decouple import config
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from ameboConfig.common import CustomValidationError
import django.contrib.auth.password_validation as validators
from cloudinary.uploader import upload, destroy
from users.models import AppUsers

class EventsSerializer(serializers.ModelSerializer):
    event_picture = serializers.FileField(allow_empty_file=False, allow_null=True, required=False)
    attendees = serializers.SerializerMethodField()

    def get_attendees(self, obj):
        # get the number of people attending the event
        try:
            return obj.appusers_set.all().count()
        except:
            return None

    def create(self, validated_data):
        with transaction.atomic():
            picture, created_by = validated_data.pop('event_picture', None), validated_data.get('created_by')
            creator_username = AppUsers.objects.filter(id=created_by.id).first().username
            event_object = super().create(validated_data)
            if picture:
                # ensure it's a supported image type
                if picture.name.split('.')[-1] not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                    raise ValidationError(message='Invalid image, file type not supported')
                # Check the size of the image
                image_size_bytes = picture.size  # Get the size of the image file in bytes

                # Convert bytes to kilobytes
                image_size_kb = image_size_bytes / 1024

                # Ensure the image size is less than 1MB
                if image_size_kb > 1024:  # 1MB in kilobytes
                    raise ValidationError(message='Image size exceeds 1MB limit')

                # If the image size is within limits, proceed with the upload
                upload_data = upload(picture)
                image_url, public_id = upload_data['url'], upload_data['public_id']
                # # delete the old event picture from cloudinary
                # if event_object.picture is not None:
                #     url = event_object.picture
                #     # get the profile picture id
                #     image_id = url.split(f'{creator_username}/')[-1].split('.')[0]
                #     # construct the profile picture public_id
                #     image_public_id = f'{creator_username}/{image_id}'
                #     destroy(image_public_id)
                # replace the former profile picture with the new one
                event_object.picture = image_url
                event_object.save()
            return event_object

    def update(self, instance, validated_data):
        with transaction.atomic():
            picture = validated_data.pop('event_picture', None)
            creator_username = instance.created_by.username
            if picture:
                # ensure it's a supported image type
                if picture.name.split('.')[-1] not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                    raise ValidationError(message='Invalid image, file type not supported')
                # Check the size of the image
                image_size_bytes = picture.size  # Get the size of the image file in bytes

                # Convert bytes to kilobytes
                image_size_kb = image_size_bytes / 1024

                # Ensure the image size is less than 1MB
                if image_size_kb > 1024:  # 1MB in kilobytes
                    raise ValidationError(message='Image size exceeds 1MB limit')

                # If the image size is within limits, proceed with the upload
                upload_data = upload(picture)
                image_url, public_id = upload_data['url'], upload_data['public_id']
                # delete the old event picture from cloudinary
                if instance.picture is not None:
                    url = instance.picture
                    # get the profile picture id
                    image_id = url.split(f'{creator_username}/')[-1].split('.')[0]
                    # construct the profile picture public_id
                    image_public_id = f'{creator_username}/{image_id}'
                    destroy(image_public_id)
                # replace the former profile picture with the new one
                instance.picture = image_url
                instance.save()
            return super().update(instance, validated_data)

    class Meta:
        model = Events
        fields = '__all__'


