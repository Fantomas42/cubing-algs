from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move


def mirror_moves(old_moves: Algorithm) -> Algorithm:
    """
    Create the mirror inverse of an algorithm.

    Reverses the order of moves and inverts each move to create
    the sequence that undoes the original algorithm.
    """
    moves: list[Move] = []

    for move in reversed(old_moves):
        moves.append(move.inverted)

    return Algorithm(moves)
