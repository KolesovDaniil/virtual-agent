from typing import Optional

from django.core.files.uploadedfile import SimpleUploadedFile


def create_file(filename: str, extension: Optional[str]) -> SimpleUploadedFile:
    name = f'{filename}.{extension}'
    return SimpleUploadedFile(name, b'some_text', content_type='text/plain')
