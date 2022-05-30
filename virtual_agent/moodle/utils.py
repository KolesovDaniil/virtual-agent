from datetime import datetime, timedelta
from typing import Optional

from django.db.models import QuerySet
from django.utils.timezone import now
from funcy import last, lmapcat, lpluck_attr, walk_values

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
    UserSerializer,
)


def sync_database():
    create_courses()
    create_or_update_users()
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

        num_of_modules = course.modules.count()
        end_date = course.start_date + timedelta(weeks=num_of_modules)
        course.end_date = end_date
        course.save()
        _add_deadlines_for_course_modules(course)


def create_or_update_users() -> None:
    courses = Course.objects.all()
    for course in courses:
        participants_data = moodle_api.get_info_about_course_users(course.moodle_id)

        for user_data in participants_data:
            _create_or_update_user(user_data)


def _create_or_update_user(user_data: dict):
    serializer = UserSerializer(data=user_data)
    serializer.is_valid(raise_exception=True)
    moodle_id = serializer.validated_data['moodle_id']
    user = User.objects.filter(moodle_id=moodle_id).first()

    first_name = serializer.validated_data['first_name']
    email = serializer.validated_data['email']
    type_ = serializer.validated_data['type']
    if user:
        user.first_name = first_name
        user.moodle_id = moodle_id
        user.email = email
        user.type_ = type_
        user.save()
    else:
        create_serializer = UserSerializer(data=user_data)
        create_serializer.is_valid(raise_exception=True)
        user = create_serializer.save()


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

    material.module.end_date = datetime.fromtimestamp(deadline_timestamp)
    material.module.save()


def _add_deadlines_for_course_modules(course: Course) -> None:
    sorted_course_modules = course.modules_with_content.order_by('section')
    if sorted_course_modules.exclude(end_date=None).exists():
        __add_deadlines_if_modules_with_deadlines_exists(course)
    else:
        __add_deadlines_if_no_modules_with_deadlines(course)


def __add_deadlines_if_modules_with_deadlines_exists(course: Course) -> None:
    sorted_course_modules = course.modules_with_content.order_by('section')
    modules_sections_with_deadlines = sorted_course_modules.exclude(end_date=None)

    # Set deadlines for first section
    first_module_with_deadline = modules_sections_with_deadlines.first()
    start_date = course.start_date
    end_date = first_module_with_deadline.end_date
    modules_for_first_part = sorted_course_modules.filter(
        section__lte=first_module_with_deadline.section
    )
    __set_deadlines(modules_for_first_part, start_date, end_date)

    # Set deadlines for internal sections
    for i in range(len(modules_sections_with_deadlines) - 1):
        start_module = modules_sections_with_deadlines[i]
        end_module = modules_sections_with_deadlines[i + 1]
        start_date = start_module.end_date
        end_date = end_module.end_date
        modules_for_this_part = sorted_course_modules.filter(
            section__gt=start_module.section, section__lte=end_module.section
        )
        __set_deadlines(modules_for_this_part, start_date, end_date)

    # Set deadlines for last section
    last_module_with_deadline = modules_sections_with_deadlines.last()
    start_date = last_module_with_deadline.end_date
    end_date = course.end_date
    modules_for_last_part = sorted_course_modules.filter(
        section__gt=last_module_with_deadline.section
    )
    __set_deadlines(modules_for_last_part, start_date, end_date)


def __add_deadlines_if_no_modules_with_deadlines(course: Course) -> None:
    sorted_course_modules = course.modules_with_content.order_by('section')
    start_date = course.start_date
    end_date = course.end_date
    __set_deadlines(sorted_course_modules, start_date, end_date)


def __set_deadlines(
    modules: QuerySet[Module], start_date: datetime, end_date: datetime
) -> None:
    module_weights = {module: module.content_weight for module in modules}
    total_weight = sum(lpluck_attr('content_weight', modules))

    if total_weight == 0:
        modules.update(start_date=start_date, end_date=end_date)
        return

    modules_normalized_weights = walk_values(
        lambda weight: weight / total_weight, module_weights
    )

    period_in_seconds = (end_date - start_date).total_seconds()
    modules_period_in_seconds = {
        material: period_in_seconds * weight
        for material, weight in modules_normalized_weights.items()
    }

    initial_start_date = start_date
    for module, period in modules_period_in_seconds.items():
        # Save start_date
        module.start_date = initial_start_date

        # Count end_date
        initial_start_date = initial_start_date + timedelta(seconds=period)

        module.end_date = datetime(
            year=now().year,
            month=initial_start_date.month,
            day=initial_start_date.day,
            hour=23,
            minute=59,
        )
        module.save()


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
