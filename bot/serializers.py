from rest_framework import serializers


class ButtonSerializer(serializers.Serializer):
    title = serializers.CharField()


class BotResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    buttons = ButtonSerializer(many=True)


class BotRequestSerializer(serializers.Serializer):
    text = serializers.CharField()
    csv = serializers.FileField(required=False)
