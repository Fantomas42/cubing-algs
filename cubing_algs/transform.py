from collections.abc import Callable
from typing import Any

from cubing_algs.constants import OFFSET_TABLE
from cubing_algs.constants import ROTATIONS
from cubing_algs.constants import SYMMETRY_E
from cubing_algs.constants import SYMMETRY_M
from cubing_algs.constants import SYMMETRY_S
from cubing_algs.constants import UNSLICE


def invert(move: str) -> str:
    if move.endswith("'"):
        return move[:1]
    return "%s'" % move


def unrotate(rotation: str, old_moves: list[str]) -> list[str]:
    moves = []
    rotation_table = OFFSET_TABLE[rotation]

    for move in old_moves:
        if move in rotation_table:
            moves.append(rotation_table[move])
        elif move[0] in rotation_table and move[-1] == '2':
            moves.append('%s2' % rotation_table[move[0]][0])
        elif "%s'" % move[0] in rotation_table and move[-1] == '2':
            moves.append('%s2' % rotation_table["%s'" % move[0]][0])
        elif invert(move) in rotation_table:
            moves.append(invert(rotation_table[invert(move)]))
        else:
            moves.append(move)

    return moves


def optimize_repeat_three_moves(old_moves: list[str]) -> list[str]:
    """ R, R, R --> R' """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 2:
        if moves[i] == moves[i + 1] == moves[i + 2]:
            moves[i:i + 3] = [invert(moves[i])]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_repeat_three_moves(moves)

    return moves


def optimize_do_undo_moves(old_moves: list[str]) -> list[str]:
    """ R R' --> <nothing>, R R R' R' --> <nothing> """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if invert(moves[i]) == moves[i + 1] or (
                moves[i] == moves[i + 1]
                and moves[i][-1] == '2'
                and moves[i + 1][-1] == '2'
        ):
            moves[i:i + 2] = []
            changed = True
        else:
            i += 1

    if changed:
        return optimize_do_undo_moves(moves)

    return moves


def optimize_double_moves(old_moves: list[str]) -> list[str]:
    """ R, R --> R2 """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if moves[i] == moves[i + 1]:
            moves[i:i + 2] = ['%s2' % moves[i][0]]
            changed = True
        else:
            i += 1

    if changed:
        return optimize_double_moves(moves)

    return moves


def optimize_triple_moves(old_moves: list[str]) -> list[str]:
    """ R, R2 --> R' """
    i = 0
    changed = False
    moves = list(old_moves)

    while i < len(moves) - 1:
        if moves[i][0] == moves[i + 1][0]:
            if moves[i][-1] == '2' and moves[i + 1][-1] != '2':
                moves[i:i + 2] = [invert(moves[i + 1])]
                changed = True
            elif moves[i][-1] != '2' and moves[i + 1][-1] == '2':
                moves[i:i + 2] = [invert(moves[i])]
                changed = True
            else:
                i += 1
        else:
            i += 1

    if changed:
        return optimize_triple_moves(moves)

    return moves


def compress_moves(old_moves: list[str]) -> list[str]:
    moves = list(old_moves)

    compressing = True
    while compressing:
        changed = False
        for optimizer in (
                optimize_do_undo_moves,
                optimize_repeat_three_moves,
                optimize_double_moves,
                optimize_triple_moves,
        ):
            new_moves = optimizer(moves)
            if new_moves != moves:
                moves = new_moves
                changed = True

        if not changed:
            compressing = False

    return moves


def unslice_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in old_moves:
        if move in UNSLICE:
            moves.extend(UNSLICE[move])
        else:
            moves.append(move)

    return moves


def symmetry_m_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in old_moves:
        if move[0] in {'x', 'M'}:
            moves.append(move)
        else:
            new_move = SYMMETRY_M[move[0]]

            if move.endswith("'"):
                moves.append(new_move)
            elif move.endswith('2'):
                moves.append('%s2' % new_move)
            else:
                moves.append("%s'" % new_move)

    return moves


def symmetry_s_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in old_moves:
        if move[0] in {'z', 'S'}:
            moves.append(move)
        else:
            new_move = SYMMETRY_S[move[0]]

            if move.endswith("'"):
                moves.append(new_move)
            elif move.endswith('2'):
                moves.append('%s2' % new_move)
            else:
                moves.append("%s'" % new_move)

    return moves


def symmetry_e_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in old_moves:
        if move[0] in {'y', 'E'}:
            moves.append(move)
        else:
            new_move = SYMMETRY_E[move[0]]

            if move.endswith("'"):
                moves.append(new_move)
            elif move.endswith('2'):
                moves.append('%s2' % new_move)
            else:
                moves.append("%s'" % new_move)

    return moves


def symmetry_c_moves(old_moves: list[str]) -> list[str]:
    moves = symmetry_m_moves(old_moves)
    return symmetry_s_moves(moves)


def mirror_moves(old_moves: list[str]) -> list[str]:
    moves = []
    for move in reversed(old_moves):
        if move.endswith("'"):
            moves.append(move.replace("'", ''))
        elif move.endswith('2'):
            moves.append(move)
        else:
            moves.append("%s'" % move)

    return moves


def expand_moves(old_moves: list[str]) -> list[str]:
    moves: list[str] = []
    for move in old_moves:
        if move.endswith('2'):
            moves.extend((move[:-1], move[:-1]))
        else:
            moves.append(move)

    return moves


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


def remove_final_rotations(old_moves: list[str]) -> list[str]:
    moves = []

    rotations = True
    for move in reversed(old_moves):
        if rotations and move[0] in ROTATIONS:
            continue
        rotations = False
        moves.append(move)

    return list(reversed(moves))
