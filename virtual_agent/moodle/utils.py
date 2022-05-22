from typing import Optional

import requests
from django.conf import settings

from virtual_agent.utils import join_url_parts


def get_moodle_token(
    username: str = settings.MOODLE_SUPERUSER_USERNAME,
    password: str = settings.MOODLE_SUPERUSER_PASSWORD,
    service_short_name: str = 'moodle_mobile_app',
) -> Optional[str]:
    url = join_url_parts(
        settings.MOODLE_BASE_URL,
        f'/login/token.php'
        f'?username={username}&password={password}&service={service_short_name}',
        trailing_slash=False,
        first_slash=False,
    )

    response = requests.request('GET', url)

    if response.status_code == 200:
        return response.json()['token']
    return None
