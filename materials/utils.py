from typing import Optional

from virtual_agent.utils import ChoicesEnum

from .models import MaterialTypes

MIMETYPE_TO_FILE_TYPE_MAPPING = {
    'video/mp4': MaterialTypes.VIDEO,
    (
        'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ): MaterialTypes.PRESENTATION,
    'application/pdf': MaterialTypes.PDF,
}


class MoodleMaterialTypes(str, ChoicesEnum):
    QUIZ = 'quiz', 'Квиз'
    TEXT = 'page', 'Текст'
    FILE = 'resource', 'Файл'


def get_material_type(
    material_type: MoodleMaterialTypes, contents_info: Optional[dict] = None
) -> str:
    if material_type == MoodleMaterialTypes.QUIZ:
        return MaterialTypes.QUIZ
    if material_type == MoodleMaterialTypes.TEXT:
        return MaterialTypes.TEXT
    if material_type == MoodleMaterialTypes.FILE:
        mimetype = contents_info['mimetypes'][0]
        file_type = MIMETYPE_TO_FILE_TYPE_MAPPING.get(mimetype)
        return file_type or MaterialTypes.OTHER
    return MaterialTypes.OTHER
