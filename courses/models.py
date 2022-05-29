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


class Module(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=128)
    moodle_id = models.IntegerField(unique=True)
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    section = models.IntegerField()
    deadline = models.DateTimeField(null=True)

    class Meta:
        unique_together = [('course', 'section')]
