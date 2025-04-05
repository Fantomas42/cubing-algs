from cubing_algs.move import Move


def japanese_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in old_moves:
        moves.append(move.japanesed)

    return moves


def unjapanese_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in old_moves:
        moves.append(move.unjapanesed)

    return moves
