"""Algorithm translation transformations based on cube orientation changes."""
from collections.abc import Callable

from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.transform.degrip import DEGRIP_FULL


def translate_moves(
        orientation_moves: Algorithm,
) -> Callable[[Algorithm], Algorithm]:
    """
    Translate moves from a list of rotation moves.

    Args:
        orientation_moves: Sequence of rotation moves defining the orientation.

    Returns:
        Function that translates algorithms based on the orientation.

    Raises:
        InvalidMoveError: If orientations_moves contain non rotation moves.

    """
    for orientation_move in orientation_moves:
        if not orientation_move.is_rotation_move:
            msg = f'{ orientation_move } is not a rotation move'
            raise InvalidMoveError(msg)

    def _translate_moves(old_moves: Algorithm) -> Algorithm:
        if not orientation_moves or not old_moves:
            return old_moves

        new_moves = old_moves.copy()
        for orientation_move in orientation_moves:
            new_moves = DEGRIP_FULL[str(orientation_move.inverted)](new_moves)

        return new_moves

    return _translate_moves


def translate_pov_moves(old_moves: Algorithm) -> Algorithm:
    """
    Rewrite moves after inline rotations to match the user's point of view.

    When an algorithm contains cube rotations (x, y, z), the moves that
    follow are in the cube's absolute frame. This function translates
    those moves into the user's frame after each rotation, so the
    algorithm reads as the user would execute it.

    Rotations are preserved in place; only non-rotation moves are
    rewritten. Each rotation's effect accumulates over subsequent ones.

    Example::

        R U R' U' y B U B' U'  →  R U R' U' y R U R' U'

    After the y rotation, B (absolute) becomes R (user's POV).

    Typical use: a Bluetooth cube with a gyroscope (e.g. GAN iCarry)
    has two independent sensors:

    - A **mechanical sensor** that detects face turns (R, U, F, ...).
      These are always reported relative to the cube's fixed physical
      stickers, regardless of how the cube is held.
    - A **gyroscope** that detects whole-cube rotations (x, y, z).
      These are injected into the move stream as separate events.

    Because these sensors are independent, the recorded algorithm
    mixes absolute-frame face moves with rotation events::

        Sensor output:  R  U  R' U'  y  B  U  B' U'
                        ^^^^^^^^^^^  ^  ^^^^^^^^^^^
                        face sensor  gyro  face sensor

    Here the user did y (rotated the cube) then continued solving
    what they see as the R face — but the cube still reports B
    because its stickers didn't move. This function rewrites the
    face moves after each rotation so the algorithm reads as the
    user intended::

        After translate:  R  U  R' U'  y  R  U  R' U'

    Args:
        old_moves: Algorithm potentially containing inline rotations.

    Returns:
        Algorithm with non-rotation moves translated to user's POV.

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
