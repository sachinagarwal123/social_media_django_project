from django.contrib.auth.models import User
from rest_framework import serializers


class AuthSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = "__all__"

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            raise serializers.ValidationError("Both email and password are required")
        return data
