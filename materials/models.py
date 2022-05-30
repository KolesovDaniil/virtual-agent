from uuid import uuid4

from django.conf import settings
from django.db import models
from django.urls import reverse

from courses.models import Module
from users.models import User
from virtual_agent.utils import ChoicesEnum, join_url_parts


class MaterialTypes(str, ChoicesEnum):
    QUIZ = 'quiz', 'Квиз'
    TEXT = 'page', 'Текст'
    PDF = 'pdf', 'PDF'
    PRESENTATION = 'pptx', 'Презентация'
    VIDEO = 'mp4', 'Видео'
    OTHER = 'other', 'Другое'


MATERIAL_WEIGHTS_IN_MINUTES = {
    MaterialTypes.QUIZ: 20,
    MaterialTypes.PRESENTATION: 45,
    MaterialTypes.PDF: 30,
    MaterialTypes.VIDEO: 45,
    MaterialTypes.TEXT: 25,
    MaterialTypes.OTHER: 40,
}


class Material(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=32, choices=MaterialTypes.choices())
    moodle_id = models.IntegerField()
    module = models.ForeignKey(
        Module, related_name='materials', on_delete=models.CASCADE
    )
    url = models.URLField()
    deadline = models.DateTimeField(null=True, blank=True)

    def get_url_for_check(self, user: User) -> str:
        check = CheckMaterial.objects.get(material=self, user=user)
        check_url = join_url_parts(
            settings.BASE_URL,
            reverse('api:check_material', args=[str(check.uuid)]),
            first_slash=False,
            trailing_slash=True,
        )
        return check_url


class CheckMaterial(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(
        User, related_name='materials_checks', on_delete=models.CASCADE
    )
    material = models.ForeignKey(
        Material, related_name='materials_checks', on_delete=models.CASCADE
    )
    is_checked = models.BooleanField(default=False)

    class Meta:
        unique_together = [('user', 'material')]

    def __hash__(self):
        return hash(str(self.uuid))
