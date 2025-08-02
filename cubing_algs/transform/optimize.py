from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.move import Move


def optimize_repeat_three_moves(
        old_moves: list[Move],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    R, R, R --> R'
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    changed = False
    moves = old_moves.copy()

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
        return optimize_repeat_three_moves(moves, max_depth - 1)

    return moves


def optimize_do_undo_moves(
        old_moves: list[Move],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    R R' --> <nothing>
    R2 R2 --> <nothing>
    R R R' R' --> <nothing>
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    changed = False
    moves = old_moves.copy()

    while i < len(moves) - 1:
        if (
            (not moves[i].is_pause
             and moves[i].inverted.untimed == moves[i + 1].untimed) or (
                 moves[i].untimed == moves[i + 1].untimed
                 and moves[i].is_double
                 and not moves[i].is_pause
             )
        ):
            moves[i:i + 2] = []
            changed = True
        else:
            i += 1

    if changed:
        return optimize_do_undo_moves(moves, max_depth - 1)

    return moves


def optimize_double_moves(
        old_moves: list[Move],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    R, R --> R2
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    changed = False
    moves = old_moves.copy()

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
        return optimize_double_moves(moves, max_depth - 1)

    return moves


def optimize_triple_moves(
        old_moves: list[Move],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    R, R2 --> R'
    R2, R --> R'
    R', R2 --> R
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    changed = False
    moves = old_moves.copy()

    while i < len(moves) - 1:
        if moves[i].base_move == moves[i + 1].base_move:
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
        return optimize_triple_moves(moves, max_depth - 1)

    return moves
