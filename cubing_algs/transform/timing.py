from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm

if TYPE_CHECKING:
    from cubing_algs.move import Move  # pragma: no cover


def untime_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove timing information from all moves in an algorithm.
    """
    moves: list[Move] = [move.untimed for move in old_moves]

    return Algorithm(moves)
