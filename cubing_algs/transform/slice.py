from collections.abc import Callable

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.constants import RESLICE_E_MOVES
from cubing_algs.constants import RESLICE_M_MOVES
from cubing_algs.constants import RESLICE_MOVES
from cubing_algs.constants import RESLICE_S_MOVES
from cubing_algs.constants import RESLICE_THRESHOLD
from cubing_algs.constants import UNSLICE_ROTATION_MOVES
from cubing_algs.constants import UNSLICE_WIDE_MOVES
from cubing_algs.move import Move


def unslice(old_moves: Algorithm, config: dict[str, list[str]]) -> Algorithm:
    """
    Convert slice moves to their component moves using configuration.
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


def unslice_wide_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert slice moves to wide moves.
    """
    return unslice(old_moves, UNSLICE_WIDE_MOVES)


def unslice_rotation_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert slice moves to outer face and rotation moves.
    """
    return unslice(old_moves, UNSLICE_ROTATION_MOVES)


def try_match_pattern(
        pattern: str,
        config: dict[str, list[str]]) -> list[str] | None:
    """
    Try to match a pattern against the config, checking both the original
    pattern and its normalized (sorted) form.
    """
    # First try exact match
    if pattern in config:
        return config[pattern]

    # Try normalized match (sorted alphabetically)
    moves = pattern.split()
    normalized = ' '.join(sorted(moves))
    if normalized in config:
        return config[normalized]

    return None


def is_within_threshold(
        moves_to_check: list[Move],
        threshold: int) -> bool:
    """
    Check if consecutive moves are within the threshold time.

    Returns True if threshold is 0, or if all consecutive moves
    are within the threshold time.
    """
    if not threshold:
        return True

    for i in range(len(moves_to_check) - 1):
        current = moves_to_check[i]
        next_move = moves_to_check[i + 1]
        if (
            current.is_timed
            and next_move.is_timed
            and abs(next_move.timed - current.timed) > threshold
        ):
            return False

    return True


def try_match_n_moves(
        old_moves: Algorithm,
        start_index: int,
        n: int,
        config: dict[str, list[str]],
        threshold: int) -> list[str] | None:
    """
    Try to match n consecutive moves starting at start_index.

    Returns the matched replacement moves if found, None otherwise.
    """
    if start_index + n > len(old_moves):
        return None

    moves_to_check = [old_moves[i] for i in range(start_index, start_index + n)]

    if not is_within_threshold(moves_to_check, threshold):
        return None

    pattern = ' '.join(str(move.untimed) for move in moves_to_check)
    return try_match_pattern(pattern, config)


def reslice(
        old_moves: Algorithm,
        config: dict[str, list[str]],
        max_depth: int = MAX_ITERATIONS,
        threshold: int = 0,
) -> Algorithm:
    """
    Convert move combinations back to slice moves using configuration.

    Patterns are matched in an order-independent way, so the config only
    needs to store one canonical ordering of each pattern.
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    moves: list[Move] = []
    changed = False

    while i < len(old_moves):
        # Try 3-move pattern first, then 2-move pattern
        for pattern_length in (3, 2):
            matched = try_match_n_moves(
                old_moves, i, pattern_length, config, threshold,
            )
            if matched:
                for move in matched:
                    moves.append(Move(move + old_moves[i].time))
                changed = True
                i += pattern_length
                break
        else:
            # No pattern matched, just add the current move
            moves.append(old_moves[i])
            i += 1

    if changed:
        return reslice(
            Algorithm(moves), config,
            max_depth - 1, threshold,
        )

    return Algorithm(moves)


def reslice_m_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert move combinations back to M slice moves.
    """
    return reslice(old_moves, RESLICE_M_MOVES)


def reslice_s_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert move combinations back to S slice moves.
    """
    return reslice(old_moves, RESLICE_S_MOVES)


def reslice_e_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert move combinations back to E slice moves.
    """
    return reslice(old_moves, RESLICE_E_MOVES)


def reslice_moves(old_moves: Algorithm) -> Algorithm:
    """
    Convert move combinations back to all slice moves.
    """
    return reslice(old_moves, RESLICE_MOVES)


def reslice_m_timed_moves(
        threshold: int = RESLICE_THRESHOLD,
) -> Callable[[Algorithm], Algorithm]:
    """
    Create a timed M-slice reslicing function with configurable threshold.
    """

    def _reslice_timed_moves(old_moves: Algorithm) -> Algorithm:
        return reslice(old_moves, RESLICE_M_MOVES, threshold=threshold)

    return _reslice_timed_moves


def reslice_s_timed_moves(
        threshold: int = RESLICE_THRESHOLD,
) -> Callable[[Algorithm], Algorithm]:
    """
    Create a timed S-slice reslicing function with configurable threshold.
    """

    def _reslice_timed_moves(old_moves: Algorithm) -> Algorithm:
        return reslice(old_moves, RESLICE_S_MOVES, threshold=threshold)

    return _reslice_timed_moves


def reslice_e_timed_moves(
        threshold: int = RESLICE_THRESHOLD,
) -> Callable[[Algorithm], Algorithm]:
    """
    Create a timed E-slice reslicing function with configurable threshold.
    """
    def _reslice_timed_moves(old_moves: Algorithm) -> Algorithm:
        return reslice(old_moves, RESLICE_E_MOVES, threshold=threshold)

    return _reslice_timed_moves


def reslice_timed_moves(
        threshold: int = RESLICE_THRESHOLD,
) -> Callable[[Algorithm], Algorithm]:
    """
    Create a timed reslicing function
    for all slice moves with configurable threshold.
    """

    def _reslice_timed_moves(old_moves: Algorithm) -> Algorithm:
        return reslice(old_moves, RESLICE_MOVES, threshold=threshold)

    return _reslice_timed_moves
