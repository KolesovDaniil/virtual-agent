from uuid import uuid4

from django.db import models

from materials.models import Material
from users.models import User


class Notification(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    materials = models.ManyToManyField(Material, related_name='notifications')
    user = models.ForeignKey(
        User, related_name='notifications', on_delete=models.CASCADE
    )


class NotificationsTimetable(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    notification = models.ForeignKey(
        Notification, related_name='timetable', on_delete=models.CASCADE
    )
    send_time = models.DateTimeField()
    is_actual = models.BooleanField(default=True)
