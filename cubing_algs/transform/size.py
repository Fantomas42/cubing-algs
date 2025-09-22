from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.move import Move
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves
from cubing_algs.transform.optimize import optimize_repeat_three_moves
from cubing_algs.transform.optimize import optimize_triple_moves


def compress_moves(
        old_moves: list[Move],
        max_iterations: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    Optimize an algorithm by applying move compression techniques.

    Repeatedly applies optimization functions to reduce the number of moves
    by eliminating redundancies and combining moves.
    """
    moves = old_moves.copy()

    for _ in range(max_iterations):
        start_length = len(moves)

        for optimizer in (
            optimize_do_undo_moves,
            optimize_repeat_three_moves,
            optimize_double_moves,
            optimize_triple_moves,
        ):
            moves = optimizer(moves)

        if len(moves) == start_length:
            break

    return moves


def expand_moves(old_moves: list[Move]) -> list[Move]:
    """
    Expand an algorithm by converting double moves to two single moves.

    Replaces each double move (like R2) with two identical single moves (R R).
    """
    moves: list[Move] = []

    for move in old_moves:
        if move.is_double:
            moves.extend((move.doubled, move.doubled))
        else:
            moves.append(move)

    return moves
