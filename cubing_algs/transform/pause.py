from cubing_algs.move import Move


def unpause_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in old_moves:
        if not move.is_pause:
            moves.append(move)

    return moves
