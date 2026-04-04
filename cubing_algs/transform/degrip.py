"""Degrip transformations for converting rotation moves into face moves."""
from collections.abc import Callable
from functools import partial

from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move
from cubing_algs.transform.offset import offset_moves

DEGRIP_X: dict[str, Callable[[Algorithm], Algorithm]] = {
    'x': partial(offset_moves, rotation='x'),
    'x2': partial(offset_moves, rotation='x', count=2),
    "x'": partial(offset_moves, rotation="x'"),
}

DEGRIP_Y: dict[str, Callable[[Algorithm], Algorithm]] = {
    'y': partial(offset_moves, rotation='y'),
    'y2': partial(offset_moves, rotation='y', count=2),
    "y'": partial(offset_moves, rotation="y'"),
}

DEGRIP_Z: dict[str, Callable[[Algorithm], Algorithm]] = {
    'z': partial(offset_moves, rotation='z'),
    'z2': partial(offset_moves, rotation='z', count=2),
    "z'": partial(offset_moves, rotation="z'"),
}


DEGRIP_FULL: dict[str, Callable[[Algorithm], Algorithm]] = {
    **DEGRIP_X,
    **DEGRIP_Y,
    **DEGRIP_Z,
}


def has_grip(
        old_moves: Algorithm,
        config: dict[str, Callable[[Algorithm], Algorithm]],
) -> tuple[bool, Algorithm, Algorithm, str]:
    """
    Check if an algorithm contains grip moves according to config.

    Args:
        old_moves: The algorithm to check.
        config: Dictionary mapping rotation moves to offset functions.

    Returns:
        Tuple of (has_grip, prefix, suffix, gripper_move_string).

    """
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

    if suffix and any(str(m.untimed) not in config for m in suffix):
        return True, prefix, suffix, gripper_move

    return False, Algorithm(), Algorithm(), ''


def degrip(
        old_moves: Algorithm,
        config: dict[str, Callable[[Algorithm], Algorithm]],
) -> Algorithm:
    """
    Remove grip moves from an algorithm by absorbing rotations into face moves.

    A "grip" is a cube rotation (x, y, z) that appears before non-rotation
    moves. Instead of rotating the whole cube and then turning faces, the
    same effect can be achieved by renaming the subsequent face moves to
    match the new orientation — eliminating the rotation entirely.

    The algorithm scans left-to-right for the first rotation listed in
    ``config``. When found, it applies the inverse offset to every move
    that follows, effectively absorbing the rotation. The rotation itself
    is pushed to the end of the algorithm (where it becomes a trailing
    rotation that can later be stripped by ``remove_ending_rotations``).

    If the result still contains grips, the process repeats until none
    remain.

    Example::

        Input:   x  R  U  R' U'
                 ^  ^^^^^^^^^^^
                 grip  face moves (absolute frame)

        Step 1:  apply x' offset to  R U R' U'  →  R F R' F'
        Result:  R  F  R' F'  x
                 ^^^^^^^^^^^^  ^
                 degripped      trailing rotation

    The trailing x is kept so the algorithm still produces the same cube
    state. Use ``remove_ending_rotations`` to strip it when the final
    orientation does not matter (e.g. displaying a short algorithm).

    Multiple grips are handled iteratively::

        Input:   x  R  U  x  F  D    (two grips)
        Pass 1:  R  F  x  D  B  x    (first x absorbed into R U x F D)
        Pass 2:  R  F  B  U  x  x    (second x absorbed into D B x)

    Contrast with ``translate_moves``, which applies a known, fixed
    orientation to the whole algorithm at once, and
    ``translate_pov_moves``, which translates moves after inline
    rotations to the user's point of view without removing them.
    ``degrip`` removes rotations by absorbing them into face moves.

    Args:
        old_moves: The algorithm to process.
        config: Dictionary mapping rotation move strings to their
            inverse offset functions (e.g. ``DEGRIP_X``, ``DEGRIP_FULL``).

    Returns:
        Algorithm with grip rotations absorbed into face moves.
        Trailing rotations are preserved to maintain cube-state equivalence.

    """
    result = old_moves

    while True:
        _gripped, prefix, suffix, gripper = has_grip(result, config)

        if not suffix:
            return result

        degripped = Algorithm([*config[gripper](suffix), Move(gripper)])

        if not has_grip(degripped, config)[0]:
            return Algorithm(prefix + degripped)

        result = prefix + degripped


def degrip_x_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove X-axis grip rotations from an algorithm.

    Args:
        old_moves: The algorithm to process.

    Returns:
        Algorithm with X-axis grips removed.

    """
    return degrip(
        old_moves, DEGRIP_X,
    )


def degrip_y_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove Y-axis grip rotations from an algorithm.

    Args:
        old_moves: The algorithm to process.

    Returns:
        Algorithm with Y-axis grips removed.

    """
    return degrip(
        old_moves, DEGRIP_Y,
    )


def degrip_z_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove Z-axis grip rotations from an algorithm.

    Args:
        old_moves: The algorithm to process.

    Returns:
        Algorithm with Z-axis grips removed.

    """
    return degrip(
        old_moves, DEGRIP_Z,
    )


def degrip_full_moves(old_moves: Algorithm) -> Algorithm:
    """
    Remove all grip rotations from an algorithm.

    Args:
        old_moves: The algorithm to process.

    Returns:
        Algorithm with all grip rotations removed.

    """
    return degrip(
        old_moves, DEGRIP_FULL,
    )
