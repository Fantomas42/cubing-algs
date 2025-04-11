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
from cubing_algs.constants import JAPANESE_CHAR
from cubing_algs.constants import OUTER_BASIC_MOVES
from cubing_algs.constants import OUTER_MOVES
from cubing_algs.constants import OUTER_WIDE_MOVES
from cubing_algs.constants import ROTATIONS


class InvalidMoveError(Exception):
    """
    Exception raised when an invalid move notation is encountered.

    This can occur when parsing algorithms with incorrect or unsupported
    move notations.
    """


class Move(UserString):
    """
    Represents a single move in a Rubik's cube algorithm.

    Extends UserString to provide string-like behavior while adding properties
    for move validation and transformation.
    A move consists of a base move (letter) and
    optional modifiers (such as ', 2, w).

    Examples of valid moves: U, R', F2, Rw, M, x
    """

    # Parsing

    @cached_property
    def is_japanese_move(self) -> bool:
        """
        Determine if this move uses Japanese notation.

        In Japanese notation, wide moves are written with a capital letter
        followed by a lowercase 'w' (e.g., Rw instead of r).
        """
        if len(self) > 1:
            return JAPANESE_CHAR in self.data[1].lower()
        return False

    @cached_property
    def base_move(self) -> str:
        """
        Extract the base letter of the move without modifiers.

        For standard notation, returns the first character.
        For Japanese notation, returns the lowercase of the first character.
        """
        if self.is_japanese_move:
            return self.data[0].lower()
        return self.data[0]

    @cached_property
    def modifier(self) -> str:
        """
        Extract the modifier part of the move.

        This includes rotation direction (' for counterclockwise) or
        repetition (2 for double moves).
        """
        if self.is_japanese_move:
            return self.data[2:]
        return self.data[1:]

    # Validation

    @cached_property
    def is_valid_move(self) -> bool:
        """
        Check if the base move is valid.

        Validates that the move letter is one of the recognized basic moves.
        """
        if self.is_japanese_move:
            return self.data[0] in OUTER_BASIC_MOVES

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
        return self.is_valid_move and self.is_valid_modifier

    # Move

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
        return not self.is_rotation_move

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
        return self.base_move in OUTER_WIDE_MOVES

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
        return self.modifier != INVERT_CHAR

    @cached_property
    def is_counter_clockwise(self) -> bool:
        """
        Check if this is a counter-clockwise move.

        Moves with the invert character (') are counter-clockwise.
        """
        return not self.is_clockwise

    # Transformations

    @cached_property
    def inverted(self) -> 'Move':
        """
        Get the inverted version of this move.

        For a clockwise move, returns the counter-clockwise version.
        For a counter-clockwise move, returns the clockwise version.
        Double moves remain unchanged when inverted.
        """
        if self.is_double:
            return self
        if self.is_counter_clockwise:
            return Move(self.base_move)
        return Move(f'{ self.base_move }{ INVERT_CHAR }')

    @cached_property
    def doubled(self) -> 'Move':
        """
        Get the doubled version of this move.

        For a single move, returns the double version (180° turn).
        For a double move, returns the single version.
        """
        if self.is_double:
            return Move(self.base_move)
        return Move(f'{ self.base_move }{ DOUBLE_CHAR }')

    @cached_property
    def japanesed(self) -> 'Move':
        """
        Convert this move to Japanese notation.

        In Japanese notation, wide moves use uppercase letters
        with a 'w' suffix.
        This only affects wide moves.
        """
        if self.is_wide_move and not self.is_japanese_move:
            return Move(
                f'{ self.base_move.upper() }{ JAPANESE_CHAR }'
                f'{ self.modifier }',
            )
        return self

    @cached_property
    def unjapanesed(self) -> 'Move':
        """
        Convert this move from Japanese to standard notation.

        This converts moves like Rw to r.
        """
        if self.is_japanese_move:
            return Move(
                f'{ self.base_move.lower() }{ self.modifier }',
            )
        return self
