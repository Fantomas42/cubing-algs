"""Algorithm inversion transformation for reversing move sequences."""
from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move


def invert_moves(old_moves: Algorithm) -> Algorithm:
    """
    Create the inverse of an algorithm.

    Reverses the order of moves and inverts each move to create
    the sequence that undoes the original algorithm.

    Timing information is preserved from the original positions.

    Args:
        old_moves: The algorithm to invert.

    Returns:
        A new Algorithm that is the inverse of the input.

    """
    times: list[str] = [
        move.time
        for move in old_moves
    ]
    inverted: list[Move] = [
        move.inverted.untimed
        for move in reversed(old_moves)
    ]

    moves: list[Move] = [
        Move(f'{ move }{ time }') if time else move
        for move, time in zip(inverted, times, strict=True)
    ]

    return Algorithm(moves)
