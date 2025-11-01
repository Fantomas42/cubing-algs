"""Cube rotation offset transformations for reorienting algorithms."""

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import OFFSET_TABLE
from cubing_algs.constants import WIDE_CHAR
from cubing_algs.move import Move


def rotate(old_moves: Algorithm, rotation: str) -> Algorithm:
    """
    Apply a rotation transformation to moves using the offset table.

    Transforms each move according to the specified rotation direction,
    maintaining move properties and notation style.
    """
    moves: list[Move] = []
    rotation_table: dict[str, str] = OFFSET_TABLE[rotation]

    for move in old_moves:
        layer = move.layer
        time = move.time
        base_move = move.base_move
        wide = WIDE_CHAR if move.is_wide_move else ''

        new_move = move

        if base_move in rotation_table:
            new_move = Move(
                layer + rotation_table[base_move] + wide + time,
            )
            if move.is_counter_clockwise:
                new_move = new_move.inverted
            elif move.is_double:
                new_move = new_move.doubled

            if move.is_sign_move:
                new_move = new_move.to_sign

        moves.append(new_move)

    return Algorithm(moves)


def offset_moves(
        old_moves: Algorithm,
        rotation: str,
        count: int = 1,
) -> Algorithm:
    """
    Apply a rotation transformation multiple times to an algorithm.

    Repeatedly applies the specified rotation to achieve the desired offset.
    """
    result = old_moves
    for _ in range(count):
        result = rotate(result, rotation)
    return result


def offset_x_moves(old_moves: Algorithm) -> Algorithm:
    """Apply x' rotation to moves."""
    return offset_moves(old_moves, "x'")


def offset_x2_moves(old_moves: Algorithm) -> Algorithm:
    """Apply x2 rotation to moves."""
    return offset_moves(old_moves, 'x', 2)


def offset_xprime_moves(old_moves: Algorithm) -> Algorithm:
    """Apply x rotation to moves."""
    return offset_moves(old_moves, 'x')


def offset_y_moves(old_moves: Algorithm) -> Algorithm:
    """Apply y' rotation to moves."""
    return offset_moves(old_moves, "y'")


def offset_y2_moves(old_moves: Algorithm) -> Algorithm:
    """Apply y2 rotation to moves."""
    return offset_moves(old_moves, 'y', 2)


def offset_yprime_moves(old_moves: Algorithm) -> Algorithm:
    """Apply y rotation to moves."""
    return offset_moves(old_moves, 'y')


def offset_z_moves(old_moves: Algorithm) -> Algorithm:
    """Apply z' rotation to moves."""
    return offset_moves(old_moves, "z'")


def offset_z2_moves(old_moves: Algorithm) -> Algorithm:
    """Apply z2 rotation to moves."""
    return offset_moves(old_moves, 'z', 2)


def offset_zprime_moves(old_moves: Algorithm) -> Algorithm:
    """Apply z rotation to moves."""
    return offset_moves(old_moves, 'z')
