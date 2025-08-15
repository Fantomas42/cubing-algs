from cubing_algs.move import Move


def sign_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in old_moves:
        moves.append(move.to_sign)

    return moves


def unsign_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in old_moves:
        moves.append(move.to_standard)

    return moves
