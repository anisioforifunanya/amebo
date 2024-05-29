from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from users.models import AppUsers


class DMs(models.Model):
    sender = models.ForeignKey('users.AppUsers', on_delete=models.CASCADE, null=True, blank=True, related_name='sender')
    receiver = models.ForeignKey('users.AppUsers', on_delete=models.CASCADE, null=True, blank=True, related_name='receiver')
    message = models.TextField(max_length=50000, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('timestamp',)


class Groups(models.Model):
    owner = models.ForeignKey(AppUsers, on_delete=models.CASCADE, null=True, blank=True, related_name='my_groups')
    name = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    members = models.ManyToManyField(AppUsers)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class GroupChatMessages(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True, blank=True)
    messages = models.JSONField(encoder=DjangoJSONEncoder, default=list, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date_created',)

