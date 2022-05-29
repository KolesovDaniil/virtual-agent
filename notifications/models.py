from uuid import uuid4

from django.db import models

from users.models import User


class Notification(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    text = models.CharField(max_length=1024)


class NotificationsTimetable(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    notification = models.ForeignKey(
        Notification, related_name='timetable', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name='notifications_timetable', on_delete=models.CASCADE
    )
    send_time = models.DateTimeField()
