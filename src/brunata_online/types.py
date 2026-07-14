import enum
from typing import TypeAlias

JsonDict: TypeAlias = dict[str, object]
JsonData: TypeAlias = JsonDict | list[JsonDict]


class Interval(enum.StrEnum):
    """Interval representations"""
    HOUR = 'H'
    DAY = 'D'
    MONTH = 'M'
    YEAR = 'Y'


class Units(enum.IntEnum):
    """Unit representations"""
    SQUARE_METERS = 8
