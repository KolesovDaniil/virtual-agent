from datetime import datetime
from typing import Optional

from rest_framework import serializers

from courses.models import Course
from users.models import Group


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='moodle_id')
    fullname = serializers.CharField(source='name')
    startdate = serializers.IntegerField(source='start_date')
    enddate = serializers.IntegerField(source='end_date')

    class Meta:
        model = Course
        fields = ['uuid', 'id', 'fullname', 'startdate', 'enddate']

    def validate_startdate(self, value: int) -> datetime:
        return datetime.fromtimestamp(value)

    def validate_enddate(self, value: int) -> Optional[datetime]:
        if not value:
            return
        return datetime.fromtimestamp(value)


class GroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='moodle_id')
    name = serializers.CharField()
    courseid = serializers.SlugRelatedField(
        slug_field='moodle_id', queryset=Course.objects.all(), source='course'
    )

    class Meta:
        fields = ['uuid', 'id', 'name', 'courseid']
        model = Group


class ModuleSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='moodle_id')
    name = serializers.CharField()
    section = serializers.IntegerField()


class MaterialSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='moodle_id')
    name = serializers.CharField()
    dates = serializers.ListField(child=serializers.DictField())
    url = serializers.URLField()
    modname = serializers.CharField(source='type')
    contentsinfo = serializers.DictField(required=False, source='contents_info')
