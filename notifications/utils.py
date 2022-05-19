from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.utils.timezone import now

from notifications.models import Notification
from subjects.models import Material


def add_notifications_for_study_materials(
    user: User,
    start_date: datetime,
    end_date: datetime,
    materials_weights: dict[int, Material],
):
    period_in_seconds = (end_date - start_date).total_seconds()
    materials_period_in_seconds = {
        material: period_in_seconds * weight
        for weight, material in materials_weights.items()
    }

    # split notifications of materials by days
    materials_to_notification_day = defaultdict(list)
    for material, period in materials_period_in_seconds.items():
        notification_datetime = start_date + timedelta(seconds=period)
        notification_month = notification_datetime.month
        notification_day = notification_datetime.day
        materials_to_notification_day[
            datetime(year=now().year, month=notification_month, day=notification_day)
        ].append(material)

    for notification_send_time, materials in materials_to_notification_day:
        notification_text = get_notification_text(materials)
        user.notifications.create(
            send_time=notification_send_time, text=notification_text
        )


def get_notification_text(materials: list[Material]) -> str:
    pass
