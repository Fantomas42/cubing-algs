from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.constants import REFAT_MOVES
from cubing_algs.constants import UNFAT_ROTATION_MOVES
from cubing_algs.constants import UNFAT_SLICE_MOVES
from cubing_algs.move import Move


def unfat(
        old_moves: list[Move],
        config: dict[str, list[str]],
) -> list[Move]:
    moves = []

    move_cache: dict[Move, list[Move]] = {}
    for move_str, replacements in config.items():
        move_cache[Move(move_str)] = [Move(m) for m in replacements]

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


def unfat_slice_moves(old_moves: list[Move]) -> list[Move]:
    return unfat(old_moves, UNFAT_SLICE_MOVES)


def unfat_rotation_moves(old_moves: list[Move]) -> list[Move]:
    return unfat(old_moves, UNFAT_ROTATION_MOVES)


def refat(
        old_moves: list[Move],
        config: dict[str, str],
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    if max_depth <= 0:
        return old_moves

    i = 0
    moves = []
    changed = False

    while i < len(old_moves) - 1:
        fatted = f'{ old_moves[i].untimed } { old_moves[i + 1].untimed }'
        if fatted in config:
            moves.append(Move(f'{ config[fatted] }{ old_moves[i].time }'))
            changed = True
            i += 2
        else:
            moves.append(old_moves[i])
            i += 1

    if i < len(old_moves):
        moves.append(old_moves[i])

    if changed:
        return refat(moves, config, max_depth - 1)

    return moves


def refat_moves(old_moves: list[Move]) -> list[Move]:
    return refat(old_moves, REFAT_MOVES)
