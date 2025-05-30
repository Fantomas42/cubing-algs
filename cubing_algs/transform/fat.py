from cubing_algs.constants import MAX_ITERATIONS
from cubing_algs.constants import REFAT_MOVES
from cubing_algs.constants import UNFAT_MOVES
from cubing_algs.move import Move


def unfat_moves(
        old_moves: list[Move],
        config: dict[str, list[str]] = UNFAT_MOVES,
) -> list[Move]:
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


def refat_moves(
        old_moves: list[Move],
        config: dict[str, str] = REFAT_MOVES,
        max_depth: int = MAX_ITERATIONS,
) -> list[Move]:
    if max_depth <= 0:
        return old_moves

    i = 0
    moves = []
    changed = False

    while i < len(old_moves) - 1:
        fatted = f'{ old_moves[i] } { old_moves[i + 1] }'
        if fatted in config:
            for move in config[fatted]:
                moves.append(Move(move))
            changed = True
            i += 2
        else:
            moves.append(old_moves[i])
            i += 1

    if i < len(old_moves):
        moves.append(old_moves[i])

    if changed:
        return refat_moves(moves, config, max_depth - 1)

    return moves
