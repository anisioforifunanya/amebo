from rest_framework.response import Response
from .serializers import *
from .models import *
from rest_framework import permissions, status
from ameboConfig.common import ResponseModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

class JobsViewset(ResponseModelViewSet):
    queryset = Jobs.objects.all()
    serializer_class = JobsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['posted_by', 'job_type', 'employment_type']
    permission_classes = [permissions.AllowAny]
