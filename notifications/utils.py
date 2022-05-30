from collections import defaultdict
from datetime import datetime, timedelta
from typing import Generator, Iterable, Optional

from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from funcy import joining, lmapcat, lpluck_attr, walk_values

from courses.models import Module
from materials.models import (
    MATERIAL_WEIGHTS_IN_MINUTES,
    CheckMaterial,
    Material,
    MaterialTypes,
)
from notifications.models import Notification, NotificationsTimetable
from users.models import User


def send_notifications() -> None:
    actual_tasks = NotificationsTimetable.objects.filter(
        is_actual=True, send_time__lt=now()
    )
    notifications_to_send = lpluck_attr('notification', actual_tasks)

    for notification in notifications_to_send:
        if not notification.user.email:
            continue

        send_mail(
            'Запланировано к изучению',
            mark_safe(get_text_for_notification(notification)),
            'agentped@yandex.ru',
            [notification.user.email],
        )
    actual_tasks.update(is_actual=False)


def create_notifications() -> None:
    modules = Module.objects.exclude(section=0)

    for module in modules:
        materials_to_learn = _get_materials_to_learn_for_module(module)
        for user, materials_weights in materials_to_learn:
            materials_to_day = _distribute_materials_within_module(
                start_date=module.start_date,
                end_date=module.end_date,
                materials_weights=materials_weights,
            )
            _create_notifications_for_materials(user, materials_to_day)


def _get_materials_to_learn_for_module(module: Module) -> Generator:
    module_materials = module.materials.all()
    module_users = lmapcat(
        lambda manager: manager.all(),
        lpluck_attr('students', module.course.groups.all()),
    )
    materials_to_learn = lpluck_attr(
        'material',
        CheckMaterial.objects.filter(
            user__in=module_users, material__in=module_materials, is_checked=False
        ),
    )
    users = lpluck_attr(
        'user',
        CheckMaterial.objects.filter(
            user__in=module_users, material__in=module_materials, is_checked=False
        ),
    )

    materials_weights = {
        material: MATERIAL_WEIGHTS_IN_MINUTES[material.type]
        for material in materials_to_learn
    }
    total_weight = sum(materials_weights.values())
    materials_normalized_weights = walk_values(
        lambda weight: weight / total_weight, materials_weights
    )

    for user in users:
        yield user, materials_normalized_weights


def _distribute_materials_within_module(
    start_date: datetime, end_date: datetime, materials_weights: dict[Material, float]
) -> dict[datetime, list[Material]]:
    period_in_seconds = (end_date - start_date).total_seconds()
    materials_period_in_seconds = {
        material: period_in_seconds * weight
        for material, weight in materials_weights.items()
    }

    # split notifications of materials by days
    materials_to_notification_day = defaultdict(list)
    notification_datetime = start_date
    for material, period in materials_period_in_seconds.items():
        notification_datetime = notification_datetime + timedelta(seconds=period)
        notification_month = notification_datetime.month
        notification_day = notification_datetime.day
        materials_to_notification_day[
            datetime(year=now().year, month=notification_month, day=notification_day)
        ].append(material)

    return materials_to_notification_day


def _create_notifications_for_materials(user: User, materials_to_day: dict) -> None:
    for notification_send_time, materials in materials_to_day.items():
        notification = Notification(user=user)
        notification.save()
        notification.materials.add(*materials)
        task = NotificationsTimetable(
            notification=notification, send_time=notification_send_time
        )
        task.save()


@joining('\n')
def get_text_for_notification(notification: Notification) -> Generator:
    materials = notification.materials.all()
    user = notification.user

    yield 'Доброе утро! Сегодня мы предлагаем вам изучить:'

    quizes = materials.filter(type=MaterialTypes.QUIZ)
    if quizes.exists():
        yield _get_text_for_quizes(user, quizes)
        yield '\n'

    texts = materials.filter(type=MaterialTypes.TEXT)
    if texts.exists():
        yield _get_text_for_texts(user, texts)
        yield '\n'

    pdfs = materials.filter(type=MaterialTypes.PDF)
    if pdfs.exists():
        yield _get_text_for_pdfs(user, pdfs)
        yield '\n'

    presentations = materials.filter(type=MaterialTypes.PRESENTATION)
    if presentations.exists():
        yield _get_text_for_presentations(user, presentations)
        yield '\n'

    videos = materials.filter(type=MaterialTypes.VIDEO)
    if videos.exists():
        yield _get_text_for_videos(user, videos)
        yield '\n'

    others = materials.filter(type=MaterialTypes.OTHER)
    if others.exists():
        yield _get_text_for_others(user, others)
        yield '\n'


@joining('\n')
def _get_text_for_quizes(user: User, quizes: Iterable[Material]) -> str:
    yield 'Квизы:'

    for quiz in quizes:
        yield f'– {quiz.get_url_for_check(user)}'


@joining('\n')
def _get_text_for_texts(user: User, texts: Iterable[Material]) -> str:
    yield 'Тексты:'

    for text in texts:
        yield f'– {text.get_url_for_check(user)}'


@joining('\n')
def _get_text_for_pdfs(user: User, pdfs: Iterable[Material]) -> str:
    yield 'PDFs:'

    for pdf in pdfs:
        yield f'– {pdf.get_url_for_check(user)}'


@joining('\n')
def _get_text_for_presentations(user: User, presentations: Iterable[Material]) -> str:
    yield 'Презентации:'

    for presentation in presentations:
        yield f'– {presentation.get_url_for_check(user)}'


@joining('\n')
def _get_text_for_videos(user: User, videos: Iterable[Material]) -> str:
    yield 'Видео:'

    for video in videos:
        yield f'– {video.get_url_for_check(user)}'


@joining('\n')
def _get_text_for_others(user: User, others: Iterable[Material]) -> str:
    yield 'Другое:'

    for other in others:
        yield f'– {other.get_url_for_check(user)}'


def a_tag(link: str, title: Optional[str] = None, target_blank: bool = False) -> str:
    title = title or link
    target = ' target="_blank"' if target_blank else ''
    return mark_safe(f'<a href="{link}"{target}>{title}</a>')  # nosec
