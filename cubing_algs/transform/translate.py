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

    def _translate_moves(algorithm: Algorithm) -> Algorithm:
        for orientation_move in orientation_moves:
            if not orientation_move.is_rotation_move:
                msg = f'{ orientation_move } is not a rotation move'
                raise InvalidMoveError(msg)

        if not orientation_moves or not algorithm:
            return algorithm

        for orientation_move in orientation_moves:
            algorithm = DEGRIP_FULL[str(orientation_move.inverted)](algorithm)

        return algorithm

    return _translate_moves
