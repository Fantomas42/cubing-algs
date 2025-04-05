# ruff: noqa: ERA001
from cubing_algs.constants import OFFSET_TABLE
from cubing_algs.move import Move


def unrotate(old_moves: list[Move], rotation: str) -> list[Move]:
    moves = []
    rotation_table = OFFSET_TABLE[rotation]

    for move in old_moves:
        if move in rotation_table:
            moves.append(rotation_table[move])
        elif move[0] in rotation_table and move[-1] == '2':
            moves.append('%s2' % rotation_table[move[0]][0])
        elif "%s'" % move[0] in rotation_table and move[-1] == '2':
            moves.append('%s2' % rotation_table["%s'" % move[0]][0])
        elif move.inverted in rotation_table:
            moves.append(Move(rotation_table[move.inverted]).inverted)
        else:
            moves.append(move)

    # for move in old_moves:
    #     if move in rotation_table:
    #         moves.append(rotation_table[move])
    #     elif move.base_move in rotation_table and move.is_double:
    #         moves.append(Move(rotation_table[move[0]]).doubled)
    #     elif "%s'" % move.base_move in rotation_table and move.is_double:
    #         moves.append('%s2' % rotation_table["%s'" % move.base_move][0])
    #     elif move.inverted in rotation_table:
    #         moves.append(Move(rotation_table[move.inverted]).inverted)
    #     else:
    #         moves.append(move)

    return moves


def offset_x_moves(old_moves: list[Move]) -> list[Move]:
    return unrotate(old_moves, "x'")


def offset_x2_moves(old_moves: list[Move]) -> list[Move]:
    return offset_x_moves(offset_x_moves(old_moves))


def offset_xprime_moves(old_moves: list[Move]) -> list[Move]:
    return unrotate(old_moves, 'x')


def offset_y_moves(old_moves: list[Move]) -> list[Move]:
    return unrotate(old_moves, "y'")


def offset_y2_moves(old_moves: list[Move]) -> list[Move]:
    return offset_y_moves(offset_y_moves(old_moves))


def offset_yprime_moves(old_moves: list[Move]) -> list[Move]:
    return unrotate(old_moves, 'y')


def offset_z_moves(old_moves: list[Move]) -> list[Move]:
    return unrotate(old_moves, "z'")


def offset_z2_moves(old_moves: list[Move]) -> list[Move]:
    return offset_z_moves(offset_z_moves(old_moves))


def offset_zprime_moves(old_moves: list[Move]) -> list[Move]:
    return unrotate(old_moves, 'z')
