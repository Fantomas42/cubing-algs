"""Constants for scramble generation."""
import re
from random import Random
from typing import Final

from cubing_algs.annotations import RegexPattern
from cubing_algs.constants import FACE_ORDER

FACE_REGEXP: RegexPattern = re.compile(rf"({ '|'.join(FACE_ORDER) })")

MOVES_EASY_CROSS: Final[list[str]] = [
    'F',
    'R',
    'B',
    'L',
]

MOVES_AUF: Final[list[str]] = [
    '',
    'U',
    'U2',
    "U'",
]

EXCLUDE_ODD_FACES_RH: Final[set[str]] = {'D', 'L', 'B'}
EXCLUDE_ODD_FACES_LH: Final[set[str]] = {'D', 'R', 'B'}

DEFAULT_RNG: Final[Random] = Random()  # noqa: S311
