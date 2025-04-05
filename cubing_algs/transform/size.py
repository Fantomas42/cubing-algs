def compress_moves(old_moves: list[str]) -> list[str]:
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


def expand_moves(old_moves: list[str]) -> list[str]:
    moves: list[str] = []
    for move in old_moves:
        if move.endswith('2'):
            moves.extend((move[:-1], move[:-1]))
        else:
            moves.append(move)

    return moves
