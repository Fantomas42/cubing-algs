"""Shared tools move transformations."""
from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move


def expand_moves(
        old_moves: Algorithm,
        config: dict[str, list[str]],
) -> Algorithm:
    """
    Expand moves using the provided configuration mapping.

    Generic expansion function used by both unslice and unwide.

    Args:
        old_moves: Algorithm to process.
        config: Mapping of moves to their component move sequences.

    Returns:
        Algorithm with matched moves expanded to component moves.

    """
    moves: list[Move] = []

    move_cache: dict[str, list[Move]] = {}
    for move_str, replacements in config.items():
        move_cache[move_str] = [Move(m) for m in replacements]

    for move in old_moves:
        move_untimed = str(move.untimed)
        cached = move_cache.get(move_untimed)

        if cached is not None:
            if move.is_timed:
                moves.extend(
                    Move(x + move.time)
                    for x in cached
                )
            else:
                moves.extend(cached)
        else:
            moves.append(move)

    return Algorithm(moves)
