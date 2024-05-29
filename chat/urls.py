from .views import *
from django.urls import re_path as url
from rest_framework.routers import DefaultRouter
from django.urls import include

app_name = "chat_mgt"

router = DefaultRouter()

router.register('dms', DMsViewset, basename='dms')
router.register('groups', GroupsViewset, basename='groups')
router.register('group_chats', GroupChatMessagesViewset, basename='group_chats')

urlpatterns = [
    url(r'', include(router.urls)),
]
