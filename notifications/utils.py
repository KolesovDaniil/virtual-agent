from collections import defaultdict
from datetime import datetime, timedelta
from typing import Generator, Iterable

from django.utils.timezone import now
from funcy import lmapcat, lpluck_attr, walk_values
from funcy import joining

from courses.models import Module
from materials.models import MATERIAL_WEIGHTS_IN_MINUTES, CheckMaterial, Material, MaterialTypes
from notifications.models import Notification, NotificationsTimetable
from users.models import User


def create_notifications() -> None:
    modules = Module.objects.exclude(section=0)

    for module in modules:
        materials_to_learn = _get_materials_to_learn_for_module(module)
        for user, materials_weights in materials_to_learn:
            _create_notifications_for_user_per_module(
                user,
                start_date=module.start_date,
                end_date=module.end_date,
                materials_weights=materials_weights,
            )


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


def _create_notifications_for_user_per_module(
    user: User,
    start_date: datetime,
    end_date: datetime,
    materials_weights: dict[Material, float],
):
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

    for notification_send_time, materials in materials_to_notification_day.items():
        notification = Notification(user=user)
        notification.save()
        notification.materials.add(*materials)
        task = NotificationsTimetable(
            notification=notification, send_time=notification_send_time
        )
        task.save()


@joining('<br>')
def get_text_for_notification(notification: Notification) -> Generator:
    materials = notification.materials.all()

    quizes = materials.filter(type=MaterialTypes.QUIZ)
    if quizes.exists():
        yield _get_text_for_quizes(quizes)

    texts = materials.filter(type=MaterialTypes.TEXT)
    if texts.exists():
        yield _get_text_for_texts(texts)

    pdfs = materials.filter(type=MaterialTypes.PDF)
    if pdfs.exists():
        yield _get_text_for_pdfs(pdfs)

    presentations = materials.filter(type=MaterialTypes.PRESENTATION)
    if presentations.exists():
        yield _get_text_for_presentations(presentations)



def _get_text_for_quizes(quizes: Iterable[Material]) -> str:
    pass

def _get_text_for_texts(texts: Iterable[Material]) -> str:
    pass

def _get_text_for_pdfs(pdfs: Iterable[Material]) -> str:
    pass

def _get_text_for_presentations(presentations: Iterable[Material]) -> str:
    pass

def _get_text_for_videos(videos: Iterable[Material]) -> str:
    pass

def _get_text_for_others(others: Iterable[Material]) -> str:
    pass
