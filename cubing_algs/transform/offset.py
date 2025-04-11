from cubing_algs.constants import OFFSET_TABLE
from cubing_algs.move import Move


def unrotate(old_moves: list[Move], rotation: str) -> list[Move]:
    moves: list[Move] = []
    rotation_table: dict[str, str] = OFFSET_TABLE[rotation]

    for move in old_moves:
        move_str = str(move)
        base_str = move.base_move

        if move_str in rotation_table:
            moves.append(Move(rotation_table[move_str]))
        elif move.is_double and base_str in rotation_table:
            moves.append(Move(rotation_table[base_str]).doubled)
        elif move.is_double and str(Move(base_str).inverted) in rotation_table:
            moves.append(Move(rotation_table[str(Move(base_str).inverted)]).doubled)
        elif str(move.inverted) in rotation_table:
            moves.append(Move(rotation_table[str(move.inverted)]).inverted)
        else:
            moves.append(move)

    return moves


def offset_moves(
        old_moves: list[Move],
        rotation: str,
        count: int = 1,
) -> list[Move]:
    result = old_moves
    for _ in range(count):
        result = unrotate(result, rotation)
    return result


def offset_x_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, "x'")


def offset_x2_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, 'x', 2)


def offset_xprime_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, 'x')


def offset_y_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, "y'")


def offset_y2_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, 'y', 2)


def offset_yprime_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, 'y')


def offset_z_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, "z'")


def offset_z2_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, 'z', 2)


def offset_zprime_moves(old_moves: list[Move]) -> list[Move]:
    return offset_moves(old_moves, 'z')
