from collections.abc import Callable

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import PAUSE_CHAR
from cubing_algs.move import Move


def unpause_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove all pause moves from an algorithm.
    """
    moves: list[Move] = []

    for move in old_moves:
        if not move.is_pause:
            moves.append(move)

    return Algorithm(moves)


def pause_moves(
        speed: int = 200, factor: int = 2,
        *, multiple: bool = False,
) -> Callable[[Algorithm], Algorithm]:
    """
    Create a configurable pause_moves function.
    """
    def _pause_moves(old_moves: Algorithm) -> Algorithm:
        if not old_moves:
            return old_moves

        if any(not m.is_timed for m in old_moves):
            return old_moves

        moves: list[Move] = []
        threshold = speed * factor

        previous_time = old_moves[0].timed
        assert previous_time is not None  # noqa: S101
        for move in old_moves:
            time = move.timed
            assert time is not None  # noqa: S101
            delta = time - previous_time

            if delta > threshold:
                if multiple:
                    delta = time - previous_time
                    occurences = int(delta / threshold)
                    offset = (delta - (threshold * occurences)) / 2

                    for i in range(occurences):
                        new_time = int(
                            previous_time + offset + (
                                (i + 1) * threshold
                            ),
                        )
                        moves.append(
                            Move(
                                f'{ PAUSE_CHAR }@{ new_time }',
                            ),
                        )
                    moves.append(move)
                else:
                    offset = int(delta / 2)

                    moves.extend(
                        [
                            Move(f'{ PAUSE_CHAR }@{ time - offset }'),
                            move,
                        ],
                    )
            else:
                moves.append(move)
            previous_time = time

        return Algorithm(moves)

    return _pause_moves
