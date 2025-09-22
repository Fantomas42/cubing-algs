from collections.abc import Callable
from typing import Any

from cubing_algs.algorithm import Algorithm
from cubing_algs.transform.offset import offset_x2_moves
from cubing_algs.transform.offset import offset_x_moves
from cubing_algs.transform.offset import offset_xprime_moves
from cubing_algs.transform.offset import offset_y2_moves
from cubing_algs.transform.offset import offset_y_moves
from cubing_algs.transform.offset import offset_yprime_moves
from cubing_algs.transform.offset import offset_z2_moves
from cubing_algs.transform.offset import offset_z_moves
from cubing_algs.transform.offset import offset_zprime_moves

DEGRIP_X: dict[str, Callable[[Algorithm], Algorithm]] = {
    'x': offset_xprime_moves,
    'x2': offset_x2_moves,
    "x'": offset_x_moves,
}

DEGRIP_Y: dict[str, Callable[[Algorithm], Algorithm]] = {
    'y': offset_yprime_moves,
    'y2': offset_y2_moves,
    "y'": offset_y_moves,
}

DEGRIP_Z: dict[str, Callable[[Algorithm], Algorithm]] = {
    'z': offset_zprime_moves,
    'z2': offset_z2_moves,
    "z'": offset_z_moves,
}


DEGRIP_FULL = {}
DEGRIP_FULL.update(DEGRIP_X)
DEGRIP_FULL.update(DEGRIP_Y)
DEGRIP_FULL.update(DEGRIP_Z)


def has_grip(
        old_moves: Algorithm,
        config: dict[str, Callable[[Algorithm], Algorithm]],
) -> tuple[bool, Any, Any, Any]:
    i = 0
    prefix = Algorithm()
    suffix = Algorithm()

    while i < len(old_moves) - 1:
        move = old_moves[i].untimed

        if move in config:
            suffix = old_moves[i + 1:]
            prefix = old_moves[:i]
            break

        i += 1

    config_keys = set(config.keys())
    if suffix and any(move not in config_keys for move in suffix):
        return True, prefix, suffix, move

    return False, False, False, False


def degrip(
        old_moves: Algorithm,
        config: dict[str, Callable[[Algorithm], Algorithm]],
) -> Algorithm:
    _gripped, prefix, suffix, gripper = has_grip(old_moves, config)

    if suffix:
        degripped = Algorithm([*config[gripper](suffix), gripper])

        if has_grip(degripped, config)[0]:
            return degrip(prefix + degripped, config)

        return Algorithm(prefix + degripped)

    return old_moves


def degrip_x_moves(old_moves: Algorithm) -> Algorithm:
    return degrip(
        old_moves, DEGRIP_X,
    )


def degrip_y_moves(old_moves: Algorithm) -> Algorithm:
    return degrip(
        old_moves, DEGRIP_Y,
    )


def degrip_z_moves(old_moves: Algorithm) -> Algorithm:
    return degrip(
        old_moves, DEGRIP_Z,
    )


def degrip_full_moves(old_moves: Algorithm) -> Algorithm:
    return degrip(
        old_moves, DEGRIP_FULL,
    )
