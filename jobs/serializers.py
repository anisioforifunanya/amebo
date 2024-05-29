from rest_framework import serializers, exceptions
from .models import *


class JobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = '__all__'

