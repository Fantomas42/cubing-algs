from cubing_algs.constants import SYMMETRY_E
from cubing_algs.constants import SYMMETRY_M
from cubing_algs.constants import SYMMETRY_S
from cubing_algs.move import Move

SYMMETRY_CONFIGS = {
    'M': ({'x', 'M'}, SYMMETRY_M),
    'S': ({'z', 'S'}, SYMMETRY_S),
    'E': ({'y', 'E'}, SYMMETRY_E),
}


def symmetry_moves(
        old_moves: list[Move],
        ignore_moves: set[str],
        symmetry_table: dict[str, str],
) -> list[Move]:
    moves = []

    for move in old_moves:
        if move.is_pause or move.base_move in ignore_moves:
            moves.append(move)
        else:
            new_move = Move(
                move.layer + symmetry_table[move.base_move] + move.time,
            )

            if move.is_japanese_move:
                new_move = new_move.japanesed

            if move.is_double:
                moves.append(new_move.doubled)
            elif move.is_clockwise:
                moves.append(new_move.inverted)
            else:
                moves.append(new_move)

    return moves


def symmetry_type_moves(
        old_moves: list[Move],
        symmetry_type: str,
) -> list[Move]:
    ignore_moves, symmetry_table = SYMMETRY_CONFIGS[symmetry_type]
    return symmetry_moves(old_moves, ignore_moves, symmetry_table)


def symmetry_m_moves(old_moves: list[Move]) -> list[Move]:
    return symmetry_type_moves(old_moves, 'M')


def symmetry_s_moves(old_moves: list[Move]) -> list[Move]:
    return symmetry_type_moves(old_moves, 'S')


def symmetry_e_moves(old_moves: list[Move]) -> list[Move]:
    return symmetry_type_moves(old_moves, 'E')


def symmetry_c_moves(old_moves: list[Move]) -> list[Move]:
    moves = symmetry_m_moves(old_moves)
    return symmetry_s_moves(moves)
