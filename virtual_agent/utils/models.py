from enum import Enum
from typing import Any

from funcy import lpluck_attr


class ChoicesEnum(Enum):
    """
    Use it like that:

    class MyChoices(int, ChoicesEnum):
        ONE = 1, 'This is the one'
    """

    def __new__(cls, value: Any, description: str = '') -> 'ChoicesEnum':
        obj = type(value).__new__(cls, value)  # type: ignore
        obj.description = description  # type: ignore

        # otherwise Enum will try to set it to value tuple
        # and will fail, because tuple can't be parsed as type of value
        obj._value_ = value  # type: ignore

        # mypy complains that obj has type 'type', but it should be ChoicesEnum;
        # dunno what to do with that, have to ignore it
        return obj  # type: ignore

    @classmethod
    def choices(cls) -> list[tuple[Any, str]]:
        return [(value.value, value.description) for value in cls]  # type: ignore

    @classmethod
    def values(cls) -> list:
        return lpluck_attr('value', cls)
