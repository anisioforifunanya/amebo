from rest_framework import serializers, exceptions
from .models import *
from django.db import IntegrityError, transaction
from django.db.models import Q
from users.models import AppUsers


class CommentsSerializer(serializers.ModelSerializer):
    author_display_name = serializers.SerializerMethodField()
    author_profile_url = serializers.SerializerMethodField()

    def get_author_display_name(self, obj):
        try:
            return obj.author.display_name
        except: return None

    def get_author_profile_url(self, obj):
        try:
            return obj.author.profile_pic_url
        except: return None

    class Meta:
        model = Comments
        fields = '__all__'



class PostsSerializer(serializers.ModelSerializer):
    author_info = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    liked_users_info = serializers.SerializerMethodField()
    is_liked = serializers.BooleanField(required=False)
    is_unliked = serializers.BooleanField(required=False)

    def get_author_details(self, author_id):
        # use this method to get the author details
        app_user = AppUsers.objects.filter(id=author_id).first()
        if app_user:
            return {
                "id": app_user.id,
                "username": app_user.username,
                "display_name": app_user.display_name,
                "profile_pic_url": app_user.profile_pic_url
            }
        else: return {}

    def get_author_info(self, obj):
        # return the author details
        try:
            info = self.get_author_details(obj.author.id)
            return info
        except: return {}

    def get_comments(self, obj):
        try:
            # get all comments attached to the post
            comments = obj.comments_set.all()
            # format comment info to be returned
            all_comments_info = []
            for comment in comments:
                info = {
                    "id" : comment.id,
                    "author" : self.get_author_details(comment.author.id),
                    "content" : comment.content,
                    "date_created" : comment.date_created
                }
                all_comments_info.append(info)

            return all_comments_info
        except Exception as e:
            print(str(e))
            return {}

    def get_liked_users_info(self, obj):
        # return the information for every user that liked the post
        try:
            data = []
            for user_id in obj.liked_users:
                user = AppUsers.objects.filter(id=user_id).first()
                data.append({
                    "username" :  user.username,
                    "display_name" :  user.display_name,
                    "profile_pic_url" :  user.profile_pic_url,
                })
            return data
        except: return {}

    def update(self, instance, validated_data):
        with transaction.atomic():
            # get logged in user
            user = self.context["request"].user
            user_id = AppUsers.objects.filter(owner=user).first().id
            # when a user likes a post, save his/her id in the db
            if validated_data.pop('is_liked', None): 
                instance.liked_users.append(str(user_id))
            if validated_data.pop('is_unliked', None): 
                instance.liked_users.remove(str(user_id))
            instance.save()
        return super().update(instance, validated_data)

    class Meta:
        model = Posts
        fields = '__all__'

