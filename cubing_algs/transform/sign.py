"""SiGN notation conversion transformations for alternative move notation."""

from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm

if TYPE_CHECKING:
    from cubing_algs.move import Move  # pragma: no cover


def sign_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert an algorithm from standard notation to SiGN notation.

    Args:
        old_moves: The algorithm to convert.

    Returns:
        A new Algorithm in SiGN notation.

    """
    moves: list[Move] = [move.to_sign for move in old_moves]

    return Algorithm(moves)


def unsign_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert an algorithm from SiGN notation to standard notation.

    Args:
        old_moves: The algorithm to convert.

    Returns:
        A new Algorithm in standard notation.

    """
    moves: list[Move] = [move.to_standard for move in old_moves]

    return Algorithm(moves)
