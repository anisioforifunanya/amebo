from django.urls import re_path as url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

app_name = "job_mgt"

router.register('jobs', JobsViewset, basename='jobs')

urlpatterns = [
    url(r'', include(router.urls)),
]

