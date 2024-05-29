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
from django_filters.rest_framework import DjangoFilterBackend


class EventsViewset(ResponseModelViewSet):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['event_type', 'category', 'likes']
    permission_classes = [permissions.AllowAny]

