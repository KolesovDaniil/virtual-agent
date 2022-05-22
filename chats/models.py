from uuid import uuid4

from django.db import models

from courses.models import Course
from users.models import User


class Chat(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=256)
    group = models.OneToOneField(Course, related_name='chat', on_delete=models.CASCADE)


class Message(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    text = models.CharField(max_length=1024)
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
