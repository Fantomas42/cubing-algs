from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import SYMMETRY_TABLE
from cubing_algs.constants import WIDE_CHAR
from cubing_algs.move import Move


def symmetry_moves(
        old_moves: Algorithm,
        ignore_moves: set[str],
        symmetry_table: dict[str, str],
) -> Algorithm:
    """
    Apply symmetry transformation to an algorithm using a symmetry table.

    Transforms each move according to the provided symmetry mapping,
    preserving move modifiers and notation style.
    """
    moves: list[Move] = []

    for move in old_moves:
        if move.is_pause or move.base_move in ignore_moves:
            moves.append(move)
        else:
            symmetry_move = symmetry_table[move.base_move]

            if move.is_wide_move:
                symmetry_move += WIDE_CHAR

            new_move = Move(
                move.layer + symmetry_move + move.time,
            )

            if move.is_sign_move:
                new_move = new_move.to_sign

            if move.is_double:
                moves.append(new_move.doubled)
            elif move.is_clockwise:
                moves.append(new_move.inverted)
            else:
                moves.append(new_move)

    return Algorithm(moves)


def symmetry_type_moves(
        old_moves: Algorithm,
        symmetry_type: str,
) -> Algorithm:
    """
    Apply a specific type of symmetry transformation to moves.

    Uses predefined symmetry tables to transform the algorithm.
    """
    ignore_moves, symmetry_table = SYMMETRY_TABLE[symmetry_type]
    return symmetry_moves(old_moves, ignore_moves, symmetry_table)


def symmetry_m_moves(old_moves: Algorithm) -> Algorithm:
    """Apply M-slice symmetry transformation to moves."""
    return symmetry_type_moves(old_moves, 'M')


def symmetry_s_moves(old_moves: Algorithm) -> Algorithm:
    """Apply S-slice symmetry transformation to moves."""
    return symmetry_type_moves(old_moves, 'S')


def symmetry_e_moves(old_moves: Algorithm) -> Algorithm:
    """Apply E-slice symmetry transformation to moves."""
    return symmetry_type_moves(old_moves, 'E')


def symmetry_c_moves(old_moves: Algorithm) -> Algorithm:
    """Apply combined symmetry transformation using M and S symmetries."""
    moves = symmetry_m_moves(old_moves)
    return symmetry_s_moves(moves)
