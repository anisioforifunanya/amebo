from rest_framework import serializers, exceptions
from .models import *
from users.models import AppUsers
from ameboConfig.common import CustomValidationError
import django.contrib.auth.password_validation as validators
from cloudinary.uploader import upload, destroy
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction


class StoreSerializer(serializers.ModelSerializer):
    picture = serializers.FileField(allow_empty_file=False, allow_null=True, required=False)

    def create(self, validated_data):
        with transaction.atomic():
            picture, posted_by = validated_data.pop('picture', None), validated_data.get('posted_by')
            creator_username = AppUsers.objects.filter(id=posted_by.id).first().username
            product_obj = super().create(validated_data)
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
                # replace the former profile picture with the new one
                product_obj.picture_url = image_url
                product_obj.save()
            return product_obj

    def update(self, instance, validated_data):
        with transaction.atomic():
            picture = validated_data.pop('picture', None)
            creator_username = instance.posted_by.username
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
                if instance.picture_url is not None:
                    url = instance.picture_url
                    # get the profile picture id
                    image_id = url.split(f'{creator_username}/')[-1].split('.')[0]
                    # construct the profile picture public_id
                    image_public_id = f'{creator_username}/{image_id}'
                    destroy(image_public_id)
                # replace the former profile picture with the new one
                instance.picture_url = image_url
                instance.save()
            return super().update(instance, validated_data)

    class Meta:
        model = Store
        fields = '__all__'

