from django.urls import re_path as url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

app_name = "event_mgt"

router.register('events', EventsViewset, basename='events')

urlpatterns = [
    url(r'', include(router.urls)),
]

