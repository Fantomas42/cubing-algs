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

# Parsed offset tables: base_move -> (new_base, direction_flipped)
ParsedTable = dict[str, tuple[str, bool]]

ROTATION_TO_OFFSET_KEYS: dict[str, tuple[str, ...]] = {
    'x': ("x'",), "x'": ('x',), 'x2': ('x', 'x'),
    'y': ("y'",), "y'": ('y',), 'y2': ('y', 'y'),
    'z': ("z'",), "z'": ('z',), 'z2': ('z', 'z'),
}

PARSED_OFFSET_TABLES: dict[str, ParsedTable] = {
    key: {
        k: (v[:-1], True) if v.endswith("'") else (v, False)
        for k, v in raw.items()
    }
    for key, raw in OFFSET_TABLE.items()
}


def compose_offset_tables(t1: ParsedTable, t2: ParsedTable) -> ParsedTable:
    """
    Compose two parsed offset tables into one.

    Returns:
        Composed table that applies t1 then t2 in a single lookup.

    """
    result: ParsedTable = {}
    for k, (mapped, flip1) in t1.items():
        if mapped in t2:
            final, flip2 = t2[mapped]
            result[k] = (final, flip1 ^ flip2)
        else:
            result[k] = (mapped, flip1)
    for k, v in t2.items():
        if k not in result:
            result[k] = v
    return result


def rotate_move(move: Move, table: ParsedTable) -> Move:
    """
    Apply a composed offset table to a single move.

    Returns:
        Move with base remapped and direction adjusted per the table.

    """
    base_move = move.base_move
    if base_move not in table:
        return move

    new_base, flip = table[base_move]
    wide = WIDE_CHAR if move.is_wide_move else ''
    new_move = Move(move.layer + new_base + wide + move.time)

    if move.is_double:
        new_move = new_move.doubled
    elif move.is_counter_clockwise ^ flip:
        new_move = new_move.inverted

    if move.is_sign_move:
        new_move = new_move.to_sign

    return new_move


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
    table = PARSED_OFFSET_TABLES[rotation]
    return Algorithm(rotate_move(move, table) for move in old_moves)


def offset_moves(
        old_moves: Algorithm,
        rotation: str,
        count: int = 1,
) -> Algorithm:
    """
    Apply a rotation transformation multiple times to an algorithm.

    Pre-composes the offset table to apply the rotation in a single
    pass regardless of count.

    Args:
        old_moves: The algorithm to transform.
        rotation: The rotation direction.
        count: Number of times to apply the rotation.

    Returns:
        Transformed algorithm after repeated rotation.

    """
    if count == 0 or not old_moves:
        return old_moves

    base_table = PARSED_OFFSET_TABLES[rotation]
    composed = base_table
    for _ in range(count - 1):
        composed = compose_offset_tables(composed, base_table)

    return Algorithm(rotate_move(move, composed) for move in old_moves)


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
