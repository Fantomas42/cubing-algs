from cubing_algs.move import Move


def remove_final_rotations(old_moves: list[Move]) -> list[Move]:
    moves = []

    rotations = True
    for move in reversed(old_moves):
        if rotations and move.is_rotation_move:
            continue
        rotations = False
        moves.append(move)

    return list(reversed(moves))
