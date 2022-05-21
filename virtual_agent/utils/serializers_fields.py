from typing import Any

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from humanize import naturalsize
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import FileField


class ValidatedFileField(FileField):
    def __init__(
        self,
        max_file_size: int = settings.MAX_FILE_SIZE_IN_BYTES,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.max_size = max_file_size
        super().__init__(*args, **kwargs)

    def get_validators(self) -> list:
        base_validators = super().get_validators()
        return base_validators + [self._validate_size]

    def _validate_size(self, data: InMemoryUploadedFile) -> None:
        if data.size > self.max_size:
            readable_limit = naturalsize(self.max_size, binary=True)
            raise ValidationError(f'File size should be less than {readable_limit}')
