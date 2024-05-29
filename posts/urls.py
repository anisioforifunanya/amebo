from django.urls import re_path as url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

app_name = "post_mgt"

router.register('posts', PostsViewset, basename='posts')
router.register('comments', CommentsViewset, basename='comments')

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^upload_media/$', UploadMediaView.as_view(), name='upload_media'),
]

