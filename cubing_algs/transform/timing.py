from cubing_algs.move import Move


def untime_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in old_moves:
        moves.append(move.untimed)

    return moves
