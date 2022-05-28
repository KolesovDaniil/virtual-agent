from chats.models import Chat
from courses.models import Course
from users.models import Group, User

from .api import moodle_api
from .serializers import CourseSerializer, GroupSerializer


def create_courses() -> None:
    users = User.objects.all()
    for user in users:
        user_courses = moodle_api.get_user_courses(user.moodle_id)
        for course_data in user_courses:
            serializer = CourseSerializer(data=course_data)
            serializer.is_valid(raise_exception=True)
            moodle_course_id = serializer.validated_data['moodle_id']
            course = Course.objects.filter(moodle_id=moodle_course_id).first()
            if course:
                update_serializer = CourseSerializer(course, data=course_data)
                update_serializer.is_valid(raise_exception=True)
                update_serializer.save()
            else:
                create_serializer = CourseSerializer(data=course_data)
                create_serializer.is_valid(raise_exception=True)
                create_serializer.save()


def create_groups() -> None:
    users = User.objects.all()
    for user in users:
        user_groups = moodle_api.get_user_groups(user.moodle_id)
        for group_data in user_groups:
            serializer = GroupSerializer(data=group_data)
            serializer.is_valid(raise_exception=True)
            moodle_course_id = serializer.validated_data['moodle_id']
            group = Group.objects.filter(moodle_id=moodle_course_id).first()
            if group:
                update_serializer = GroupSerializer(group, data=group_data)
                update_serializer.is_valid(raise_exception=True)
                user.moodle_groups.add(update_serializer.save())
            else:
                create_serializer = GroupSerializer(data=group_data)
                create_serializer.is_valid(raise_exception=True)
                user.moodle_groups.add(create_serializer.save())


def create_chats() -> None:
    groups = Group.objects.all()

    for group in groups:
        try:
            group.chat
        except Chat.DoesNotExist:
            chat_name = f'{group.course.name} {group.name}'
            chat = Chat(name=chat_name, group=group)
            chat.save()
