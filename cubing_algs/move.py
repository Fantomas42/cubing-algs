"""
Simple move object
"""
from collections import UserString
from functools import cached_property

from cubing_algs.constants import ALL_BASIC_MOVES
from cubing_algs.constants import DOUBLE_CHAR
from cubing_algs.constants import INNER_MOVES
from cubing_algs.constants import INVERT_CHAR
from cubing_algs.constants import JAPANESE_CHAR
from cubing_algs.constants import OUTER_MOVES
from cubing_algs.constants import OUTER_WIDE_MOVES
from cubing_algs.constants import ROTATIONS


class InvalidMoveError(Exception):
    pass


class Move(UserString):

    @cached_property
    def base_move(self):
        return self[0]

    @cached_property
    def is_valid(self):
        return self.base_move in ALL_BASIC_MOVES

    @cached_property
    def is_double(self):
        return DOUBLE_CHAR in self

    @cached_property
    def is_clockwise(self):
        return INVERT_CHAR not in self

    @cached_property
    def is_counter_clockwise(self):
        return not self.is_clockwise

    @cached_property
    def is_rotation_move(self):
        return self.base_move in ROTATIONS

    @cached_property
    def is_face_move(self):
        return not self.is_rotation_move

    @cached_property
    def is_inner_move(self):
        return self.base_move in INNER_MOVES

    @cached_property
    def is_outer_move(self):
        return self.base_move in OUTER_MOVES

    @cached_property
    def is_wide_move(self):
        return self.base_move in OUTER_WIDE_MOVES

    #### TODO

    def invert(self) -> 'Move':
        if self.endswith(INVERT_CHAR):
            return Move(self[:1])
        return Move(f'{ self }{ INVERT_CHAR }')

    # Japanisation

    @cached_property
    def is_japanese(self) -> bool:
        return JAPANESE_CHAR in self.lower()

    @cached_property
    def is_japanesable(self) -> bool:
        return (
            self[0].islower()
            and self[0] not in ROTATIONS
            and not self.is_japanese
        )

    def japanese(self) -> 'Move':
        return Move(
            f'{ self[0].upper() }{ JAPANESE_CHAR }{ self[1:] }',
        )

    def unjapanese(self) -> 'Move':
        return Move(
            f'{ self[0].lower() }{ self[2:] }',
        )
