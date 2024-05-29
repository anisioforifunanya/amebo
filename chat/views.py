from .models import *
from .serializers import *
from ameboConfig.common import ResponseModelViewSet
from django_filters.rest_framework import DjangoFilterBackend


class DMsViewset(ResponseModelViewSet):
    queryset = DMs.objects.all()
    serializer_class = DMsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sender', 'receiver']

class GroupsViewset(ResponseModelViewSet):
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']


class GroupChatMessagesViewset(ResponseModelViewSet):
    queryset = GroupChatMessages.objects.all()
    serializer_class = GroupChatMessagesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group']

