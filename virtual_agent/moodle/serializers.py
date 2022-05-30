from datetime import datetime
from typing import Optional

from funcy import first
from rest_framework import serializers

from courses.models import Course
from users.models import Group, User, UserTypes

ROLE_TO_USER_TYPE_MAPPING = {
    'student': UserTypes.STUDENT,
    'editingteacher': UserTypes.LECTURER,
}


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


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='moodle_id')
    fullname = serializers.CharField(source='first_name')
    email = serializers.EmailField()
    roles = serializers.ListField(child=serializers.DictField(), source='type')

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email', 'roles']

    def validate_roles(self, value: list) -> int:
        role_info = first(value)
        role_short_name = role_info['shortname']
        return ROLE_TO_USER_TYPE_MAPPING.get(role_short_name, UserTypes.STUDENT)
