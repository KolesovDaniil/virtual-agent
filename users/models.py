from typing import Any, Optional
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from virtual_agent.utils import ChoicesEnum


class TeachersPositions(int, ChoicesEnum):
    LABORATORY_ASSISTANT = 1, 'Лаборант'
    SENIOR_LABORATORY_ASSISTANT = 2, 'Старший лаборант'
    ASSISTANT = 3, 'Ассистент'
    LECTURER = 4, 'Преподаватель'
    SENIOR_LECTURER = 5, 'Старший преподаватель'
    ASSISTANT_PROFESSOR = 6, 'Доцент'
    PROFESSOR = 7, 'Профессор'
    DEPARTMENT_HEAD = 8, 'Завкафедрой'
    DEAN = 9, 'Декан'
    VICE_RECTOR = 10, 'Проректор'
    RECTOR = 11, 'Ректор'


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
    position = models.IntegerField(
        verbose_name='Должность',
        choices=TeachersPositions.choices(),
        null=True,
        blank=True,
    )
    image = models.URLField(verbose_name='Аватарка', null=True, blank=True)
    moodle_id = models.IntegerField(unique=True)
    type = models.IntegerField(choices=UserTypes.choices())

    def save(
        self, skip_checks: Optional[bool] = False, *args: Any, **kwargs: Any
    ) -> None:
        if skip_checks:
            super().save(*args, **kwargs)
            return
        elif self.type == UserTypes.LECTURER and not self.position:
            raise ValidationError(f'Lecturer: {self.uuid} must have position')
        super().save(*args, **kwargs)

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def is_lecturer(self):
        return self.type == UserTypes.LECTURER
