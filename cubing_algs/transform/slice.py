from cubing_algs.constants import UNSLICE


def unslice_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in old_moves:
        if move in UNSLICE:
            moves.extend(UNSLICE[move])
        else:
            moves.append(move)

    return moves

def reslice_moves(old_moves: list[str]) -> list[str]:
    i = 0
    moves = []
    changed = False

    while i < len(old_moves) - 1:
        sliced = f'{ old_moves[i] } { old_moves[i + 1] }'
        if sliced in SLICES:
            moves.append(SLICES[sliced])
            changed = True
            i += 2
        else:
            moves.append(old_moves[i])
            i += 1

    moves.append(old_moves[i])

    if changed:
        return reslice_moves(moves)

    return moves
