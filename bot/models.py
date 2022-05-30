from django.db import models

from users.models import User
from virtual_agent.utils import ChoicesEnum


class UserStatesEnum(int, ChoicesEnum):
    FAQ_COURSE = 1, 'FAQ номер курса'
    FAQ_QUESTION = 2, 'FAQ номер вопроса'
    DEADLINES_COURSE = 3, 'Дедлайны номер курса'


class UserState(models.Model):
    state = models.IntegerField(choices=UserStatesEnum.choices())
    object_uuid = models.CharField(max_length=64, null=True)
    user = models.ForeignKey(User, related_name='states', on_delete=models.CASCADE)
    is_actual = models.BooleanField(default=True)
