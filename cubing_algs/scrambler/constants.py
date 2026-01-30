"""Constants for scramble generation."""
import re
from random import Random

from cubing_algs.constants import FACE_ORDER

FACE_REGEXP = re.compile(rf"({ '|'.join(FACE_ORDER) })")

MOVES_EASY_CROSS = [
    'F',
    'R',
    'B',
    'L',
]

EXCLUDE_ODD_FACES_RH = {'D', 'L', 'B'}
EXCLUDE_ODD_FACES_LH = {'D', 'R', 'B'}

DEFAULT_RNG = Random()  # noqa: S311
