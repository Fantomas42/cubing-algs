from cubing_algs.move import Move


def mirror_moves(old_moves: list[Move]) -> list[Move]:
    moves = []
    for move in reversed(old_moves):
        moves.append(move.inverted)

    return moves
