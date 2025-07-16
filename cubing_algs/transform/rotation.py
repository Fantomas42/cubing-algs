from cubing_algs.move import Move
from cubing_algs.transform.size import compress_moves


def remove_final_rotations(old_moves: list[Move]) -> list[Move]:
    moves = []

    rotation = True
    for move in reversed(old_moves):
        if rotation and (move.is_rotation_move or move.is_pause):
            continue
        rotation = False
        moves.append(move)

    return list(reversed(moves))


def compress_final_rotations(old_moves: list[Move]) -> list[Move]:
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
        return old_moves

    moves.reverse()
    rotations.reverse()

    rotations = compress_moves(rotations)

    return moves + rotations
