from django.db import models

from users.models import User
from virtual_agent.utils import ChoicesEnum


class UserStatesEnum(int, ChoicesEnum):
    FAQ_CSV_DOWNLOAD = 3, 'FAQ загрузка файла'
    FAQ_INFO_QUESTIONS = 4, 'FAQ получение вопросов'
    FAQ_CSV_SUCCESS = 5, 'FAQ загрузка файла прошла успешно'
    FAQ_INFO_ANSWER = 6, 'FAQ получение ответа'
    DEADLINES_COURSE = 7, 'Дедлайны номер курса'


class UserState(models.Model):
    state = models.IntegerField(choices=UserStatesEnum.choices())
    object_uuid = models.CharField(max_length=64, null=True)
    user = models.ForeignKey(User, related_name='states', on_delete=models.CASCADE)
    is_actual = models.BooleanField(default=True)
