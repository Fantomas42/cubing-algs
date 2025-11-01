from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.move import Move
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves
from cubing_algs.transform.optimize import optimize_repeat_three_moves
from cubing_algs.transform.optimize import optimize_triple_moves

CANCEL_TRIPLET: set[str | Move] = {'x2', 'y2', 'z2'}


def remove_rotations(old_moves: Algorithm) -> Algorithm:
    """
    Remove rotations from an algorithm.

    Strips rotation moves while preserving the core face moves.
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
    """
    moves: list[Move] = []

    rotation = True
    for move in reversed(old_moves):
        if rotation and (move.is_rotation_move or move.is_pause):
            continue
        rotation = False
        moves.append(move)

    return Algorithm(reversed(moves))


def optimize_triple_rotations(
        old_moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    x2, y2, z2 --> <nothing>
    x2, z2, y2 --> <nothing>
    z2, x2, y2 --> <nothing>.
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    changed = False
    moves = old_moves.copy()

    while i < len(moves) - 2:
        triplet = {moves[i].untimed, moves[i + 1].untimed, moves[i + 2].untimed}
        if triplet == CANCEL_TRIPLET:
            moves[i:i + 3] = []
            changed = True
        else:
            i += 1

    if changed:
        return optimize_triple_rotations(moves, max_depth - 1)

    return moves


def optimize_double_rotations(
        old_moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    x2, y2 --> z2
    x2, z2 --> y2
    y2, z2 --> x2.
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    changed = False
    moves = old_moves.copy()

    while i < len(moves) - 1:
        one = moves[i].untimed
        two = moves[i + 1].untimed
        if (
            one != two
            and one.is_double
            and two.is_double
        ):
            missing_rotation = (CANCEL_TRIPLET - {one, two}).pop()
            moves[i:i + 2] = [Move(missing_rotation)]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_double_moves(moves, max_depth - 1)

    return moves


def optimize_conjugate_rotations(
        old_moves: Algorithm,
        max_depth: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    x, y2, x' --> z2
    x', y2, x --> z2
    x, z2, x' --> y2
    y, z2, y' --> x2.
    """
    if max_depth <= 0:
        return old_moves

    i = 0
    changed = False
    moves = old_moves.copy()

    while i < len(moves) - 2:
        one = moves[i].untimed
        two = moves[i + 1].untimed
        three = moves[i + 2].untimed
        if (
                two.is_double
                and one.base_move == three.base_move
                and not one.is_double
                and not three.is_double
                and one.modifier != three.modifier
        ):
            missing_rotation = (CANCEL_TRIPLET - {one.doubled, two}).pop()
            moves[i:i + 3] = [Move(missing_rotation)]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_double_moves(moves, max_depth - 1)

    return moves


def split_moves_ending_rotations(
        old_moves: Algorithm,
) -> tuple[Algorithm, Algorithm]:
    """
    Split an algorithm into core moves and ending rotations.

    Separates the algorithm into two parts: the main moves and
    the trailing rotations and pauses.
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


def compress_rotations(
        old_moves: Algorithm,
        max_iterations: int = MAX_ITERATIONS,
) -> Algorithm:
    """
    Optimize rotation sequences by applying compression techniques.

    Applies various optimization functions specifically designed
    for rotation moves to reduce redundancy.
    """
    moves = old_moves.copy()

    for _ in range(max_iterations):
        start_length = len(moves)

        for optimizer in (
                optimize_do_undo_moves,
                optimize_repeat_three_moves,
                optimize_double_moves,
                optimize_triple_moves,
                optimize_conjugate_rotations,
                optimize_double_rotations,
                optimize_triple_rotations,
        ):
            moves = optimizer(moves)

        if len(moves) == start_length:
            break

    return moves


def compress_ending_rotations(old_moves: Algorithm) -> Algorithm:
    """
    Optimize ending rotations in an algorithm.

    Separates core moves from ending rotations, optimizes the rotations,
    and recombines them for a more efficient algorithm.
    """
    moves, rotations = split_moves_ending_rotations(old_moves)

    if len(rotations) > 1:
        rotations = compress_rotations(rotations)

    return moves + rotations
