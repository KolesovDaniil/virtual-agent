from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from notifications.models import Notification

from .serializers import NotificationSerializer


@extend_schema(tags=['Notifications'])
class NotificationViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
