from cubing_algs.constants import RESLICE_MOVES
from cubing_algs.constants import UNSLICE_ROTATION_MOVES
from cubing_algs.constants import UNSLICE_WIDE_MOVES
from cubing_algs.move import Move


def unslice(old_moves: list[Move], config: dict[str, list[str]]) -> list[Move]:
    moves = []
    for _move in old_moves:
        move = str(_move)
        if move in config:
            for m in config[move]:
                moves.append(Move(m))
        else:
            moves.append(_move)

    return moves


def unslice_wide_moves(old_moves: list[Move]) -> list[Move]:
    return unslice(old_moves, UNSLICE_WIDE_MOVES)


def unslice_rotation_moves(old_moves: list[Move]) -> list[Move]:
    return unslice(old_moves, UNSLICE_ROTATION_MOVES)


def reslice_moves(old_moves: list[Move]) -> list[Move]:
    i = 0
    moves = []
    changed = False

    while i < len(old_moves) - 1:
        sliced = f'{ old_moves[i] } { old_moves[i + 1] }'
        if sliced in RESLICE_MOVES:
            for move in RESLICE_MOVES[sliced]:
                moves.append(Move(move))
            changed = True
            i += 2
        else:
            moves.append(old_moves[i])
            i += 1

    if i < len(old_moves):
        moves.append(old_moves[i])

    if changed:
        return reslice_moves(moves)

    return moves
