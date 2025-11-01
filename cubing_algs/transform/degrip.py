"""Degrip transformations for converting rotation moves into face moves."""

from collections.abc import Callable

from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move
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
) -> tuple[bool, Algorithm, Algorithm, str]:
    """Check if an algorithm contains grip moves according to config."""
    i = 0
    prefix = Algorithm()
    suffix = Algorithm()
    gripper_move = ''

    while i < len(old_moves) - 1:
        move_str = str(old_moves[i].untimed)

        if move_str in config:
            suffix = old_moves[i + 1:]
            prefix = old_moves[:i]
            gripper_move = move_str
            break

        i += 1

    config_keys = set(config.keys())
    if suffix and any(str(m.untimed) not in config_keys for m in suffix):
        return True, prefix, suffix, gripper_move

    return False, Algorithm(), Algorithm(), ''


def degrip(
        old_moves: Algorithm,
        config: dict[str, Callable[[Algorithm], Algorithm]],
) -> Algorithm:
    """
    Remove grip moves from an algorithm
    by applying appropriate transformations.
    """
    _gripped, prefix, suffix, gripper = has_grip(old_moves, config)

    if suffix:
        degripped = Algorithm([*config[gripper](suffix), Move(gripper)])

        if has_grip(degripped, config)[0]:
            return degrip(prefix + degripped, config)

        return Algorithm(prefix + degripped)

    return old_moves


def degrip_x_moves(old_moves: Algorithm) -> Algorithm:
    """Remove X-axis grip rotations from an algorithm."""
    return degrip(
        old_moves, DEGRIP_X,
    )


def degrip_y_moves(old_moves: Algorithm) -> Algorithm:
    """Remove Y-axis grip rotations from an algorithm."""
    return degrip(
        old_moves, DEGRIP_Y,
    )


def degrip_z_moves(old_moves: Algorithm) -> Algorithm:
    """Remove Z-axis grip rotations from an algorithm."""
    return degrip(
        old_moves, DEGRIP_Z,
    )


def degrip_full_moves(old_moves: Algorithm) -> Algorithm:
    """Remove all grip rotations from an algorithm."""
    return degrip(
        old_moves, DEGRIP_FULL,
    )
