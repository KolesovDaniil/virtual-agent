from rest_framework import serializers


class UserLoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
