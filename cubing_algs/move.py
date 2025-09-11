"""
Move representation for Rubik's cube algorithms.

This module defines the Move class, which represents a single move in a
Rubik's cube algorithm, along with properties to identify move types and
transformations between different notations.
"""
from collections import UserString
from functools import cached_property

from cubing_algs.constants import ALL_BASIC_MOVES
from cubing_algs.constants import DOUBLE_CHAR
from cubing_algs.constants import INNER_MOVES
from cubing_algs.constants import INVERT_CHAR
from cubing_algs.constants import LAYER_SPLIT
from cubing_algs.constants import OUTER_MOVES
from cubing_algs.constants import PAUSE_CHAR
from cubing_algs.constants import ROTATIONS
from cubing_algs.constants import WIDE_CHAR


class Move(UserString):
    """
    Represents a single move in a Rubik's cube algorithm.

    Extends UserString to provide string-like behavior while adding properties
    for move validation and transformation.
    A move consists of an optional layer impacted (such as 2, 3-4),
    a base move (letter) and optional modifiers (such as ', 2, w).

    Examples of valid moves: U, R', F2, Rw, M, x, 3-4Rw, 2F
    """

    # Parsing

    @cached_property
    def layer_move_modifier_time(self) -> tuple[str, str, str, str]:
        """
        Parse the move string into its component parts.
        """
        layer = ''
        move = ''
        modifier = ''
        time = ''

        layer_match = LAYER_SPLIT.match(self.data)
        if layer_match:
            layer = layer_match.groups()[1]

        kept = self.data[len(layer):]
        if '@' in self.data:
            kept, time = kept.split('@')
            time = f'@{ time }'

        if WIDE_CHAR in kept:
            move, modifier = kept.split(WIDE_CHAR, 1)
            move += WIDE_CHAR
        else:
            move = kept[0]
            modifier = kept[1:]

        return layer, move, modifier, time

    @cached_property
    def layer(self) -> str:
        """
        Extract the layers impacted.
        """
        return self.layer_move_modifier_time[0]

    @cached_property
    def layers(self) -> list[int]:
        """
        List of impacted layers, 0-indexed.
        """
        if not self.layer:
            if self.is_wide_move:
                return [0, 1]
            return [0]
        if '-' not in self.layer:
            if self.is_wide_move:
                return list(range(int(self.layer)))
            return [int(self.layer) - 1]

        start, end = self.layer.split('-', 1)

        return list(range(int(start) - 1, int(end)))

    @cached_property
    def base_move(self) -> str:
        """
        Extract the base letter of the move without modifiers.

        For standard notation, returns the first character.
        For SiGN notation, returns the uppercase of the move.
        """
        if self.is_sign_move:
            return self.raw_base_move[0].upper()
        return self.raw_base_move[0]

    @cached_property
    def raw_base_move(self) -> str:
        """
        Extract the base letter of the move without modifiers
        keeping original notation.

        For standard notation, returns the two first character.
        For SiGN notation, returns the first character.
        """
        return self.layer_move_modifier_time[1]

    @cached_property
    def modifier(self) -> str:
        """
        Extract the modifier part of the move.

        This includes rotation direction (' for counterclockwise) or
        repetition (2 for double moves).
        """
        return self.layer_move_modifier_time[2]

    @cached_property
    def time(self) -> str:
        """
        Extract the time part of the move.
        """
        return self.layer_move_modifier_time[3]

    @cached_property
    def timed(self) -> int | None:
        """
        Integer version of the timed move
        """
        if self.time:
            return int(self.time[1:])
        return None

    # Validation

    @cached_property
    def is_valid_layer(self) -> bool:
        """
        Check if the layer is valid.

        Validates that the layer is effective and valid.
        """
        if not self.is_layered:
            return True

        if '-' in self.layer and not self.is_wide_move:
            return False

        return not len(self.layer.split('-')) > 2

    @cached_property
    def is_valid_move(self) -> bool:
        """
        Check if the base move is valid.

        Validates that the move letter is one of the recognized basic moves.
        """
        if self.is_pause:
            return True

        if WIDE_CHAR in self.data and self.raw_base_move.islower():
            return False

        return self.base_move in ALL_BASIC_MOVES

    @cached_property
    def is_valid_modifier(self) -> bool:
        """
        Check if the modifier is valid.

        Valid modifiers include the invert character (')
        and the double character (2).
        """
        if not self.modifier:
            return True

        if len(self.modifier) > 1:
            return False

        return self.is_double or self.is_counter_clockwise

    @cached_property
    def is_valid(self) -> bool:
        """
        Check if the entire move is valid.

        A move is valid if both its base move and modifier are valid.
        """
        return (
            self.is_valid_layer
            and self.is_valid_move
            and self.is_valid_modifier
        )

    # Move

    @cached_property
    def is_pause(self) -> bool:
        """
        Determine if this is a Pause.

        Pause is a dot (.).
        """
        return self.base_move == PAUSE_CHAR

    @cached_property
    def is_rotation_move(self) -> bool:
        """
        Check if this is a cube rotation move.

        Rotation moves include x, y, and z, which rotate the entire cube.
        """
        return self.base_move in ROTATIONS

    @cached_property
    def is_face_move(self) -> bool:
        """
        Check if this is a face move.

        Face moves are moves that turn a face or slice of the cube,
        as opposed to rotating the entire cube.
        """
        return not self.is_pause and not self.is_rotation_move

    @cached_property
    def is_inner_move(self) -> bool:
        """
        Check if this is an inner slice move.

        Inner slice moves include M, E, and S, which turn the middle slices.
        """
        return self.base_move in INNER_MOVES

    @cached_property
    def is_outer_move(self) -> bool:
        """
        Check if this is an outer face move.

        Outer face moves include U, D, L, R, F, and B,
        which turn the outer faces.
        """
        return self.base_move in OUTER_MOVES

    @cached_property
    def is_wide_move(self) -> bool:
        """
        Check if this is a wide move.

        Wide moves turn two layers at once, such as r, l, u, d, f, and b.
        """
        return self.is_sign_move or WIDE_CHAR in self.raw_base_move

    @cached_property
    def is_layered(self) -> bool:
        """
        Check if this is a layered move.

        Layered moves are moves with layer information, such as 3-4Rw, 3Fw2, u.
        """
        return bool(self.layer) or self.is_wide_move

    @cached_property
    def is_timed(self) -> bool:
        """
        Check if this is a timed move.

        Timed moves are moves with time information, separated by an @.
        """
        return bool(self.time)

    # Notation

    @cached_property
    def is_standard_move(self) -> bool:
        """
        Determine if this move uses Standard notation.
        """
        return not self.is_sign_move

    @cached_property
    def is_sign_move(self) -> bool:
        """
        Determine if this move uses SiGN notation.

        In SiGN notation, wide moves are written with a lower letter
        removing the 'w' (e.g., r instead of Rw).
        """
        if not self.data.islower():
            return False

        return all(char not in self.data for char in [WIDE_CHAR, *ROTATIONS])

    # Modifiers

    @cached_property
    def is_double(self) -> bool:
        """
        Check if this is a double move (180° turn).

        Double moves have a '2' modifier, like U2 or R2.
        """
        return self.modifier == DOUBLE_CHAR

    @cached_property
    def is_clockwise(self) -> bool:
        """
        Check if this is a clockwise move.

        Moves without the invert character (') are clockwise.
        """
        return not self.is_pause and self.modifier != INVERT_CHAR

    @cached_property
    def is_counter_clockwise(self) -> bool:
        """
        Check if this is a counter-clockwise move.

        Moves with the invert character (') are counter-clockwise.
        """
        return not self.is_pause and not self.is_clockwise

    # Transformations

    @cached_property
    def inverted(self) -> 'Move':
        """
        Get the inverted version of this move.

        For a clockwise move, returns the counter-clockwise version.
        For a counter-clockwise move, returns the clockwise version.
        Double moves remain unchanged when inverted.
        """
        if self.is_double or self.is_pause:
            return self

        if self.is_counter_clockwise:
            return Move(
                f'{ self.layer }'
                f'{ self.raw_base_move }'
                f'{ self.time }',
            )
        return Move(
            f'{ self.layer }'
            f'{ self.raw_base_move }'
            f'{ INVERT_CHAR }'
            f'{ self.time }',
        )

    @cached_property
    def doubled(self) -> 'Move':
        """
        Get the doubled version of this move.

        For a single move, returns the double version (180° turn).
        For a double move, returns the single version.
        """
        if self.is_pause:
            return self

        if self.is_double:
            return Move(
                f'{ self.layer }'
                f'{ self.raw_base_move }'
                f'{ self.time }',
            )
        return Move(
            f'{ self.layer }'
            f'{ self.raw_base_move }'
            f'{ DOUBLE_CHAR }'
            f'{ self.time }',
        )

    @cached_property
    def unlayered(self) -> 'Move':
        """
        Convert this move without layer information.

        This converts moves like 3Rw to Rw.
        """
        if self.is_layered:
            return Move(
                f'{ self.raw_base_move }'
                f'{ self.modifier }'
                f'{ self.time }',
            )
        return self

    @cached_property
    def untimed(self) -> 'Move':
        """
        Convert this move without time information.

        This converts moves like 3Rw@200 to 3Rw.
        """
        if self.is_timed:
            return Move(
                f'{ self.layer }'
                f'{ self.raw_base_move }'
                f'{ self.modifier }',
            )
        return self

    @cached_property
    def to_sign(self) -> 'Move':
        """
        Convert this move to SiGN notation.

        In SiGN notation, wide moves use lowercase letters.

        This converts moves like Rw to r.

        This only affects wide moves.
        """
        if self.is_wide_move and not self.is_sign_move:
            return Move(
                f'{ self.layer }'
                f'{ self.base_move.lower() }'
                f'{ self.modifier }'
                f'{ self.time }',
            )
        return self

    @cached_property
    def to_standard(self) -> 'Move':
        """
        Convert this move from SiGN notation to standard notation.

        This converts moves like r to Rw.

        This only affects wide moves.
        """
        if self.is_sign_move:
            return Move(
                f'{ self.layer }'
                f'{ self.base_move.upper() }{ WIDE_CHAR }'
                f'{ self.modifier }'
                f'{ self.time }',
            )
        return self
