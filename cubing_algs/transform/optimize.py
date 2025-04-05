def optimize_repeat_three_moves(old_moves: list[str]) -> list[str]:
    """ R, R, R --> R' """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 2:
        if moves[i] == moves[i + 1] == moves[i + 2]:
            moves[i:i + 3] = [invert(moves[i])]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_repeat_three_moves(moves)

    return moves


def optimize_do_undo_moves(old_moves: list[str]) -> list[str]:
    """ R R' --> <nothing>, R R R' R' --> <nothing> """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if invert(moves[i]) == moves[i + 1] or (
                moves[i] == moves[i + 1]
                and moves[i][-1] == '2'
                and moves[i + 1][-1] == '2'
        ):
            moves[i:i + 2] = []
            changed = True
        else:
            i += 1

    if changed:
        return optimize_do_undo_moves(moves)

    return moves


def optimize_double_moves(old_moves: list[str]) -> list[str]:
    """ R, R --> R2 """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if moves[i] == moves[i + 1]:
            moves[i:i + 2] = ['%s2' % moves[i][0]]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_double_moves(moves)

    return moves


def optimize_triple_moves(old_moves: list[str]) -> list[str]:
    """ R, R2 --> R' """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if moves[i][0] == moves[i + 1][0]:
            if moves[i][-1] == '2' and moves[i + 1][-1] != '2':
                moves[i:i + 2] = [invert(moves[i + 1])]
                changed = True
            elif moves[i][-1] != '2' and moves[i + 1][-1] == '2':
                moves[i:i + 2] = [invert(moves[i])]
                changed = True
            else:
                i += 1
        else:
            i += 1

    if changed:
        return optimize_triple_moves(moves)

    return moves
