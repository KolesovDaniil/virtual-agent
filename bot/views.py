from datetime import datetime
from typing import Any, Iterable, Optional

from django.db.models import Model
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from funcy import joining, lmapcat, lpluck_attr
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from faq.models import FAQ
from materials.models import Material
from users.models import User
from virtual_agent.utils import ResponseWithStatusAndError

from .models import UserState, UserStatesEnum
from .serializers import BotRequestSerializer, BotResponseSerializer

NAME_TO_MODEL_MAPPING = {'course': Course}

DEFAULT_ANSWER = {
    'answer': 'Выберите действие',
    'buttons': [{'title': 'Дедлайны'}, {'title': 'FAQ'}],
}
DEFAULT_BUTTONS = [{'title': 'Дедлайны'}, {'title': 'FAQ'}]


@extend_schema(
    tags=['Bot'],
    request=BotRequestSerializer,
    responses={'200': BotResponseSerializer, '4XX': ResponseWithStatusAndError},
)
class MainBotAPIView(APIView):
    permission_classes = ()

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        user_state = _get_user_state(user)

        serializer = BotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data['text']

        if not user_state:
            return Response(DEFAULT_ANSWER)

        if text == 'FAQ':
            return Response(faq_courses(user))

        if user_state.state == UserStatesEnum.FAQ_COURSE:
            return Response(faq_for_course(user, text))

        if user_state.state == UserStatesEnum.FAQ_QUESTION:
            q_num, _ = text.split(' ')
            course = Course.objects.filter(uuid=user_state.object_uuid).first()
            return Response(faq_answer(user, q_num, course))

        if text == 'Дедлайны':
            return Response(deadlines(user))

        return Response(DEFAULT_ANSWER)


def faq_courses(user: User) -> dict:
    answer = {'answer': 'Выберите курс'}
    buttons = []
    courses = lpluck_attr('course', user.moodle_groups.all())

    for course in courses:
        buttons.append({'title': course.name})

    answer['buttons'] = buttons
    _set_user_state(user, UserStatesEnum.FAQ_COURSE)

    return answer


def faq_for_course(user: User, course_name: str) -> dict:
    course = Course.objects.filter(name=course_name).first()
    if not course:
        _reset_user_state(user)
        return {'answer': 'Такого курса не существует', 'buttons': DEFAULT_BUTTONS}

    faqs = FAQ.objects.filter(course__name=course_name).order_by('uuid')
    questions = faqs.values_list('question', flat=True)
    questions_list = ''
    for num, question in enumerate(questions):
        questions_list = questions_list + f'{num + 1} {question}\n'
    answer = f'Введите номер вопроса:\n{questions_list}'
    _set_user_state(user, UserStatesEnum.FAQ_QUESTION, course)

    return {'answer': answer}


def faq_answer(user: User, question_id: int, course: Course) -> dict:
    faqs = FAQ.objects.filter(course=course).order_by('uuid')
    answer = faqs[question_id - 1].answer
    _reset_user_state(user)
    return {'answer': answer, 'buttons': DEFAULT_BUTTONS}


def deadlines(user: User) -> dict:
    today = now()
    start_date = datetime(
        year=today.year, month=today.month, day=today.day, hour=0, minute=0
    )
    end_date = datetime(
        year=today.year, month=today.month, day=today.day, hour=23, minute=59
    )
    user_courses = lpluck_attr('course', user.moodle_groups.all())
    user_modules_uuids = lpluck_attr(
        'uuid',
        lmapcat(lambda manager: manager.all(), lpluck_attr('modules', user_courses)),
    )
    materials = Material.objects.filter(module__uuid__in=user_modules_uuids).exclude(
        deadline=None
    )
    materials_for_today = materials.filter(
        deadline__gt=start_date, deadline__lt=end_date
    )
    text = _get_text_for_deadlines(materials_for_today)

    return {'answer': text, 'buttons': DEFAULT_BUTTONS}


def _set_user_state(
    user: User, state: UserStatesEnum, obj: Optional[Model] = None
) -> None:
    obj_model_name = NAME_TO_MODEL_MAPPING[obj.__class__]
    obj_uuid = str(obj.uuid)
    user.states.update(is_actual=False)
    user.states.create(
        state=state, state_model=obj_model_name, state_object_uuid=obj_uuid
    )


def _get_user_state(user: User) -> Optional[UserState]:
    return user.states.filter(is_actual=True).last()


def _reset_user_state(user: User) -> None:
    user.states.update(is_actual=False)


@joining('\n')
def _get_text_for_deadlines(materials: Iterable[Material]) -> str:
    yield 'На сегодня запланировано:'

    for material in materials:
        time_format = material.deadline.date().strftime('%Y-%m-%d %H:%m')
        yield f'{material.name}  --  {time_format}'
