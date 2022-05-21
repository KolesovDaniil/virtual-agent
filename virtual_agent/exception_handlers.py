from http import HTTPStatus
from typing import Iterable, Optional, Union

from django.http import Http404, HttpResponse, JsonResponse
from funcy import collecting
from rest_framework.exceptions import (
    APIException,
    ErrorDetail,
    NotFound,
    ValidationError,
)
from rest_framework.views import exception_handler


def handle_bad_request(exception: Exception, context: dict) -> HttpResponse:
    if isinstance(exception, Http404):
        data = _render_error(
            code=NotFound.default_code, message=NotFound.default_detail
        )
        return JsonResponse(data, status=HTTPStatus.NOT_FOUND)
    elif isinstance(exception, APIException):
        if isinstance(exception, ValidationError):
            errors = flatten_errors(exception.get_full_details())
            data = _render_error(
                code='bad_request', message='Validation failed', form_errors=errors
            )
        elif isinstance(exception.detail, dict):
            # errors of InvalidToken from rest_framework_simplejwt
            data = _render_error(
                code=exception.detail['code'], message=exception.detail['detail']
            )
        else:
            data = _render_error(code=exception.detail.code, message=str(exception))
        response = JsonResponse(data, status=exception.status_code)
        response._has_been_logged = True  # skips report to sentry
        return response
    return exception_handler(exception, context)


@collecting
def flatten_errors(
    full_details: Union[dict, list], field: Optional[str] = None
) -> Iterable[dict]:
    if isinstance(full_details, list):
        full_details = {'__all__': full_details}

    for field_, all_errors in full_details.items():
        if field is not None:
            field_ = f'{field}[{field_}]'
        if isinstance(all_errors, dict):
            yield from flatten_errors(all_errors, field=field_)
        else:
            for details in all_errors:
                if isinstance(details, ErrorDetail):
                    yield {
                        'field': field_,
                        'code': details.code,
                        'message': str(details),
                    }
                elif 'message' in details and 'code' in details:
                    yield {
                        'field': field_,
                        'code': details['code'],
                        'message': str(details['message']),
                    }
                else:
                    yield from flatten_errors(details)


def _render_error(code: str, message: str, form_errors: Optional[list] = None) -> dict:
    data: dict = {'status': 'error', 'error': {'code': code, 'message': message}}
    if form_errors:
        data['error']['formFields'] = form_errors
    return data
