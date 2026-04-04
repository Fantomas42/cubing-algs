"""AUF (Adjust U Face) transformations for optimizing last layer adjustments."""
from collections.abc import Callable
from collections.abc import Iterable
from functools import partial
from itertools import takewhile

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import AUF_CHAR
from cubing_algs.move import Move
from cubing_algs.transform.offset import offset_moves
from cubing_algs.transform.trim import trim_moves

OFFSET_MAP: dict[int, Callable[[Algorithm], Algorithm]] = {
    1: partial(offset_moves, rotation="y'"),
    2: partial(offset_moves, rotation='y', count=2),
    3: partial(offset_moves, rotation='y'),
}


def get_move_score(move: Move) -> int:
    """
    Calculate the numeric score for a move for AUF calculations.

    Args:
        move: The move to score.

    Returns:
        Numeric score (2 for double, -1 for CCW, 1 for CW, 0 for pause).

    """
    if move.is_double:
        return 2
    if move.is_counter_clockwise:
        return -1
    if move.is_clockwise:
        return 1
    return 0


def is_auf_or_pause(move: Move) -> bool:
    """
    Check if a move is an AUF move or pause.

    Args:
        move: The move to check.

    Returns:
        True if the move is AUF or pause.

    """
    return move.base_move == AUF_CHAR or move.is_pause


def calculate_auf_score(moves: Iterable[Move]) -> int:
    """
    Calculate the total AUF score for a sequence of moves.

    Args:
        moves: Sequence of moves to score.

    Returns:
        Total AUF score.

    """
    return sum(
        get_move_score(move)
        for move in takewhile(is_auf_or_pause, moves)
    )


def remove_auf_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove AUF (Adjust Upper Face) moves from an algorithm.

    Args:
        old_moves: The algorithm to process.

    Returns:
        Algorithm with AUF moves removed.

    """
    if not old_moves:
        return old_moves

    score = (
        calculate_auf_score(old_moves) +
        calculate_auf_score(reversed(old_moves))
    ) % 4

    transforms = [trim_moves(AUF_CHAR)]
    if score:
        transforms.insert(0, OFFSET_MAP[score])

    return old_moves.transform(*transforms)
