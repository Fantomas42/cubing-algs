"""Mirror transformation for creating inverse algorithms."""

from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm

if TYPE_CHECKING:
    from cubing_algs.move import Move  # pragma: no cover


def mirror_moves(old_moves: Algorithm) -> Algorithm:
    """
    Create the mirror inverse of an algorithm.

    Reverses the order of moves and inverts each move to create
    the sequence that undoes the original algorithm.
    """
    moves: list[Move] = [move.inverted for move in reversed(old_moves)]

    return Algorithm(moves)
