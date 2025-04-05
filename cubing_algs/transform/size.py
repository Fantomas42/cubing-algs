from cubing_algs.move import Move
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves
from cubing_algs.transform.optimize import optimize_repeat_three_moves
from cubing_algs.transform.optimize import optimize_triple_moves


def compress_moves(old_moves: list[Move]) -> list[Move]:
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


def expand_moves(old_moves: list[Move]) -> list[Move]:
    moves: list[Move] = []

    for move in old_moves:
        if move.is_double:
            moves.extend((move.doubled, move.doubled))
        else:
            moves.append(move)

    return moves
