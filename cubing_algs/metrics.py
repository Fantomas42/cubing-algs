import operator
from typing import Any

from cubing_algs.move import Move

MOVE_COUNTS = {
    'htm': {'rotation': [0, 0], 'outer': [1, 0], 'inner': [2, 0]},
    'qtm': {'rotation': [0, 0], 'outer': [0, 1], 'inner': [0, 2]},
    'stm': {'rotation': [0, 0], 'outer': [1, 0], 'inner': [1, 0]},
    'etm': {'rotation': [1, 0], 'outer': [1, 0], 'inner': [1, 0]},
    'qstm': {'rotation': [0, 0], 'outer': [0, 1], 'inner': [0, 1]},
}


def amount(move: Move) -> int:
    if move.is_double:
        return 2
    return 1


def move_score(mode: str, field: str,
               moves: list[Move]) -> int:
    datas = MOVE_COUNTS[mode][field]

    return sum(
        datas[0] + (amount(move) * datas[1])
        for move in moves
    )


def compute_score(mode: str,
                  rotations: list[Move],
                  outer: list[Move],
                  inner: list[Move]) -> int:
    return (
        move_score(mode, 'rotation', rotations)
        + move_score(mode, 'outer', outer)
        + move_score(mode, 'inner', inner)
    )


def compute_generators(moves: list[Move]) -> list[Move]:
    count: dict[str, int] = {}
    for move in moves:
        if move.is_rotation_move:
            continue

        count.setdefault(move.base_move, 0)
        count[move.base_move] += 1

    return [
        k
        for k, v in sorted(
                count.items(),
                key=operator.itemgetter(1),
                reverse=True,
        )
    ]


def regroup_moves(
        moves: list[Move],
) -> tuple[list[Move], list[Move], list[Move]]:
    rotations = []
    outer_moves = []
    inner_moves = []

    for move in moves:
        if move.is_outer_move:
            outer_moves.append(move)
        elif move.is_inner_move:
            inner_moves.append(move)
        else:
            rotations.append(move)

    return rotations, outer_moves, inner_moves


def compute_metrics(moves: list[Move]) -> dict[str, Any]:
    rotations, outer_moves, inner_moves = regroup_moves(moves)

    return {
        'rotations': len(rotations),
        'outer_moves': len(outer_moves),
        'inner_moves': len(inner_moves),
        'htm': compute_score('htm', rotations, outer_moves, inner_moves),
        'qtm': compute_score('qtm', rotations, outer_moves, inner_moves),
        'stm': compute_score('stm', rotations, outer_moves, inner_moves),
        'etm': compute_score('etm', rotations, outer_moves, inner_moves),
        'qstm': compute_score('qstm', rotations, outer_moves, inner_moves),
        'generators': compute_generators(moves),
    }
