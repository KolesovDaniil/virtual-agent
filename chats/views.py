from typing import Any

from drf_spectacular.utils import extend_schema
from funcy import lpluck_attr
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from virtual_agent.utils import ResponseWithStatusAndError

from .models import Chat, Message
from .serializers import (
    ChatMessagesSerializer,
    ChatSerializer,
    CreateMessageSerializer,
    MessageSerializer,
    SimpleUserSerializer,
)


@extend_schema(tags=['Messages'])
class MessageViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = ()
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'chat_uuid'

    def get_object(self) -> Chat:
        chat_uuid = self.kwargs[self.lookup_field]
        return get_object_or_404(Chat.objects.all(), uuid=chat_uuid)

    @extend_schema(
        request=CreateMessageSerializer,
        responses={'201': MessageSerializer, '4XX': ResponseWithStatusAndError},
    )
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        request_serializer = CreateMessageSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        user = request.user
        chat = request_serializer.validated_data['chat']
        text = request_serializer.validated_data['text']

        if chat.group not in request.user.moodle_groups.all():
            raise PermissionDenied('User can not write in this chat')

        message = chat.messages.create(user=user, text=text)

        response_serializer = self.serializer_class(
            message, context=self.get_serializer_context()
        )

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={'201': ChatMessagesSerializer, '4XX': ResponseWithStatusAndError}
    )
    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        chat = self.get_object()
        user = request.user
        user_chats = lpluck_attr('chat', user.moodle_groups.all())

        if chat not in user_chats:
            raise PermissionDenied('You do not have access to read chat messages')

        data = MessageSerializer(chat.messages.all(), many=True).data
        data['chat'] = str(chat.uuid)
        data['self_user'] = SimpleUserSerializer(user).data
        response_serializer = ChatMessagesSerializer(data)

        return Response(response_serializer.data)


@extend_schema(
    tags=['Chats'],
    responses={'200': ChatSerializer(many=True), '4XX': ResponseWithStatusAndError},
)
class GetUserChatsView(APIView):
    permission_classes = ()

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        user_chats = lpluck_attr('chat', user.moodle_groups.all())
        response_serializer = ChatSerializer(user_chats, many=True)

        return Response(response_serializer.data)
