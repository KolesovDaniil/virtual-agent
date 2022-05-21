from django.db import models

from users.models import Group, User


class Chat(models.Model):
    uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=256)
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='chats')


class Message(models.Model):
    uuid = models.UUIDField(primary_key=True)
    text = models.CharField(max_length=1024)
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
