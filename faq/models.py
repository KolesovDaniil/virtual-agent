from uuid import uuid4

from django.db import models

from courses.models import Course


class FAQ(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    question = models.CharField(max_length=256)
    answer = models.CharField(max_length=256)
    course = models.ForeignKey(Course, related_name='faqs', on_delete=models.CASCADE)
