from typing import Optional

from rest_framework.renderers import JSONRenderer


class UnicodeJsonRenderer(JSONRenderer):
    charset = 'utf-8'


class EnvelopedJSONRenderer(UnicodeJsonRenderer):
    def render(
        self,
        data: dict,
        accepted_media_type: Optional[str] = None,
        renderer_context: Optional[dict] = None,
    ) -> bytes:
        if renderer_context and renderer_context['response'].status_code < 400:
            if data and 'data' in data:
                # data is already enveloped (eg after pagination)
                enveloped_data: dict = {'status': 'ok', **data}
            else:
                enveloped_data = {'status': 'ok', 'data': data}
        else:
            enveloped_data = {'status': 'error', 'error': data}
        return super().render(enveloped_data, accepted_media_type, renderer_context)
