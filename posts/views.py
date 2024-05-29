from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .serializers import *
from .models import *
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from ameboConfig.permissions import Registration, IsAdminOrReadOnly
from ameboConfig.common import ResponseModelViewSet, CustomResponse, error_handler, CustomValidationError
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView
import django.contrib.auth.password_validation as validators
from cloudinary.uploader import upload, destroy
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError, transaction


class PostsViewset(ResponseModelViewSet):
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer

class CommentsViewset(ResponseModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'author']


class UploadMediaView(APIView):
    """A view to upload a media, either an image or a video"""
    parser_classes = (MultiPartParser, JSONParser)

    @staticmethod
    def post(request):
        with transaction.atomic():
            try:
                # get the media to upload, either an image or a video
                post = request.data.get('post_id')
                img = request.data.get('image')
                vid = request.data.get('video')
                post_object = Posts.objects.filter(id=post).first() # get the post object
                author_username = post_object.author.username
                if img:
                    # ensure it's a supported image type
                    if img.name.split('.')[-1] not in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                        return CustomResponse.failed(message='Invalid image, file type not supported')
                    # Check the size of the image
                    image_size_bytes = img.size  # Get the size of the image file in bytes
                    # Convert bytes to kilobytes
                    image_size_kb = image_size_bytes / 1024
                    # Ensure the image size is less than 1MB
                    if image_size_kb > 1024:  # 1MB in kilobytes
                        return CustomResponse.failed(message='Image size exceeds 1MB limit')
                    # If the image size is within limits, proceed with the upload
                    upload_data = upload(img)
                    image_url, public_id = upload_data['url'], upload_data['public_id']
                    # save the image
                    media_info = {
                        "type" : "image",
                        "url" : image_url,
                        "post_id" : post,
                    }
                    post_object.media.append(media_info)
                    post_object.save()
                elif vid:
                    # ensure it's a supported video type
                    if vid.name.split('.')[-1] not in ['mp4', 'mp3']:
                        return CustomResponse.failed(message='Invalid video, file type not supported')
                    # Check the size of the video
                    video_size_bytes = vid.size  # Get the size of the video file in bytes
                    # Convert bytes to kilobytes
                    video_size_kb = video_size_bytes / 1024
                    # Ensure the video size is less than 8MB
                    if video_size_kb > 8 * 1024:  # 8MB in kilobytes
                        return CustomResponse.failed(message='Video size exceeds 8MB limit')
                    # If the video size is within limits, proceed with the upload
                    upload_data = upload(vid, resource_type="video")
                    video_url, public_id = upload_data['secure_url'], upload_data['public_id']
                    # save the video
                    media_info = {
                        "type" : "video",
                        "url" : video_url,
                        "post_id" : post,
                    }
                    post_object.media.append(media_info)
                    post_object.save()
                return Response({
                    'status': 'success',
                    'data': upload_data,
                }, status=201)
            except Exception as e:
                media_type = 'video' if vid else 'image'
                return Response({
                    'status': 'error',
                    'message': f'Failed to upload {media_type}: {str(e)}',
                }, status=500)



