def offset_x_moves(old_moves: list[str]) -> list[str]:
    return unrotate("x'", old_moves)


def offset_x2_moves(old_moves: list[str]) -> list[str]:
    return offset_x_moves(offset_x_moves(old_moves))


def offset_xprime_moves(old_moves: list[str]) -> list[str]:
    return unrotate('x', old_moves)


def offset_y_moves(old_moves: list[str]) -> list[str]:
    return unrotate("y'", old_moves)


def offset_y2_moves(old_moves: list[str]) -> list[str]:
    return offset_y_moves(offset_y_moves(old_moves))


def offset_yprime_moves(old_moves: list[str]) -> list[str]:
    return unrotate('y', old_moves)


def offset_z_moves(old_moves: list[str]) -> list[str]:
    return unrotate("z'", old_moves)


def offset_z2_moves(old_moves: list[str]) -> list[str]:
    return offset_z_moves(offset_z_moves(old_moves))


def offset_zprime_moves(old_moves: list[str]) -> list[str]:
    return unrotate('z', old_moves)
