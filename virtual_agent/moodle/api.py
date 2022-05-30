import logging
from typing import Optional

import requests
from django.conf import settings
from furl import furl
from requests import Response

from virtual_agent.utils import join_url_parts, safe_request_method

logger = logging.getLogger(__name__)


class MoodleException(Exception):
    pass


class NoResponseFromMoodle(MoodleException):
    pass


class BadResponseFromMercury(MoodleException):
    pass


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


class MoodleAPI:
    base_url = settings.MOODLE_BASE_URL
    token = get_moodle_token(
        settings.MOODLE_SUPERUSER_USERNAME, settings.MOODLE_SUPERUSER_PASSWORD
    )
    _safe_request = safe_request_method(
        error_msg='Moodle is unavailable', raise_as=NoResponseFromMoodle
    )

    def get_user_courses(self, moodle_user_id: int) -> list:
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_enrol_get_users_courses',
            'moodlewsrestformat': 'json',
            'userid': moodle_user_id,
        }
        url = join_url_parts(
            self.base_url,
            'webservice/rest/server.php',
            first_slash=False,
            trailing_slash=False,
        )
        url = furl(url).add(params).url

        return requests.request('POST', url).json()

    def get_user_groups(self, moodle_user_id: int) -> list:
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_group_get_course_user_groups',
            'moodlewsrestformat': 'json',
            'userid': moodle_user_id,
        }
        url = join_url_parts(
            self.base_url,
            'webservice/rest/server.php',
            first_slash=False,
            trailing_slash=False,
        )
        url = furl(url).add(params).url

        return requests.request('POST', url).json()['groups']

    def get_course_content(self, moodle_course_id: int) -> list:
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_course_get_contents',
            'moodlewsrestformat': 'json',
            'courseid': moodle_course_id,
        }
        url = join_url_parts(
            self.base_url,
            'webservice/rest/server.php',
            first_slash=False,
            trailing_slash=False,
        )
        url = furl(url).add(params).url

        return requests.request('POST', url).json()

    def get_info_about_course_users(self, moodle_course_id: int) -> list:
        params = {
            'wstoken': self.token,
            'wsfunction': 'core_enrol_get_enrolled_users',
            'moodlewsrestformat': 'json',
            'courseid': moodle_course_id,
        }
        url = join_url_parts(
            self.base_url,
            'webservice/rest/server.php',
            first_slash=False,
            trailing_slash=False,
        )
        url = furl(url).add(params).url

        return requests.request('POST', url).json()


moodle_api = MoodleAPI()
