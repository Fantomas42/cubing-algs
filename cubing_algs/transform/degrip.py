def has_grip(
        old_moves: list[str],
        config: dict[str, Callable[[list[str]], list[str]]],
) -> tuple[bool, Any, Any, Any]:
    i = 0
    prefix = []
    suffix = []

    while i < len(old_moves) - 1:
        move = old_moves[i]

        if move in config:
            suffix = old_moves[i + 1:]
            prefix = old_moves[:i]
            break

        i += 1

    if suffix and set(suffix) - set(config.keys()):
        return True, prefix, suffix, move

    return False, False, False, False


def degrip(
        old_moves: list[str],
        config: dict[str, Callable[[list[str]], list[str]]],
) -> list[str]:
    _gripped, prefix, suffix, gripper = has_grip(old_moves, config)

    if suffix:
        degripped = [*config[gripper](suffix), gripper]

        if has_grip(degripped, config)[0]:
            return degrip(prefix + degripped, config)

        return compress_moves(prefix + degripped)

    return compress_moves(old_moves)


def degrip_x_moves(old_moves: list[str]) -> list[str]:
    return degrip(
        old_moves, {
            'x': offset_xprime_moves,
            'x2': offset_x2_moves,
            "x'": offset_x_moves,
        },
    )


def degrip_y_moves(old_moves: list[str]) -> list[str]:
    return degrip(
        old_moves, {
            'y': offset_yprime_moves,
            'y2': offset_y2_moves,
            "y'": offset_y_moves,
        },
    )


def degrip_z_moves(old_moves: list[str]) -> list[str]:
    return degrip(
        old_moves, {
            'z': offset_zprime_moves,
            'z2': offset_z2_moves,
            "z'": offset_z_moves,
        },
    )


def degrip_full_moves(old_moves: list[str]) -> list[str]:
    return degrip(
        old_moves, {
            'x': offset_xprime_moves,
            'x2': offset_x2_moves,
            "x'": offset_x_moves,
            'y': offset_yprime_moves,
            'y2': offset_y2_moves,
            "y'": offset_y_moves,
            'z': offset_zprime_moves,
            'z2': offset_z2_moves,
            "z'": offset_z_moves,
        },
    )
