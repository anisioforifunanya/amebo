from rest_framework import serializers
from .models import *
from django.db import transaction

class DMsSerializer(serializers.ModelSerializer):
    sender_info = serializers.SerializerMethodField()
    receiver_info = serializers.SerializerMethodField()

    def get_sender_info(self, obj):
        # get the sender information
        try:
            data = {
                "username": obj.sender.username,
                "display_name": obj.sender.display_name,
                "profile_pic_url": obj.sender.profile_pic_url
            }
            return data
        except: return {}

    def get_receiver_info(self, obj):
        # get the receiver information
        try:
            data = {
                "username": obj.receiver.username,
                "display_name": obj.receiver.display_name,
                "profile_pic_url": obj.receiver.profile_pic_url
            }
            return data
        except: return {}

    class Meta:
        model = DMs
        fields = '__all__'


class GroupsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Groups
        fields = '__all__'



class GroupChatMessagesSerializer(serializers.ModelSerializer):
    group_info = serializers.SerializerMethodField()
    new_message = serializers.JSONField(write_only=True)

    @transaction.atomic
    def create(self, validated_data):
        new_message, group_id = validated_data.pop('new_message'),  validated_data.get('group')
        # get the record for that group
        group_record = GroupChatMessages.objects.filter(group=group_id)
        if group_record.exists():
            group_record = group_record.first()
            group_record.messages.append(new_message)
            group_record.save()
        else:
            group_record = GroupChatMessages.objects.create(group=group_id,
                messages=[new_message])
        return group_record

    def get_group_info(self, obj):
        # get the group information
        try:
            return GroupsSerializer(obj, many=True).data
        except: return {}

    class Meta:
        model = GroupChatMessages
        fields = '__all__'


