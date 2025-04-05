def remove_final_rotations(old_moves: list[str]) -> list[str]:
    moves = []

    rotations = True
    for move in reversed(old_moves):
        if rotations and move[0] in ROTATIONS:
            continue
        rotations = False
        moves.append(move)

    return list(reversed(moves))
