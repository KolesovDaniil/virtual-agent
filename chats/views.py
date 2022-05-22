from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from virtual_agent.utils import ResponseWithStatusAndError

from .models import Message
from .serializers import CreateMessageSerializer, MessageSerializer


@extend_schema(tags=['Message'])
class MessageViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_serializer_class(self) -> type[Serializer]:
        if self.action == 'create':
            return CreateMessageSerializer
        return self.serializer_class

    @extend_schema(
        request=CreateMessageSerializer,
        responses={'201': MessageSerializer, '4XX': ResponseWithStatusAndError},
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        chat = request_serializer.validated_data['chat']

        if chat not in request.user.group.chats:
            raise PermissionDenied('User can not write in this chat')

        message = request_serializer.save()

        response_serializer = self.serializer_class(
            message, context=self.get_serializer_context()
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
