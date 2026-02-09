"""Constants for scramble generation."""
from random import Random
from typing import Final

CROSS_DIFFICULTIES = {
    'easy': 3,
    'normal': 5,
    'hard': 7,
}

MOVES_AUF: Final[list[str]] = [
    '',
    'U',
    'U2',
    "U'",
]

EXCLUDE_ODD_FACES_RH: Final[set[str]] = {'D', 'L', 'B'}
EXCLUDE_ODD_FACES_LH: Final[set[str]] = {'D', 'R', 'B'}

DEFAULT_RNG: Final[Random] = Random()  # noqa: S311
