from uuid import uuid4

from django.conf import settings
from django.db import models

from users.models import User
from virtual_agent.utils import join_url_parts


class Course(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=128)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    moodle_id = models.IntegerField(unique=True)

    @property
    def url(self) -> str:
        return join_url_parts(
            settings.MOODLE_BASE_URL,
            f'/course/view.php?id={self.moodle_id}',
            first_slash=False,
            trailing_slash=False,
        )

    @property
    def modules_with_content(self) -> models.QuerySet:
        return self.modules.exclude(section=0)


class Module(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=128)
    moodle_id = models.IntegerField(unique=True)
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    section = models.IntegerField()
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = [('course', 'section')]

    @property
    def content_weight(self) -> int:
        from materials.models import MATERIAL_WEIGHTS_IN_MINUTES

        content_types = self.materials.values_list('type', flat=True)
        return sum(map(lambda type_: MATERIAL_WEIGHTS_IN_MINUTES[type_], content_types))
