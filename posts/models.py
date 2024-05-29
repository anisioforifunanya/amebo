from django.db import models
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from users.models import AppUsers


class Posts(models.Model):
    author = models.ForeignKey(AppUsers, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    media = models.JSONField(encoder=DjangoJSONEncoder, default=list)
    liked_users = models.JSONField(encoder=DjangoJSONEncoder, default=list)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author}"


class Comments(models.Model):
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(AppUsers, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.post} - {self.author}"
