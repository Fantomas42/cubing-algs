from collections.abc import Callable

from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.transform.degrip import DEGRIP_FULL


def translate_moves(
        orientation_moves: Algorithm,
) -> Callable[[Algorithm], Algorithm]:
    """
    Translate moves from a list of rotation moves.
    """

    def _translate_moves(old_moves: Algorithm) -> Algorithm:
        if not orientation_moves or not old_moves:
            return old_moves

        for orientation_move in orientation_moves:
            if not orientation_move.is_rotation_move:
                msg = f'{ orientation_move } is not a rotation move'
                raise InvalidMoveError(msg)

        new_moves = old_moves.copy()
        for orientation_move in orientation_moves:
            new_moves = DEGRIP_FULL[str(orientation_move.inverted)](new_moves)

        return new_moves

    return _translate_moves


def translate_pov_moves(old_moves: Algorithm) -> Algorithm:
    """
    Translate moves to match user POV.
    """
    new_moves = old_moves.copy()

    for i, move in enumerate(old_moves):
        if move.is_rotation_move:
            new_moves[i:] = [
                move, *translate_moves(
                    Algorithm([move.untimed]),
                )(new_moves[i + 1:]),
            ]

    return new_moves
