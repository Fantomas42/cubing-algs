from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.move import Move
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves
from cubing_algs.transform.optimize import optimize_repeat_three_moves
from cubing_algs.transform.optimize import optimize_triple_moves

CANCEL_TRIPLET = {'x2', 'y2', 'z2'}


def remove_final_rotations(old_moves: list[Move]) -> list[Move]:
    moves = []

    rotation = True
    for move in reversed(old_moves):
        if rotation and (move.is_rotation_move or move.is_pause):
            continue
        rotation = False
        moves.append(move)

    return list(reversed(moves))


def optimize_triple_rotations(
        old_moves: list[Move],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    x2, y2, z2 --> <nothing>
    x2, z2, y2 --> <nothing>
    z2, x2, y2 --> <nothing>
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
        old_moves: list[Move],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    x2, y2 --> z2
    x2, z2 --> y2
    y2, z2 --> x2
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
        old_moves: list[Move],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    """
    x, y2, x' --> z2
    x', y2, x --> z2
    x, z2, x' --> y2
    y, z2, y' --> x2
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


def split_moves_final_rotations(
        old_moves: list[Move],
) -> tuple[list[Move], list[Move]]:
    moves = []
    rotations = []

    rotation = True
    for move in reversed(old_moves):
        if rotation and (move.is_rotation_move or move.is_pause):
            rotations.append(move)
            continue
        rotation = False
        moves.append(move)

    if not rotations:
        return old_moves, []

    moves.reverse()
    rotations.reverse()

    return moves, rotations


def compress_rotations(
        old_moves: list[Move],
        max_iterations: int = MAX_ITERATIONS,
) -> list[Move]:
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


def compress_final_rotations(old_moves: list[Move]) -> list[Move]:
    moves, rotations = split_moves_final_rotations(old_moves)

    if len(rotations) > 1:
        rotations = compress_rotations(rotations)

    return moves + rotations
