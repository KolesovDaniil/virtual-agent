from uuid import uuid4

from django.db import models

from users.models import User


class Course(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=128)
    teachers = models.ManyToManyField(User, related_name='courses')
    moodle_url = models.URLField()
