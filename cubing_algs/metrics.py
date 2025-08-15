"""
Metrics and analysis tools for Rubik's cube algorithms.

This module provides functions to calculate various metrics
for evaluating and comparing Rubik's cube algorithms,
including different move counting systems (HTM, QTM, STM, etc.)
and algorithm composition analysis.
"""
import operator
from typing import Any

from cubing_algs.move import Move

# Dictionary mapping metric names to scoring rules for different move types
MOVE_COUNTS = {
    'htm': {'rotation': [0, 0], 'outer': [1, 0], 'inner': [2, 0]},
    'qtm': {'rotation': [0, 0], 'outer': [0, 1], 'inner': [0, 2]},
    'stm': {'rotation': [0, 0], 'outer': [1, 0], 'inner': [1, 0]},
    'etm': {'rotation': [1, 0], 'outer': [1, 0], 'inner': [1, 0]},
    'rtm': {'rotation': [0, 1], 'outer': [0, 0], 'inner': [0, 0]},
    'qstm': {'rotation': [0, 0], 'outer': [0, 1], 'inner': [0, 1]},
}


def amount(move: Move) -> int:
    """
    Determine the quantity factor for a move.

    Double moves (like U2) count as 2, while single moves count as 1.
    This is used for quarter-turn metrics.
    """
    if move.is_double:
        return 2
    return 1


def move_score(mode: str, field: str,
               moves: list[Move]) -> int:
    """
    Calculate the score for a specific group of moves under a given metric.

    Uses the MOVE_COUNTS dictionary to determine how to score each move
    based on the metric mode and move type.
    """
    datas = MOVE_COUNTS[mode][field]

    return sum(
        datas[0] + (amount(move) * datas[1])
        for move in moves
    )


def compute_score(mode: str,
                  rotations: list[Move],
                  outer: list[Move],
                  inner: list[Move]) -> int:
    """
    Compute the total score for an algorithm under a specific metric.

    Combines scores from all move types (rotations, outer, and inner moves)
    according to the rules of the specified metric.
    """
    return (
        move_score(mode, 'rotation', rotations)
        + move_score(mode, 'outer', outer)
        + move_score(mode, 'inner', inner)
    )


def compute_generators(moves: list[Move]) -> list[str]:
    """
    Identify the most frequently used move faces in an algorithm.

    This function counts how many times each face is turned (ignoring
    direction and whether it's a single or double turn) and returns them in
    order of frequency.
    Rotations are excluded from this analysis.
    """
    count: dict[str, int] = {}
    for move in moves:
        if move.is_rotation_move or move.is_pause:
            continue

        count.setdefault(move.raw_base_move, 0)
        count[move.raw_base_move] += 1

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
) -> tuple[list[Move], list[Move], list[Move], list[Move]]:
    """
    Categorize moves into pause, rotation, outer, and inner move types.

    This separation is necessary for accurate metric calculations, as different
    move types are counted differently depending on the metric.
    """
    pauses = []
    rotations = []
    outer_moves = []
    inner_moves = []

    for move in moves:
        if move.is_pause:
            pauses.append(move)
        elif move.is_outer_move:
            outer_moves.append(move)
        elif move.is_inner_move:
            inner_moves.append(move)
        else:
            rotations.append(move)

    return pauses, rotations, outer_moves, inner_moves


def compute_metrics(moves: list[Move]) -> dict[str, Any]:
    """
    Calculate a comprehensive set of metrics for an algorithm.

    This function computes various metrics including:
    - Move counts by type (rotations, outer moves, inner moves)
    - Standard metrics (HTM, QTM, STM, ETM, QSTM)
    - Generator analysis (most used faces)

    Returns:
        dict[str, Any]: A dictionary containing all calculated metrics.
        Keys include:
            - rotations: Number of rotation moves
            - outer_moves: Number of outer face moves
            - inner_moves: Number of inner slice moves
            - htm: Half Turn Metric score
            - qtm: Quarter Turn Metric score
            - stm: Slice Turn Metric score
            - etm: Execution Turn Metric score
            - rtm: Rotation Turn Metric score
            - qstm: Quarter Slice Turn Metric score
            - generators: List of most frequently used faces
    """
    pauses, rotations, outer_moves, inner_moves = regroup_moves(moves)

    return {
        'pauses': len(pauses),
        'rotations': len(rotations),
        'outer_moves': len(outer_moves),
        'inner_moves': len(inner_moves),
        'htm': compute_score('htm', rotations, outer_moves, inner_moves),
        'qtm': compute_score('qtm', rotations, outer_moves, inner_moves),
        'stm': compute_score('stm', rotations, outer_moves, inner_moves),
        'etm': compute_score('etm', rotations, outer_moves, inner_moves),
        'rtm': compute_score('rtm', rotations, outer_moves, inner_moves),
        'qstm': compute_score('qstm', rotations, outer_moves, inner_moves),
        'generators': compute_generators(moves),
    }
