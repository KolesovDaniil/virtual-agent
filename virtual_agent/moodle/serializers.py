from rest_framework import serializers

from courses.models import Course
from users.models import Group, User


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='moodle_id')
    fullname = serializers.CharField(source='name')

    class Meta:
        model = Course
        fields = ['uuid', 'id', 'fullname']


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


class MaterialSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='moodle_id')
    name = serializers.CharField()
    dates = serializers.ListField(child=serializers.DictField())
    url = serializers.URLField()
    modname = serializers.CharField(source='type')
    contentsinfo = serializers.DictField(required=False, source='contents_info')
