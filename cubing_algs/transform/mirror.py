from cubing_algs.move import Move


def mirror_moves(old_moves: list[Move]) -> list[Move]:
    """
    Create the mirror inverse of an algorithm.

    Reverses the order of moves and inverts each move to create
    the sequence that undoes the original algorithm.
    """
    moves = []
    for move in reversed(old_moves):
        moves.append(move.inverted)

    return moves
