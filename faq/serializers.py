from rest_framework import serializers

from virtual_agent.utils import ValidatedFileField

from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['uuid', 'question', 'answer', 'course']


class CreateFAQSerializer(serializers.Serializer):
    csv_file = ValidatedFileField()
