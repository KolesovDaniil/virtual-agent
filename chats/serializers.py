from rest_framework import serializers

from users.models import User

from .models import Chat, Message


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['uuid', 'first_name', 'last_name', 'image', 'is_lecturer']


class MessageSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()

    class Meta:
        model = Message
        fields = ['uuid', 'text', 'chat', 'user']


class CreateMessageSerializer(serializers.ModelSerializer):
    chat = serializers.SlugRelatedField(slug_field='uuid', queryset=Chat.objects.all())
    user = serializers.SlugRelatedField(slug_field='uuid', queryset=User.objects.all())

    class Meta:
        model = Message
        exclude = ['uuid']
