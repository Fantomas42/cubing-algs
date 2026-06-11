"""Move trimming transformations for removing moves from algorithm ends."""
from collections.abc import Callable

from cubing_algs.algorithm import Algorithm


def find_trim_start(
        old_moves: Algorithm,
        trim_move: str,
        lo: int,
        hi: int,
) -> int:
    """
    Find start boundary after trimming target moves and adjacent pauses.

    Scans forward from ``lo`` to ``hi``, consuming moves that match
    ``trim_move`` or are pauses.

    Returns:
        New start index if a target move was found, otherwise ``lo``.

    """
    i = lo
    has_target = False

    while i < hi:
        if old_moves[i].base_move == trim_move:
            has_target = True
            i += 1
        elif old_moves[i].is_pause:
            i += 1
        else:
            break

    return i if has_target else lo


def find_trim_end(
        old_moves: Algorithm,
        trim_move: str,
        lo: int,
        hi: int,
) -> int:
    """
    Find end boundary after trimming target moves and adjacent pauses.

    Scans backward from ``hi`` to ``lo``, consuming moves that match
    ``trim_move`` or are pauses.

    Returns:
        New end index if a target move was found, otherwise ``hi``.

    """
    i = hi
    has_target = False

    while i > lo:
        if old_moves[i - 1].base_move == trim_move:
            has_target = True
            i -= 1
        elif old_moves[i - 1].is_pause:
            i -= 1
        else:
            break

    return i if has_target else hi


def trim_moves(
        trim_move: str,
        *,
        start: bool = True,
        end: bool = True,
) -> Callable[[Algorithm], Algorithm]:
    """
    Remove specified moves from the start and/or end of an algorithm.

    Args:
        trim_move: Base move to trim (e.g., 'y').
        start: Whether to trim from the start.
        end: Whether to trim from the end.

    Returns:
        Function that trims the specified move from algorithm ends.

    """

    def trimmer(old_moves: Algorithm) -> Algorithm:
        """
        Apply the trimming logic to remove specified moves from ends.

        Pauses are only trimmed if the contiguous run at the edge contains
        at least one target move.

        Args:
            old_moves: Algorithm to trim.

        Returns:
            Algorithm with specified moves removed from ends.

        """
        if not old_moves:
            return old_moves

        lo = 0
        hi = len(old_moves)

        if start:
            lo = find_trim_start(old_moves, trim_move, lo, hi)

        if end:
            hi = find_trim_end(old_moves, trim_move, lo, hi)

        return Algorithm(old_moves.data[lo:hi])

    return trimmer
