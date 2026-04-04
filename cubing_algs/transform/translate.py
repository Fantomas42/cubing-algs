"""Algorithm translation transformations based on cube orientation changes."""
from collections.abc import Callable
from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.transform.offset import PARSED_OFFSET_TABLES
from cubing_algs.transform.offset import ROTATION_TO_OFFSET_KEYS
from cubing_algs.transform.offset import ParsedTable
from cubing_algs.transform.offset import compose_offset_tables
from cubing_algs.transform.offset import rotate_move

if TYPE_CHECKING:
    from cubing_algs.move import Move


def translate_moves(
        orientation_moves: Algorithm,
) -> Callable[[Algorithm], Algorithm]:
    """
    Return a transform that rewrites an algorithm for a given cube orientation.

    Given a sequence of rotations describing how the cube is held,
    returns a function that translates any algorithm so it produces the
    same effect on the reoriented cube.

    This is a higher-order function: call it once with the orientation,
    then apply the returned function to one or more algorithms.

    Orientations use the two-letter notation from ``ORIENTATIONS``
    (top-face + front-face). Standard is UF (white top, green front,
    no rotation). Each orientation maps to a rotation sequence::

        UF  (standard)       →  (none)
        DF  (yellow, green)  →  z2
        RF  (red, green)     →  z'
        FU  (green, yellow)  →  x
        ...

    The problem this solves:

    A Bluetooth cube has no gyroscope — it only has mechanical sensors
    on each face. Those sensors always report moves in the cube's
    absolute frame (UF), no matter how the user holds the cube.

    When the user picks an orientation before solving (e.g. DF), there
    is a mismatch between what the user does and what the cube records::

        User holds the cube in DF (z2 = yellow top, green front).
        The user executes what they see as  R U R' U' :

        ┌─────────────────┬──────────────────────────────────┐
        │ What user sees  │ What the cube records (UF frame) │
        ├─────────────────┼──────────────────────────────────┤
        │ R  (right face) │ L  (it's physically the L face)  │
        │ U  (top face)   │ D  (it's physically the D face)  │
        │ R'              │ L'                               │
        │ U'              │ D'                               │
        └─────────────────┴──────────────────────────────────┘

    This function bridges that gap:

        translate_moves(z2):  L D L' D'  →  R U R' U'
                              (recorded)    (what user meant)

    Same principle with other orientations::

        Orientation   User does   Cube records   After translate
        ────────────────────────────────────────────────────────
        DF  (z2)      R U R' U'   L D L' D'      R U R' U'
        RF  (z')      R U R' U'   D R D' R'      R U R' U'
        FU  (x)       R U R' U'   R F R' F'      R U R' U'
        FR  (x y)     R U R' U'   U F U' F'      R U R' U'
        FL  (x y')    R U R' U'   D F D' F'      R U R' U'
        LU  (z y)     R U R' U'   B L B' L'      R U R' U'

    Also works for translating scrambles. A scramble generator produces
    moves in the standard UF frame. If the user holds the cube in DF,
    they need each move rewritten so they can apply it from their POV::

        UF scramble:  R  U  F' D2 L  B' R2 U'
        DF scramble:  L  D  F' U2 R  B' L2 D'

        translate_moves(z2):  R U F' D2 L B' R2 U'
                            → L D F' U2 R B' L2 D'

    Both scrambles produce the exact same cube state — the user just
    reads different face names because they are holding the cube
    upside down.

    Contrast with ``translate_pov_moves``, which handles rotations
    discovered inline during the algorithm (gyroscope events).
    ``translate_moves`` handles a known, fixed orientation applied to
    the whole algorithm at once.

    Args:
        orientation_moves: Rotation moves (x, y, z) defining the orientation.

    Returns:
        Function that translates algorithms into the given orientation.

    Raises:
        InvalidMoveError: If orientation_moves contain non-rotation moves.

    """
    for orientation_move in orientation_moves:
        if not orientation_move.is_rotation_move:
            msg = f'{ orientation_move } is not a rotation move'
            raise InvalidMoveError(msg)

    composed: ParsedTable = {}
    for orientation_move in orientation_moves:
        for key in ROTATION_TO_OFFSET_KEYS[str(orientation_move.untimed)]:
            composed = compose_offset_tables(
                composed, PARSED_OFFSET_TABLES[key],
            )

    def _translate_moves(old_moves: Algorithm) -> Algorithm:
        if not composed or not old_moves:
            return old_moves

        return Algorithm(
            rotate_move(move, composed)
            for move in old_moves
        )

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
    new_moves: list[Move] = []
    composed: ParsedTable = {}

    for move in old_moves:
        if move.is_rotation_move:
            for key in ROTATION_TO_OFFSET_KEYS[str(move.untimed)]:
                composed = compose_offset_tables(
                    composed, PARSED_OFFSET_TABLES[key],
                )
            new_moves.append(move)
        elif composed:
            new_moves.append(rotate_move(move, composed))
        else:
            new_moves.append(move)

    return Algorithm(new_moves)
