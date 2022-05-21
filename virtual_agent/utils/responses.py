from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


class EmptyResponse(serializers.Serializer):
    pass


class ErrorSerializer(serializers.Serializer):
    code = serializers.ChoiceField(
        choices=[
            'invalid',
            'not_authenticated',
            'not_found',
            'permission_denied',
            'parse_error',
            'unavailable',
            'failed_dependency',
            'bad_request',
        ]
    )
    message = serializers.CharField()


@extend_schema_serializer(many=False)
class ResponseWithStatusAndError(serializers.Serializer):
    status = serializers.ChoiceField(choices=['ok', 'error'])
    error = ErrorSerializer()
