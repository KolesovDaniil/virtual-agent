import logging
from json.decoder import JSONDecodeError
from typing import Any, Optional
from uuid import UUID

import requests
from dateutil.parser import parse
from django.conf import settings
from django.utils.decorators import method_decorator
from funcy import get_in, retry
from requests import RequestException, Response

from virtual_agent.utils import join_url_parts, safe_request_method

logger = logging.getLogger(__name__)


class MoodleException(Exception):
    pass


class NoResponseFromMoodle(MoodleException):
    pass


class BadResponseFromMercury(MoodleException):
    pass


class MoodleAPI:
    base_url = settings.MOODLE_BASE_URL
    token = settings.MOODLE_TOKEN
    _safe_request = safe_request_method(
        error_msg='Moodle is unavailable', raise_as=NoResponseFromMoodle
    )

    # def get_article_data(self, article_uuid: str) -> dict:
    #     url = f'{self.base_url}/api/articles/{article_uuid}/comments'
    #
    #     data = self._get(url)
    #
    #     published_at = parse(data['date_published'])
    #     result = {
    #         'uuid': data['uuid'],
    #         'title': data['title'],
    #         'article_name': data['url'],
    #         'editorial_id': data['author_id'],
    #         'published_at': published_at,
    #         'comments_allowed': data['comments_allowed'],
    #         'editorium': data['editorium'],
    #         'rubric': data['rubric'],
    #     }
    #
    #     return result
    #
    # def get_last_articles(
    #     self, period_in_seconds: Optional[int] = None, author_id: Optional[int] = None
    # ) -> list[dict]:
    #     params = {}
    #     if period_in_seconds:
    #         period_in_hours = int(period_in_seconds / 60 / 60) or 1
    #         params['period'] = f'{period_in_hours}hour'
    #     if author_id:
    #         params['author_id'] = author_id  # type: ignore
    #
    #     url = join_url_parts(self.base_url, '/api/public/v1/potoque/')
    #     return self._get(url, **params)['data']
    #
    # def get_mercury_user_data(self, mercury_user_id: int) -> dict:
    #     url = join_url_parts(self.base_url, '/api/authors/', mercury_user_id)
    #     return self._get(url)
    #
    # def send_form_answer(  # noqa: CFQ002
    #     self,
    #     author: dict,
    #     form_data: dict,
    #     form_id: UUID,
    #     use_titles_as_headers: bool,
    #     hide_author: bool,
    # ) -> dict:
    #     url = join_url_parts(self.base_url, '/api/private/v1/ugc-importer/')
    #     return self._post(
    #         url,
    #         author=author,
    #         article_data=form_data,
    #         form_id=str(form_id),
    #         use_titles_as_headers=use_titles_as_headers,
    #         hide_author=hide_author,
    #     )['data']

    def _get(self, url: str, **params: Any) -> dict:
        with self._safe_request():
            return self._parse_mercury_response(
                self._request('GET', url, params=params)
            )

    def _post(self, url: str, **data: Any) -> dict:
        with self._safe_request():
            return self._parse_mercury_response(self._request('POST', url, json=data))

    def _patch(self, url: str, **data: Any) -> dict:
        with self._safe_request():
            return self._parse_mercury_response(self._request('PATCH', url, json=data))

    def _parse_moodle_response(self, response: Response) -> dict:
        try:
            data = response.json()
        except JSONDecodeError:
            raise BadResponseFromMercury(
                f'Bad response from Mercury: {response.text or response.status_code}'
            )
        if not data or 'error' in data or 'http_code' in data:
            raise BadResponseFromMercury(
                get_in(data, ['message'])
                or get_in(data, ['error', 'message'])
                or get_in(data, ['error', 'http_code'])
                or ''
            )
        return data

    @method_decorator(retry(3, [RequestException]))
    def _request(self, method: str, url: str, **kwargs: Any) -> Response:
        headers = {'Authorization': f'Bearer {self.token}'}
        return requests.request(
            method,
            url,
            headers=headers,
            timeout=settings.MOODLE_API_TIMEOUT_IN_SECONDS,
            **kwargs,
        )


moodle_api = MoodleAPI()
