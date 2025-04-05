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

    # Properties

    @cached_property
    def is_japanese_move(self) -> bool:
        return JAPANESE_CHAR in self.lower()

    @cached_property
    def base_move(self):
        return self[0]

    @cached_property
    def modifiers(self):
        if self.is_japanese_move:
            return self[2:]
        return self[1:]

    @cached_property
    def is_valid(self):
        return self.base_move in ALL_BASIC_MOVES

    @cached_property
    def is_double(self):
        return DOUBLE_CHAR in self.modifiers

    @cached_property
    def is_clockwise(self):
        return INVERT_CHAR not in self.modifiers

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

    # Modifiers

    @cached_property
    def inverted(self) -> 'Move':
        if self.is_counter_clockwise or self.is_double:
            return Move(self.base_move)
        return Move(f'{ self.base_move }{ INVERT_CHAR }')

    @cached_property
    def doubled(self) -> 'Move':
        if self.is_double:
            return Move(self.base_move)
        return Move(f'{ self.base_move }{ DOUBLE_CHAR }')

    @cached_property
    def japanesed(self) -> 'Move':
        if self.is_wide_move and not self.is_japanese_move:
            return Move(
                f'{ self.base_move.upper() }{ JAPANESE_CHAR }'
                f'{ self.modifiers }',
            )
        return self
