"""
Single-rotation offset transformations for remapping move names.

The core building block for rotation-aware transforms.  Given a single
rotation (x, y, z, or their primes), ``rotate`` rewrites every move in
an algorithm so it targets the same physical pieces when viewed from the
rotated perspective.

Example — offset by y (the cube turns clockwise from above, like U)::

    After y the cube looks like this:

        position:  U    R    F    D    L    B
        stickers:  W    B    R    Y    G    O
                   (same) ←—— shifted clockwise ——→ (same)

    The R face (red) is now in front.  From the y-shifted viewpoint
    the user calls it "F".  Every face that moved gets a new name:

        R → F    F → L    L → B    B → R    (U and D stay)

        offset_y_moves( R  U  R' U' )
                      → F  U  F' U'

    The algorithm has been rewritten for someone looking at the cube
    after a y turn — same physical pieces, different face names.

Naming convention — perspective shift, not rotation applied:

    ``offset_y_moves``  means "rewrite for a y-shifted viewpoint."
    Internally it applies the *inverse* rotation table (y') to each
    move.  This is why the function name and the rotation string look
    swapped::

        offset_y_moves      → offset_moves(old_moves, "y'")   # y' table
        offset_yprime_moves → offset_moves(old_moves, "y")    # y  table

    The inverse is needed because we are translating into the rotated
    frame: "what does the original R become if the observer has turned
    by y?" — the R face is now in front, so it becomes F.

Relationship with other transform modules:

    ``offset`` applies a single, known rotation to every move in an
    algorithm.  It is a pure remapping — no moves are added or removed.

    ``degrip`` scans an algorithm for inline rotation moves, removes
    each one, and uses offset to rewrite the moves that follow.  To
    absorb a y rotation it calls ``offset_yprime_moves`` (the inverse
    offset) so subsequent moves land on the correct faces::

        y  R  U  R' U'               (algorithm with grip)
        ↓  degrip absorbs y by calling offset_yprime_moves on suffix
        B  U  B' U'  y               (degripped, trailing y preserved)

    ``translate_moves`` handles a full orientation (possibly multi-rotation,
    e.g. z2 or x y) applied to the whole algorithm at once.  It chains
    offset calls through the degrip tables for each rotation in order.

    ``translate_pov_moves`` walks an algorithm left-to-right and
    accumulates rotations as they appear, translating only the
    non-rotation moves that follow each rotation into the user's
    current point of view.
"""
from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import OFFSET_TABLE
from cubing_algs.constants import WIDE_CHAR
from cubing_algs.move import Move


def rotate(old_moves: Algorithm, rotation: str) -> Algorithm:
    """
    Apply a rotation transformation to moves using the offset table.

    Transforms each move according to the specified rotation direction,
    maintaining move properties and notation style.

    Args:
        old_moves: The algorithm to transform.
        rotation: The rotation direction (e.g., 'x', 'y', 'z', "x'", etc).

    Returns:
        Transformed algorithm with rotated moves.

    """
    moves: list[Move] = []
    rotation_table: dict[str, str] = OFFSET_TABLE[rotation]

    for move in old_moves:
        time = move.time
        base_move = move.base_move
        wide = WIDE_CHAR if move.is_wide_move else ''

        new_move = move

        if base_move in rotation_table:
            new_move = Move(
                move.layer + rotation_table[base_move] + wide + time,
            )
            if move.is_counter_clockwise:
                new_move = new_move.inverted
            elif move.is_double:
                new_move = new_move.doubled

            if move.is_sign_move:
                new_move = new_move.to_sign

        moves.append(new_move)

    return Algorithm(moves)


def offset_moves(
        old_moves: Algorithm,
        rotation: str,
        count: int = 1,
) -> Algorithm:
    """
    Apply a rotation transformation multiple times to an algorithm.

    Repeatedly applies the specified rotation to achieve the desired offset.

    Args:
        old_moves: The algorithm to transform.
        rotation: The rotation direction.
        count: Number of times to apply the rotation.

    Returns:
        Transformed algorithm after repeated rotation.

    """
    result = old_moves
    for _ in range(count):
        result = rotate(result, rotation)
    return result


def offset_x_moves(old_moves: Algorithm) -> Algorithm:
    """
    Offset moves by x perspective (applies x' rotation internally).

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm with moves remapped from x-shifted perspective.

    """
    return offset_moves(old_moves, "x'")


def offset_x2_moves(old_moves: Algorithm) -> Algorithm:
    """
    Apply x2 rotation to moves.

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm rotated by x2.

    """
    return offset_moves(old_moves, 'x', 2)


def offset_xprime_moves(old_moves: Algorithm) -> Algorithm:
    """
    Offset moves by x' perspective (applies x rotation internally).

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm with moves remapped from x'-shifted perspective.

    """
    return offset_moves(old_moves, 'x')


def offset_y_moves(old_moves: Algorithm) -> Algorithm:
    """
    Offset moves by y perspective (applies y' rotation internally).

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm with moves remapped from y-shifted perspective.

    """
    return offset_moves(old_moves, "y'")


def offset_y2_moves(old_moves: Algorithm) -> Algorithm:
    """
    Apply y2 rotation to moves.

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm rotated by y2.

    """
    return offset_moves(old_moves, 'y', 2)


def offset_yprime_moves(old_moves: Algorithm) -> Algorithm:
    """
    Offset moves by y' perspective (applies y rotation internally).

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm with moves remapped from y'-shifted perspective.

    """
    return offset_moves(old_moves, 'y')


def offset_z_moves(old_moves: Algorithm) -> Algorithm:
    """
    Offset moves by z perspective (applies z' rotation internally).

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm with moves remapped from z-shifted perspective.

    """
    return offset_moves(old_moves, "z'")


def offset_z2_moves(old_moves: Algorithm) -> Algorithm:
    """
    Apply z2 rotation to moves.

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm rotated by z2.

    """
    return offset_moves(old_moves, 'z', 2)


def offset_zprime_moves(old_moves: Algorithm) -> Algorithm:
    """
    Offset moves by z' perspective (applies z rotation internally).

    Args:
        old_moves: The algorithm to transform.

    Returns:
        Algorithm with moves remapped from z'-shifted perspective.

    """
    return offset_moves(old_moves, 'z')
