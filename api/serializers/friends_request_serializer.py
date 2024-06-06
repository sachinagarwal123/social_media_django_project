from rest_framework import serializers
from django.contrib.auth.models import User
from api.models.friend_request_model import FriendRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    recipient = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'recipient', 'status', 'created_at']
