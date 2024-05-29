from .serializers import *
from .models import *
from rest_framework import permissions, status
from ameboConfig.common import ResponseModelViewSet
from django_filters.rest_framework import DjangoFilterBackend


class StoreViewset(ResponseModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'condition']
    permission_classes = [permissions.AllowAny]

