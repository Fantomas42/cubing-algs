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
from cubing_algs.constants import OUTER_BASIC_MOVES
from cubing_algs.constants import OUTER_MOVES
from cubing_algs.constants import OUTER_WIDE_MOVES
from cubing_algs.constants import ROTATIONS


class InvalidMoveError(Exception):
    pass


class Move(UserString):

    # Parsing

    @cached_property
    def is_japanese_move(self) -> bool:
        if len(self) > 1:
            return JAPANESE_CHAR in self[1].lower()
        return False

    @cached_property
    def base_move(self):
        if self.is_japanese_move:
            return self[0].lower()
        return self[0]

    @cached_property
    def modifier(self):
        if self.is_japanese_move:
            return self[2:]
        return self[1:]

    # Validation

    @cached_property
    def is_valid_move(self):
        if self.is_japanese_move:
            return self[0] in OUTER_BASIC_MOVES

        return self.base_move in ALL_BASIC_MOVES

    @cached_property
    def is_valid_modifier(self) -> bool:
        if not self.modifier:
            return True

        if len(self.modifier) > 1:
            return False

        return self.is_double or self.is_counter_clockwise

    @cached_property
    def is_valid(self) -> bool:
        return self.is_valid_move and self.is_valid_modifier

    # Move

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
    def is_double(self):
        return self.modifier == DOUBLE_CHAR

    @cached_property
    def is_clockwise(self):
        return self.modifier != INVERT_CHAR

    @cached_property
    def is_counter_clockwise(self):
        return not self.is_clockwise

    # Transformations

    @cached_property
    def inverted(self) -> 'Move':
        if self.is_double:
            return self
        if self.is_counter_clockwise:
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
                f'{ self.modifier }',
            )
        return self
