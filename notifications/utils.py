from collections import defaultdict
from datetime import datetime, timedelta
from typing import Generator

from django.utils.timezone import now
from funcy import lmapcat, lpluck_attr, walk_values

from courses.models import Module
from materials.models import MATERIAL_WEIGHTS_IN_MINUTES, CheckMaterial, Material
from notifications.models import Notification
from users.models import User


def create_notifications() -> None:
    modules = Module.objects.all()

    for module in modules:
        deadline = module.deadline or now() + timedelta(weeks=1)
        materials_to_learn = _get_materials_to_learn_for_module(module)
        start_date = now()
        end_date = start_date + timedelta(weeks=1)
        _create_notifications_for_user_per_module()


def _get_materials_to_learn_for_module(
    module: Module,
) -> Generator[tuple[User, dict[Material, float]]]:
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
        notification_text = get_notification_text(materials)
        notification = Notification(text=notification_text)
        notification.save()
        user.notifications_timetable.create(
            send_time=notification_send_time, notification=notification
        )


def get_notification_text(materials: list[Material]) -> str:
    return 'text text'
