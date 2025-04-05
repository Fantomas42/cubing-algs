def unslice_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in old_moves:
        if move in UNSLICE:
            moves.extend(UNSLICE[move])
        else:
            moves.append(move)

    return moves
