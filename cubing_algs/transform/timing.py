"""Timing transformations for algorithm moves."""
from collections.abc import Callable

from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move


def time_moves(interval: int = 100) -> Callable[[Algorithm], Algorithm]:
    """
    Assign timing information to all moves in an algorithm.

    Each move receives an incrementing timestamp based on the interval.
    Already timed moves are re-timed with the new interval.

    Args:
        interval: Time in milliseconds between each move.

    Returns:
        Function that assigns timing to algorithm moves.

    """
    def _time_moves(old_moves: Algorithm) -> Algorithm:
        moves: list[Move] = [
            Move(f'{ move.untimed }@{ i * interval }')
            for i, move in enumerate(old_moves)
        ]

        return Algorithm(moves)

    return _time_moves


def untime_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove timing information from all moves in an algorithm.

    Args:
        old_moves: The algorithm to process.

    Returns:
        A new Algorithm with timing information removed from all moves.

    """
    moves: list[Move] = [move.untimed for move in old_moves]

    return Algorithm(moves)
