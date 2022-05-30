from typing import Any
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models

from virtual_agent.utils import ChoicesEnum


class UserTypes(int, ChoicesEnum):
    STUDENT = 1, 'Студент'
    LECTURER = 2, 'Преподаватель'


class Group(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=256)
    course = models.ForeignKey(
        'courses.Course', related_name='groups', on_delete=models.CASCADE
    )
    moodle_id = models.IntegerField(unique=True)


class User(AbstractUser):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    moodle_groups = models.ManyToManyField(
        Group, verbose_name='Группы', related_name='students', null=True, blank=True
    )
    image = models.URLField(verbose_name='Аватарка', null=True, blank=True)
    moodle_id = models.IntegerField(unique=True)
    type = models.IntegerField(choices=UserTypes.choices())

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.username:
            self.username = f'user#{self.uuid}'
        super().save(args, kwargs)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def is_lecturer(self):
        return self.type == UserTypes.LECTURER
