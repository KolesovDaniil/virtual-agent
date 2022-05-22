from http import HTTPStatus

from rest_framework.exceptions import APIException


class FailedDependency(APIException):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    default_detail = 'Other service respond with error'
    default_code = 'failed_dependency'


class Unavailable(APIException):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    default_detail = 'Endpoint is unavailable right now'
    default_code = 'unavailable'


class Unsupported(APIException):
    status_code = HTTPStatus.NOT_IMPLEMENTED
    default_detail = 'This version is not supported'
    default_code = 'not_supported'
