from datetime import datetime
from typing import Optional

from funcy import last, lmapcat, lpluck_attr

from chats.models import Chat
from courses.models import Course, Module
from materials.models import CheckMaterial, Material, MaterialTypes
from materials.utils import get_material_type
from users.models import Group, User

from .api import moodle_api
from .serializers import (
    CourseSerializer,
    GroupSerializer,
    MaterialSerializer,
    ModuleSerializer,
)


def sync_database():
    create_courses()
    create_groups()
    create_chats()
    create_modules_with_materials()


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


def create_modules_with_materials() -> None:
    courses = Course.objects.all()

    for course in courses:
        data = moodle_api.get_course_content(course.moodle_id)

        for module_data in data:
            module = _create_module_for_course(module_data, course)
            materials_data = module_data['modules']

            for material_data in materials_data:
                _create_material_for_module(material_data, module)


def _create_module_for_course(module_data: dict, course: Course) -> Module:
    serializer = ModuleSerializer(data=module_data)
    serializer.is_valid(raise_exception=True)
    moodle_id = serializer.validated_data['moodle_id']
    module = course.modules.filter(moodle_id=moodle_id).first()

    name = serializer.validated_data['name']
    section = serializer.validated_data['section']
    if module:
        module.name = name
        module.section = section
        module.save()
        return module

    else:
        return course.modules.create(name=name, moodle_id=moodle_id, section=section)


def _create_material_for_module(material_data: dict, module: Module) -> None:
    serializer = MaterialSerializer(data=material_data)
    serializer.is_valid(raise_exception=True)
    moodle__id = serializer.validated_data['moodle_id']
    material = module.materials.filter(moodle_id=moodle__id).first()

    name = serializer.validated_data['name']
    url = serializer.validated_data['url']
    dates = serializer.validated_data['dates']
    contents_info = serializer.validated_data.get('contents_info')
    material_type = get_material_type(serializer.validated_data['type'], contents_info)
    deadline_timestamp = last(dates) and last(dates)['timestamp']

    if material:
        material.name = name
        material.url = url
        material.type = material_type
        if deadline_timestamp:
            material.deadline = datetime.fromtimestamp(deadline_timestamp)
        material.save()

    else:
        data = {
            'name': name,
            'moodle_id': moodle__id,
            'url': url,
            'type': material_type,
        }
        if deadline_timestamp:
            data |= {'deadline': datetime.fromtimestamp(deadline_timestamp)}
        material = module.materials.create(**data)

    _check_if_material_is_deadline_quiz(material, deadline_timestamp)
    _create_checks_for_material(material)


def _check_if_material_is_deadline_quiz(
    material: Material, deadline_timestamp: Optional[int]
) -> None:
    material_name_words = material.name.lower().split(' ')

    if 'deadline' not in material_name_words or material.type != MaterialTypes.QUIZ:
        return

    if not deadline_timestamp:
        return

    material.module.deadline = datetime.fromtimestamp(deadline_timestamp)
    material.module.save()


def _create_checks_for_material(material: Material) -> None:
    material_learners = lmapcat(
        lambda manager: manager.all(),
        lpluck_attr('students', material.module.course.groups.all()),
    )

    material_checks = []
    for material_learner in material_learners:
        try:
            CheckMaterial.objects.get(user=material_learner, material=material)
        except CheckMaterial.DoesNotExist:
            material_checks.append(
                CheckMaterial(user=material_learner, material=material)
            )

    CheckMaterial.objects.bulk_create(material_checks)
