from collections.abc import Callable
from itertools import dropwhile

from cubing_algs.move import Move


def trim_moves(
        trim_move: str,
        start: bool = True, end: bool = True,  # noqa: FBT001, FBT002
) -> Callable[[list[Move]], list[Move]]:

    def trimmer(old_moves: list[Move]) -> list[Move]:
        if not old_moves:
            return []

        moves = old_moves.copy()

        def should_trim(m: Move) -> bool:
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

        return moves

    return trimmer
