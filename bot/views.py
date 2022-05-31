from datetime import datetime
from typing import Any, Iterable, Optional

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Model
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from funcy import joining, lcat, lpluck_attr
from rest_framework.request import Request
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from courses.models import Course
from faq.models import FAQ
from faq.utils import create_faq_from_csv
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

    @csrf_exempt
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = request.user
        user_state = _get_user_state(user)

        serializer = BotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data.get('text')
        csv_file = serializer.validated_data.get('csv_file')

        if not text:
            return Response(DEFAULT_ANSWER)

        if text == 'FAQ':
            return Response(faq_get_action())

        if text == 'Дедлайны':
            return Response(deadlines(user))

        if text == 'Получить FAQ':
            return Response(faq_info_courses(user))

        if text == 'Загрузить FAQ':
            return Response(faq_csv_courses(user))

        if not user_state:
            return Response(DEFAULT_ANSWER)

        if user_state.state == UserStatesEnum.FAQ_INFO_QUESTIONS:
            return Response(faq_info_questions(user, text))

        if user_state.state == UserStatesEnum.FAQ_INFO_ANSWER:
            return Response(faq_info_answer(user, text))

        if user_state.state == UserStatesEnum.FAQ_CSV_DOWNLOAD:
            return Response(faq_csv_download(user, text))

        if user_state.state == UserStatesEnum.FAQ_CSV_SUCCESS:
            if not csv_file:
                return Response(
                    {'answer': 'Необходимо загрузить csv файл', 'buttons': []}
                )
            return Response(faq_csv_success(user, csv_file))

        return Response(DEFAULT_ANSWER)


def faq_get_action() -> dict:
    return {
        'answer': 'Выберите действие',
        'buttons': [{'title': 'Получить FAQ'}, {'title': 'Загрузить FAQ'}],
    }


def faq_csv_courses(user: User) -> dict:
    answer = {'answer': 'Выберите курс:'}
    buttons = []
    courses = lpluck_attr('course', user.moodle_groups.all())

    for course in courses:
        buttons.append({'title': course.name})

    answer['buttons'] = buttons
    _set_user_state(user, UserStatesEnum.FAQ_CSV_DOWNLOAD)

    return answer


def faq_info_courses(user: User) -> dict:
    answer = {'answer': 'Выберите курс:'}
    buttons = []
    courses = lpluck_attr('course', user.moodle_groups.all())

    for course in courses:
        buttons.append({'title': course.name})

    answer['buttons'] = buttons
    _set_user_state(user, UserStatesEnum.FAQ_INFO_QUESTIONS)

    return answer


def faq_csv_download(user: User, text: str) -> dict:
    course = Course.objects.filter(name=text).first()
    if not course:
        response = faq_csv_courses(user)
        response['answer'] = (
            'Извините, такого курса не существует. ' + response['answer']
        )
        return response
    _set_user_state(user, UserStatesEnum.FAQ_CSV_SUCCESS, course)
    return {
        'answer': (
            'Загрузите csv файл с двумя колонками. '
            'В первой должны содержаться вопросы, а во второй ответы'
        ),
        'buttons': [],
    }


def faq_csv_success(user: User, csv_file: InMemoryUploadedFile) -> dict:
    user_state = _get_user_state(user)
    course = Course.objects.get(uuid=user_state.object_uuid)

    create_faq_from_csv(csv_file, course)
    _reset_user_state(user)
    return {'answer': 'FAQ успешно загружен!', 'buttons': DEFAULT_BUTTONS}


def faq_info_questions(user: User, text: str) -> dict:
    course = Course.objects.filter(name=text).first()
    if not course:
        response = faq_info_courses(user)
        response['answer'] = (
            'Извините, такого курса не существует. ' + response['answer']
        )
        return response

    faqs = FAQ.objects.filter(course=course).order_by('uuid')
    if faqs.count() == 0:
        response = faq_info_courses(user)
        response['answer'] = (
            'Извините, данный курс ещё не имеет FAQ. ' + response['answer']
        )
        return response

    questions = faqs.values_list('question', flat=True)
    questions_list = ''
    for num, question in enumerate(questions):
        questions_list = questions_list + f'{num + 1} {question}\n'
    answer = f'Введите номер вопроса:\n{questions_list}'
    _set_user_state(user, UserStatesEnum.FAQ_INFO_ANSWER, course)

    return {'answer': answer}


def faq_info_answer(user: User, text: str) -> dict:
    question_id = int(text)
    user_state = _get_user_state(user)
    course = Course.objects.get(uuid=user_state.object_uuid)
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
        'uuid', lcat(lpluck_attr('modules_with_content', user_courses))
    )
    materials = Material.objects.filter(module__uuid__in=user_modules_uuids).exclude(
        deadline=None
    )
    materials_for_today = materials.filter(
        deadline__gt=start_date, deadline__lt=end_date
    )
    if materials_for_today.count() == 0:
        return {
            'answer': 'На сегодня ничего не запланировано!',
            'buttons': DEFAULT_BUTTONS,
        }
    text = _get_text_for_deadlines(materials_for_today)

    return {'answer': text, 'buttons': DEFAULT_BUTTONS}


def _set_user_state(
    user: User, state: UserStatesEnum, obj: Optional[Model] = None
) -> None:
    user.states.update(is_actual=False)

    data = {'state': state}
    if obj:
        data['object_uuid'] = str(obj.uuid)

    user.states.create(**data)


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
