from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100)
    is_active = serializers.BooleanField(default=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_active']

    def validate_email(self, value):
        instance = self.instance
        if instance and instance.email == value:
            return value 

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address is already in use")
        return value

