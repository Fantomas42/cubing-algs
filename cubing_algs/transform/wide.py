"""Wide move expansion and contraction transformations."""

from collections.abc import Callable

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.constants import REWIDE_MOVES
from cubing_algs.constants import REWIDE_THRESHOLD
from cubing_algs.constants import UNWIDE_ROTATION_MOVES
from cubing_algs.constants import UNWIDE_SLICE_MOVES
from cubing_algs.move import Move


def unwide(
        old_moves: Algorithm,
        config: dict[str, list[str]],
) -> Algorithm:
    """
    Expand wide moves using the provided configuration mapping.

    Args:
        old_moves: Algorithm to process.
        config: Mapping of wide moves to their component move sequences.

    Returns:
        Algorithm with wide moves expanded to component moves.

    """
    moves: list[Move] = []

    move_cache: dict[Move, list[Move]] = {}
    for move_str, replacements in config.items():
        move_cache[Move(move_str)] = [Move(m) for m in replacements]

    for move in old_moves:
        move_untimed = move.untimed

        if move_untimed in config:
            if move.is_timed:
                moves.extend(
                    [
                        Move(x + move.time)
                        for x in move_cache[move_untimed]
                    ],
                )
            else:
                moves.extend(move_cache[move_untimed])
        else:
            moves.append(move)

    return Algorithm(moves)


def unwide_slice_moves(old_moves: Algorithm) -> Algorithm:
    """
    Expand wide moves into outer face and slice moves.

    Args:
        old_moves: Algorithm to process.

    Returns:
        Algorithm with wide moves converted to face and slice moves.

    """
    return unwide(old_moves, UNWIDE_SLICE_MOVES)


def unwide_rotation_moves(old_moves: Algorithm) -> Algorithm:
    """
    Expand wide moves into outer face and rotation moves.

    Args:
        old_moves: Algorithm to process.

    Returns:
        Algorithm with wide moves converted to face and rotation moves.

    """
    return unwide(old_moves, UNWIDE_ROTATION_MOVES)


def rewide(
        old_moves: Algorithm,
        config: dict[str, str],
        max_depth: int = MAX_ITERATIONS,
        threshold: int = 0,
) -> Algorithm:
    """
    Convert sequences of moves back into wide moves using configuration.

    Args:
        old_moves: Algorithm to process.
        config: Configuration mapping move pairs to wide moves.
        max_depth: Maximum recursion depth for optimization.
        threshold: Maximum time difference for grouping moves.

    Returns:
        Algorithm with move sequences converted to wide moves.

    """
    if max_depth <= 0:
        return old_moves

    i = 0
    moves: list[Move] = []
    changed = False

    while i < len(old_moves) - 1:
        current_move = old_moves[i]
        next_move = old_moves[i + 1]

        valid_threshold = True
        if (
                threshold
                and current_move.is_timed
                and next_move.is_timed
                and next_move.timed - current_move.timed > threshold
        ):
            valid_threshold = False

        wided = f'{ old_moves[i].untimed } { old_moves[i + 1].untimed }'
        if valid_threshold and wided in config:
            moves.append(Move(f'{ config[wided] }{ old_moves[i].time }'))
            changed = True
            i += 2
        else:
            moves.append(old_moves[i])
            i += 1

    if i < len(old_moves):
        moves.append(old_moves[i])

    if changed:
        return rewide(
            Algorithm(moves), config,
            max_depth - 1,
        )

    return Algorithm(moves)


def rewide_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert move sequences back into wide moves where possible.

    Args:
        old_moves: Algorithm to process.

    Returns:
        Algorithm with wide move patterns consolidated.

    """
    return rewide(old_moves, REWIDE_MOVES)


def rewide_timed_moves(
        threshold: int = REWIDE_THRESHOLD,
) -> Callable[[Algorithm], Algorithm]:
    """
    Create a timed reslicing function
    for all slice moves with configurable threshold.

    Args:
        threshold: Maximum time difference for grouping moves.

    Returns:
        Function that applies rewide with timing constraints.

    """

    def _rewide_timed_moves(old_moves: Algorithm) -> Algorithm:
        return rewide(old_moves, REWIDE_MOVES, threshold=threshold)

    return _rewide_timed_moves
