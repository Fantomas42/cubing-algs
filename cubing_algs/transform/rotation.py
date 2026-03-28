"""Rotation move removal and manipulation transformations."""
from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

if TYPE_CHECKING:
    from cubing_algs.move import Move


def remove_rotations(old_moves: Algorithm) -> Algorithm:
    """
    Remove rotations from an algorithm.

    Strips rotation moves while preserving the core face moves.

    Args:
        old_moves: Algorithm to process.

    Returns:
        Algorithm with rotation moves removed.

    """
    moves: list[Move] = [
        move
        for move in old_moves
        if not move.is_rotation_move
    ]

    return Algorithm(moves)


def remove_starting_rotations(old_moves: Algorithm) -> Algorithm:
    """
    Remove starting rotations and pauses from an algorithm.

    Strips rotation moves and pauses from the beginning of the algorithm
    while preserving the core face moves.

    Args:
        old_moves: Algorithm to process.

    Returns:
        Algorithm with starting rotations and pauses removed.

    """
    moves: list[Move] = []

    rotation = True
    for move in old_moves:
        if rotation and (move.is_rotation_move or move.is_pause):
            continue
        rotation = False
        moves.append(move)

    return Algorithm(moves)


def remove_ending_rotations(old_moves: Algorithm) -> Algorithm:
    """
    Remove trailing rotations and pauses from an algorithm.

    Strips rotation moves and pauses from the end of the algorithm
    while preserving the core face moves.

    Args:
        old_moves: Algorithm to process.

    Returns:
        Algorithm with ending rotations and pauses removed.

    """
    moves: list[Move] = []

    rotation = True
    for move in reversed(old_moves):
        if rotation and (move.is_rotation_move or move.is_pause):
            continue
        rotation = False
        moves.append(move)

    return Algorithm(reversed(moves))


def split_moves_ending_rotations(
        old_moves: Algorithm,
) -> tuple[Algorithm, Algorithm]:
    """
    Split an algorithm into core moves and ending rotations.

    Separates the algorithm into two parts: the main moves and
    the trailing rotations and pauses.

    Args:
        old_moves: Algorithm to split.

    Returns:
        Tuple of (core moves, ending rotations).

    """
    moves: list[Move] = []
    rotations: list[Move] = []

    rotation = True
    for move in reversed(old_moves):
        if rotation and (move.is_rotation_move or move.is_pause):
            rotations.append(move)
            continue
        rotation = False
        moves.append(move)

    if not rotations:
        return old_moves, Algorithm()

    moves.reverse()
    rotations.reverse()

    return Algorithm(moves), Algorithm(rotations)


def compress_rotations(old_moves: Algorithm) -> Algorithm:
    """
    Compress a rotation sequence to its optimal form.

    Simulates the rotation sequence on a virtual cube, reads the
    resulting orientation, and returns the shortest equivalent
    rotation sequence (at most 2 moves).

    Args:
        old_moves: Algorithm containing rotation moves to compress.

    Returns:
        Compressed algorithm with the optimal rotation sequence.

    """
    if not old_moves:
        return old_moves

    rotation_moves = Algorithm(
        m.untimed for m in old_moves if m.is_rotation_move
    )

    if not rotation_moves:
        return old_moves

    cube = VCube()
    cube.rotate(rotation_moves, history=False)

    moves_str = ORIENTATION_FACE_MOVES[cube.orientation]
    return parse_moves(moves_str) if moves_str else Algorithm()


def compress_ending_rotations(old_moves: Algorithm) -> Algorithm:
    """
    Optimize ending rotations in an algorithm.

    Separates core moves from ending rotations, optimizes the rotations,
    and recombines them for a more efficient algorithm.

    Args:
        old_moves: Algorithm to process.

    Returns:
        Algorithm with optimized ending rotations.

    """
    moves, rotations = split_moves_ending_rotations(old_moves)

    if len(rotations) > 1:
        rotations = compress_rotations(rotations)

    return moves + rotations
