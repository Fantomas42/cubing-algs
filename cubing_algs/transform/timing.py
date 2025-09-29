from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move


def untime_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove timing information from all moves in an algorithm.
    """
    moves: list[Move] = []

    for move in old_moves:
        moves.append(move.untimed)

    return Algorithm(moves)
