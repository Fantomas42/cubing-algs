"""Move trimming transformations for removing moves from algorithm ends."""

from collections.abc import Callable
from itertools import dropwhile

from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move


def trim_moves(
        trim_move: str,
        *, start: bool = True, end: bool = True,
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

        Args:
            old_moves: Algorithm to trim.

        Returns:
            Algorithm with specified moves removed from ends.

        """
        if not old_moves:
            return old_moves

        moves = list(old_moves.copy())

        def should_trim(m: Move) -> bool:
            """
            Check if a move should be trimmed based on criteria.

            Args:
                m: Move to check.

            Returns:
                True if the move should be trimmed, False otherwise.

            """
            return m.base_move == trim_move or m.is_pause

        if start:
            moves = list(
                dropwhile(should_trim, moves),
            )

        if end:
            moves = list(
                reversed(
                    list(
                        dropwhile(should_trim, reversed(moves)),
                    ),
                ),
            )

        return Algorithm(moves)

    return trimmer
