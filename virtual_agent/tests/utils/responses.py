def api_response(data=None):
    return {'status': 'ok', 'data': data}


def not_found_response():
    return error_response('not_found', 'Not Found')


def failed_validation_response(*form_errors):
    return error_response('bad_request', 'Validation failed', form_errors)


def error_response(code, message, form_errors=None):
    error = {'code': code, 'message': message}

    if form_errors:
        error['formFields'] = [
            {'code': code, 'field': field, 'message': message}
            for code, field, message in form_errors
        ]

    return {'status': 'error', 'error': error}
