"""Move optimization functions for reducing algorithm length and complexity."""
from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import MAX_ITERATIONS


def optimize_repeat_three_moves_inplace(
        moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R, R, R --> R' (in-place).

    Modifies *moves* directly. Callers are responsible for providing
    a copy when the original must be preserved.

    Args:
        moves: Algorithm to optimize in-place.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        The same Algorithm object, optimized.

    """
    if max_depth <= 0:
        return moves

    i = 0
    changed = False

    while i < len(moves) - 2:
        if (
            not moves[i].is_pause
            and moves[i].untimed == moves[i + 1].untimed == moves[i + 2].untimed
        ):
            moves[i:i + 3] = [moves[i + 2].inverted]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_repeat_three_moves_inplace(moves, max_depth - 1)

    return moves


def optimize_do_undo_moves_inplace(
        moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R R' --> <nothing> (in-place)
    R2 R2 --> <nothing> (in-place)
    R R R' R' --> <nothing> (in-place).

    Modifies *moves* directly. Callers are responsible for providing
    a copy when the original must be preserved.

    Args:
        moves: Algorithm to optimize in-place.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        The same Algorithm object, optimized.

    """
    if max_depth <= 0:
        return moves

    i = 0
    changed = False

    while i < len(moves) - 1:
        if (
            not moves[i].is_pause
            and moves[i].inverted.untimed == moves[i + 1].untimed
        ):
            moves[i:i + 2] = []
            changed = True
        else:
            i += 1

    if changed:
        return optimize_do_undo_moves_inplace(moves, max_depth - 1)

    return moves


def optimize_double_moves_inplace(
        moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R, R --> R2 (in-place).

    Modifies *moves* directly. Callers are responsible for providing
    a copy when the original must be preserved.

    Args:
        moves: Algorithm to optimize in-place.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        The same Algorithm object, optimized.

    """
    if max_depth <= 0:
        return moves

    i = 0
    changed = False

    while i < len(moves) - 1:
        if (
            not moves[i].is_pause
            and not moves[i].is_double
            and moves[i].untimed == moves[i + 1].untimed
        ):
            moves[i:i + 2] = [moves[i + 1].doubled]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_double_moves_inplace(moves, max_depth - 1)

    return moves


def optimize_triple_moves_inplace(
        moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R, R2 --> R' (in-place)
    R2, R --> R' (in-place)
    R', R2 --> R (in-place).

    Modifies *moves* directly. Callers are responsible for providing
    a copy when the original must be preserved.

    Args:
        moves: Algorithm to optimize in-place.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        The same Algorithm object, optimized.

    """
    if max_depth <= 0:
        return moves

    i = 0
    changed = False

    while i < len(moves) - 1:
        if (
                not moves[i].is_pause
                and moves[i].base_move == moves[i + 1].base_move
                and moves[i].layer == moves[i + 1].layer
                and moves[i].is_wide_move == moves[i + 1].is_wide_move
        ):
            if moves[i].is_double and not moves[i + 1].is_double:
                moves[i:i + 2] = [moves[i + 1].inverted]
                changed = True
            elif not moves[i].is_double and moves[i + 1].is_double:
                moves[i:i + 2] = [moves[i].inverted]
                changed = True
            else:
                i += 1
        else:
            i += 1

    if changed:
        return optimize_triple_moves_inplace(moves, max_depth - 1)

    return moves


def optimize_repeat_three_moves(
        old_moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R, R, R --> R'.

    Args:
        old_moves: Algorithm to optimize.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        Optimized algorithm with triple repeats converted to inverse.

    """
    return optimize_repeat_three_moves_inplace(old_moves.copy(), max_depth)


def optimize_do_undo_moves(
        old_moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R R' --> <nothing>
    R2 R2 --> <nothing>
    R R R' R' --> <nothing>.

    Args:
        old_moves: Algorithm to optimize.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        Optimized algorithm with canceling move pairs removed.

    """
    return optimize_do_undo_moves_inplace(old_moves.copy(), max_depth)


def optimize_double_moves(
        old_moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R, R --> R2.

    Args:
        old_moves: Algorithm to optimize.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        Optimized algorithm with consecutive identical moves combined.

    """
    return optimize_double_moves_inplace(old_moves.copy(), max_depth)


def optimize_triple_moves(
        old_moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    R, R2 --> R'
    R2, R --> R'
    R', R2 --> R.

    Args:
        old_moves: Algorithm to optimize.
        max_depth: Maximum recursion depth for optimization.

    Returns:
        Optimized algorithm with move-double combinations simplified.

    """
    return optimize_triple_moves_inplace(old_moves.copy(), max_depth)
