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
        move_untimed = move.untimed

        if move_untimed in config:
            if move.is_timed:
                moves.extend(
                    [
                        Move(x + move.time)
                        for x in move_cache[move_untimed]
                    ],
                )
            else:
                moves.extend(move_cache[move_untimed])
        else:
            moves.append(move)

    return moves


def unslice_wide_moves(old_moves: list[Move]) -> list[Move]:
    return unslice(old_moves, UNSLICE_WIDE_MOVES)


def unslice_rotation_moves(old_moves: list[Move]) -> list[Move]:
    return unslice(old_moves, UNSLICE_ROTATION_MOVES)


def reslice(
        old_moves: list[Move],
        config: dict[str, list[str]],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    if max_depth <= 0:
        return old_moves

    i = 0
    moves = []
    changed = False

    while i < len(old_moves) - 1:
        sliced = f'{ old_moves[i].untimed } { old_moves[i + 1].untimed }'
        if sliced in config:
            for move in config[sliced]:
                moves.append(Move(move + old_moves[i + 1].time))
            changed = True
            i += 2
        else:
            moves.append(old_moves[i])
            i += 1

    if i < len(old_moves):
        moves.append(old_moves[i])

    if changed:
        return reslice(moves, config, max_depth - 1)

    return moves


def reslice_m_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_M_MOVES)


def reslice_s_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_S_MOVES)


def reslice_e_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_E_MOVES)


def reslice_moves(old_moves: list[Move]) -> list[Move]:
    return reslice(old_moves, RESLICE_MOVES)
