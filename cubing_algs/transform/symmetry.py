from cubing_algs.constants import SYMMETRY_E
from cubing_algs.constants import SYMMETRY_M
from cubing_algs.constants import SYMMETRY_S


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
