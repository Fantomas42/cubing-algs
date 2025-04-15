from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.constants import RESLICE_E_MOVES
from cubing_algs.constants import RESLICE_M_MOVES
from cubing_algs.constants import RESLICE_MOVES
from cubing_algs.constants import RESLICE_S_MOVES
from cubing_algs.constants import UNSLICE_ROTATION_MOVES
from cubing_algs.constants import UNSLICE_WIDE_MOVES
from cubing_algs.move import Move


def unslice(old_moves: list[Move], config: dict[str, list[str]]) -> list[Move]:
    moves = []

    move_cache = {}
    for move_str, replacements in config.items():
        move_cache[move_str] = [Move(m) for m in replacements]

    for move in old_moves:
        move_str = str(move)
        if move_str in config:
            moves.extend(move_cache[move_str])
        else:
            moves.append(move)

    return moves


def unslice_wide_moves(old_moves: list[Move]) -> list[Move]:
    return unslice(old_moves, UNSLICE_WIDE_MOVES)


def unslice_rotation_moves(old_moves: list[Move]) -> list[Move]:
    return unslice(old_moves, UNSLICE_ROTATION_MOVES)


def reslice(
        old_moves: list[Move],
        mapping: dict[str, list[str]],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    if max_depth <= 0:
        return old_moves

    i = 0
    moves = []
    changed = False

    while i < len(old_moves) - 1:
        sliced = f'{ old_moves[i] } { old_moves[i + 1] }'
        if sliced in mapping:
            for move in mapping[sliced]:
                moves.append(Move(move))
            changed = True
            i += 2
        else:
            moves.append(old_moves[i])
            i += 1

    if i < len(old_moves):
        moves.append(old_moves[i])

    if changed:
        return reslice(moves, mapping, max_depth - 1)

    return moves


def reslice_m_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_M_MOVES)


def reslice_s_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_S_MOVES)


def reslice_e_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_E_MOVES)


def reslice_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_MOVES)
