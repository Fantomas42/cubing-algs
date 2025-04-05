def mirror_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in reversed(old_moves):
        if move.endswith("'"):
            moves.append(move.replace("'", ''))
        elif move.endswith('2'):
            moves.append(move)
        else:
            moves.append("%s'" % move)

    return moves
