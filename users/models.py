from django.contrib.auth.models import User
from django.db import models


class Group(models.Model):
    uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=256)


class Student(User):
    uuid = models.UUIDField(primary_key=True)
    group = models.ForeignKey(
        Group, verbose_name="Группа", related_name="students", on_delete=models.CASCADE
    )


class Teacher(User):
    uuid = models.UUIDField(primary_key=True)
    position = models.CharField(verbose_name='Должность', max_length=256)
