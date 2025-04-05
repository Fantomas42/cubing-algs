from cubing_algs.move import Move


def optimize_repeat_three_moves(old_moves: list[Move]) -> list[Move]:
    """ R, R, R --> R' """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 2:
        if moves[i] == moves[i + 1] == moves[i + 2]:
            moves[i:i + 3] = [moves[i].inverted]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_repeat_three_moves(moves)

    return moves


def optimize_do_undo_moves(old_moves: list[Move]) -> list[Move]:
    """ R R' --> <nothing>,
        R2 R2 --> <nothing>
        R R R' R' --> <nothing>
    """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if moves[i].inverted == moves[i + 1] or (
                moves[i] == moves[i + 1]
                and moves[i].is_double
        ):
            moves[i:i + 2] = []
            changed = True
        else:
            i += 1

    if changed:
        return optimize_do_undo_moves(moves)

    return moves


def optimize_double_moves(old_moves: list[Move]) -> list[Move]:
    """ R, R --> R2 """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if moves[i] == moves[i + 1]:
            moves[i:i + 2] = [moves[i].doubled]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_double_moves(moves)

    return moves


def optimize_triple_moves(old_moves: list[Move]) -> list[Move]:
    """ R, R2 --> R'
        R2, R --> R'
        R', R2 --> R
    """
    i = 0
    changed = False
    moves = list(old_moves)

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
        return optimize_triple_moves(moves)

    return moves


def compress_moves(old_moves: list[Move]) -> list[Move]:
    moves = list(old_moves)

    compressing = True
    while compressing:
        changed = False
        for optimizer in (
                optimize_do_undo_moves,
                optimize_repeat_three_moves,
                optimize_double_moves,
                optimize_triple_moves,
        ):
            new_moves = optimizer(moves)
            if new_moves != moves:
                moves = new_moves
                changed = True

        if not changed:
            compressing = False

    return moves
