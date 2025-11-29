"""
Dynamic cube rotation system for arbitrary cube sizes.

This module provides a size-agnostic rotation system that works with facelet
strings of any cube size. It uses coordinate-based rotation logic inspired by
MagicCube but maintains the facelet string representation.

Facelet Layout:
    - 2x2x2: 24 facelets (6 faces x 4 facelets each)
    - 3x3x3: 54 facelets (6 faces x 9 facelets each)
    - NxNxN: 6*N*N facelets

Face Order: U, R, F, D, L, B

Example 2x2x2 grid (per face):
    0 1
    2 3

Example 3x3x3 grid (per face):
    0 1 2
    3 4 5
    6 7 8

3D Coordinate System:
    - x-axis: 0 (left/L) to N-1 (right/R)
    - y-axis: 0 (down/D) to N-1 (up/U)
    - z-axis: 0 (back/B) to N-1 (front/F)
"""


from cubing_algs.move import Move

# Face ordering matches VCube convention
FACE_ORDER = ['U', 'R', 'F', 'D', 'L', 'B']

# Cache for permutation calculations
_PERMUTATION_CACHE: dict[tuple[int, str], list[int]] = {}


def get_face_coordinates(size: int) -> dict[str, list[tuple[int, int, int]]]:
    """
    Generate 3D coordinates for all facelets on each face.

    This follows MagicCube's coordinate system where each facelet
    is mapped to a 3D position (x, y, z).

    Args:
        size: The size of the cube (2 for 2x2x2, 3 for 3x3x3, etc.)

    Returns:
        Dictionary mapping face letters to lists of (x, y, z) coordinates.
        Each list contains size*size coordinates in facelet order.

    """
    # U face: top (y = size-1), scanning left-to-right, front-to-back
    u_coords = [
        (x, size - 1, z)
        for z in range(size)
        for x in range(size)
    ]

    # R face: right side (x = size-1), scanning front-to-back, top-to-bottom
    r_coords = [
        (size - 1, y, z)
        for y in reversed(range(size))
        for z in reversed(range(size))
    ]

    # F face: front (z = size-1), scanning left-to-right, top-to-bottom
    f_coords = [
        (x, y, size - 1)
        for y in reversed(range(size))
        for x in range(size)
    ]

    # D face: bottom (y = 0), scanning left-to-right, back-to-front
    d_coords = [
        (x, 0, z)
        for z in reversed(range(size))
        for x in range(size)
    ]

    # L face: left side (x = 0), scanning back-to-front, top-to-bottom
    l_coords = [
        (0, y, z)
        for y in reversed(range(size))
        for z in range(size)
    ]

    # B face: back (z = 0), scanning right-to-left, top-to-bottom
    b_coords = [
        (x, y, 0)
        for y in reversed(range(size))
        for x in reversed(range(size))
    ]

    return {
        'U': u_coords,
        'R': r_coords,
        'F': f_coords,
        'D': d_coords,
        'L': l_coords,
        'B': b_coords,
    }


def build_coord_to_facelet_map(
    size: int,
) -> dict[tuple[int, int, int], int]:
    """
    Build a mapping from 3D coordinates to facelet indices.

    Args:
        size: The size of the cube.

    Returns:
        Dictionary mapping (x, y, z) tuples to facelet indices.

    """
    face_coords = get_face_coordinates(size)
    coord_to_facelet: dict[tuple[int, int, int], int] = {}

    facelet_idx = 0
    for face in FACE_ORDER:
        for coord in face_coords[face]:
            coord_to_facelet[coord] = facelet_idx
            facelet_idx += 1

    return coord_to_facelet


def rotate_coordinates_90(
    coords: list[tuple[int, int, int]],
    axis: int,
    size: int,
    direction: int = 1,
) -> list[tuple[int, int, int]]:
    """
    Rotate a list of 3D coordinates 90 degrees around an axis.

    This is a pure Python implementation of numpy's rot90 for 3D coordinates.

    Args:
        coords: List of (x, y, z) coordinates to rotate.
        axis: Rotation axis (0=x/LR, 1=y/UD, 2=z/BF).
        size: Size of the cube (needed for coordinate transformation).
        direction: Rotation direction (1=CW, -1=CCW from axis perspective).

    Returns:
        List of rotated coordinates.

    Raises:
        ValueError: If axis is not 0, 1, or 2.

    """
    rotated = []

    for x, y, z in coords:
        if axis == 0:  # Rotate around x-axis (L/R moves)
            # y,z plane rotation
            # direction = 1 means CCW (like np.rot90 k=1)
            # direction = -1 means CW (like np.rot90 k=-1)
            if direction == 1:  # Counter-clockwise
                new_coord = (x, size - 1 - z, y)
            else:  # Clockwise (direction == -1)
                new_coord = (x, z, size - 1 - y)

        elif axis == 1:  # Rotate around y-axis (U/D moves)
            # x,z plane rotation
            if direction == 1:  # Counter-clockwise
                new_coord = (size - 1 - z, y, x)
            else:  # Clockwise (direction == -1)
                new_coord = (z, y, size - 1 - x)

        elif axis == 2:  # Rotate around z-axis (F/B moves)
            # x,y plane rotation
            if direction == 1:  # Counter-clockwise
                new_coord = (size - 1 - y, x, z)
            else:  # Clockwise (direction == -1)
                new_coord = (y, size - 1 - x, z)

        else:
            msg = f'Invalid axis: {axis}'
            raise ValueError(msg)

        rotated.append(new_coord)

    return rotated


def get_slice_mask(  # noqa: C901, PLR0912
    size: int,
    move_type: str,
    layers: list[int] | None = None,
) -> list[tuple[int, int, int]]:
    """
    Get all coordinates that should be rotated for a given move.

    Args:
        size: Size of the cube.
        move_type: Move type (e.g., 'R', 'U', 'F', 'L', 'D', 'B',
            'x', 'y', 'z').
        layers: List of 0-indexed layer indices to affect. If None,
            defaults to outermost layer only [0].

    Returns:
        List of (x, y, z) coordinates that are affected by this move.

    Layer Indexing:
        - Layer 0 is always the outermost layer
        - For R, U, F: layer 0 maps to coordinate (size-1),
          layer N to (size-1-N)
        - For L, D, B: layer 0 maps to coordinate 0, layer N to N

    Raises:
        ValueError: If move_type is not supported.

    """
    if layers is None:
        layers = [0]

    coords: list[tuple[int, int, int]] = []

    if move_type == 'R':
        # Right face: layer 0 at x = size - 1, layer N at x = size - 1 - N
        for layer_idx in layers:
            x_coord = size - 1 - layer_idx
            coords.extend(
                (x_coord, y, z)
                for y in range(size)
                for z in range(size)
            )

    elif move_type == 'L':
        # Left face: layer 0 at x = 0, layer N at x = N
        for layer_idx in layers:
            x_coord = layer_idx
            coords.extend(
                (x_coord, y, z)
                for y in range(size)
                for z in range(size)
            )

    elif move_type == 'U':
        # Up face: layer 0 at y = size - 1, layer N at y = size - 1 - N
        for layer_idx in layers:
            y_coord = size - 1 - layer_idx
            coords.extend(
                (x, y_coord, z)
                for x in range(size)
                for z in range(size)
            )

    elif move_type == 'D':
        # Down face: layer 0 at y = 0, layer N at y = N
        for layer_idx in layers:
            y_coord = layer_idx
            coords.extend(
                (x, y_coord, z)
                for x in range(size)
                for z in range(size)
            )

    elif move_type == 'F':
        # Front face: layer 0 at z = size - 1, layer N at z = size - 1 - N
        for layer_idx in layers:
            z_coord = size - 1 - layer_idx
            coords.extend(
                (x, y, z_coord)
                for x in range(size)
                for y in range(size)
            )

    elif move_type == 'B':
        # Back face: layer 0 at z = 0, layer N at z = N
        for layer_idx in layers:
            z_coord = layer_idx
            coords.extend(
                (x, y, z_coord)
                for x in range(size)
                for y in range(size)
            )

    # Rotation moves affect the entire cube
    elif move_type == 'x':
        # Rotate around x-axis (entire cube)
        coords.extend(
            (x, y, z)
            for x in range(size)
            for y in range(size)
            for z in range(size)
        )

    elif move_type == 'y':
        # Rotate around y-axis (entire cube)
        coords.extend(
            (x, y, z)
            for x in range(size)
            for y in range(size)
            for z in range(size)
        )

    elif move_type == 'z':
        # Rotate around z-axis (entire cube)
        coords.extend(
            (x, y, z)
            for x in range(size)
            for y in range(size)
            for z in range(size)
        )

    else:
        msg = f'Unsupported move type: {move_type}'
        raise ValueError(msg)

    return coords


def get_move_axis_and_direction(move_type: str) -> tuple[int, int]:
    """
    Get the rotation axis and direction for a move type.

    Args:
        move_type: The base move type (e.g., 'R', 'U', 'F').

    Returns:
        Tuple of (axis, direction) where:
            - axis: 0=x, 1=y, 2=z
            - direction: 1=CW, -1=CCW from positive axis perspective

    Raises:
        ValueError: If move_type is unknown.

    """
    # Following MagicCube's conventions
    if move_type in {'R', 'L', 'x'}:
        axis = 0
        direction = -1 if move_type in {'R', 'x'} else 1
    elif move_type in {'U', 'D', 'y'}:
        axis = 1
        direction = 1 if move_type in {'U', 'y'} else -1
    elif move_type in {'F', 'B', 'z'}:
        axis = 2
        direction = -1 if move_type in {'F', 'z'} else 1
    else:
        msg = f'Unknown move type: {move_type}'
        raise ValueError(msg)

    return axis, direction


def get_axis_for_facelet(coord: tuple[int, int, int], size: int) -> list[int]:
    """
    Determine which axis (face direction) a coordinate represents.

    For a piece at (x, y, z), returns which axis is on the surface:
    - If x == 0 or x == size-1: axis 0 (L/R)
    - If y == 0 or y == size-1: axis 1 (D/U)
    - If z == 0 or z == size-1: axis 2 (B/F)

    Args:
        coord: The (x, y, z) coordinate.
        size: Size of the cube.

    Returns:
        List of axes that are on the surface (1-3 values).

    """
    x, y, z = coord
    axes = []

    if x == 0 or x == size - 1:
        axes.append(0)
    if y == 0 or y == size - 1:
        axes.append(1)
    if z == 0 or z == size - 1:
        axes.append(2)

    return axes


def rotate_piece_orientation(
    axes: list[int],
    rotation_axis: int,
) -> list[int]:
    """
    Rotate the internal orientation of a piece.

    When a piece rotates around an axis, its facelets permute.
    This follows MagicCube's rotation logic.

    Args:
        axes: List of axes this piece has facelets on.
        rotation_axis: The axis around which we're rotating.

    Returns:
        Permuted list of axes.

    Raises:
        ValueError: If rotation_axis is not 0, 1, or 2.

    """
    if rotation_axis == 0:  # Rotating around x-axis (L/R moves)
        # [x, y, z] -> [x, z, y]
        mapping = {0: 0, 1: 2, 2: 1}
    elif rotation_axis == 1:  # Rotating around y-axis (U/D moves)
        # [x, y, z] -> [z, y, x]
        mapping = {0: 2, 1: 1, 2: 0}
    elif rotation_axis == 2:  # Rotating around z-axis (F/B moves)
        # [x, y, z] -> [y, x, z]
        mapping = {0: 1, 1: 0, 2: 2}
    else:
        msg = f'Invalid rotation axis: {rotation_axis}'
        raise ValueError(msg)

    return [mapping[axis] for axis in axes]


def build_coord_to_facelets_map(
    size: int,
) -> dict[tuple[int, int, int], list[tuple[int, int]]]:
    """
    Build a mapping from coordinates to ALL facelets on that piece.

    Each coordinate (corner/edge/center) may have multiple facelets.

    Args:
        size: Size of the cube.

    Returns:
        Dict mapping (x,y,z) -> [(facelet_idx, axis), ...].

    Raises:
        ValueError: If an unknown face is encountered.

    """
    face_coords = get_face_coordinates(size)
    coord_to_facelets: dict[tuple[int, int, int], list[tuple[int, int]]] = {}

    for face_idx, face in enumerate(FACE_ORDER):
        # Determine which axis this face represents
        if face in {'U', 'D'}:
            face_axis = 1
        elif face in {'R', 'L'}:
            face_axis = 0
        elif face in {'F', 'B'}:
            face_axis = 2
        else:
            msg = f'Unknown face: {face}'
            raise ValueError(msg)

        for local_idx, coord in enumerate(face_coords[face]):
            global_idx = face_idx * size * size + local_idx

            if coord not in coord_to_facelets:
                coord_to_facelets[coord] = []

            coord_to_facelets[coord].append((global_idx, face_axis))

    return coord_to_facelets


def calculate_permutation(size: int, move: str) -> list[int]:  # noqa: C901, PLR0914
    """
    Calculate the facelet permutation for a given move.

    Args:
        size: Size of the cube.
        move: Move string (e.g., 'R', "R'", 'R2', 'Rw', '2F',
            "3-4Rw'", 'x', "y'").

    Returns:
        Permutation array where result[i] = j means facelet i moves to
            position j.

    Raises:
        ValueError: If move is invalid or requires layers beyond cube size.

    """
    # Parse the move using Move class to extract layers and base move
    move_obj = Move(move)

    # Validate the move
    if not move_obj.is_valid:
        msg = f'Invalid move: {move}'
        raise ValueError(msg)

    # Get base move (without layers or modifiers)
    base_move = move_obj.base_move

    # For rotations, keep lowercase
    if base_move in 'XYZ':
        base_move = base_move.lower()

    # Get layer indices (0-indexed)
    layers = move_obj.layers

    # Validate layer indices don't exceed cube size
    if max(layers) >= size:
        msg = (
            f'Move {move} requires layer {max(layers) + 1} '
            f'but cube only has {size} layers'
        )
        raise ValueError(msg)

    # Determine number of 90-degree rotations
    num_rotations = 2 if move_obj.is_double else 1

    # Get axis and direction
    axis, base_direction = get_move_axis_and_direction(base_move)

    # Adjust direction for prime moves
    if move_obj.is_counter_clockwise:
        base_direction *= -1

    # Build coordinate to facelets mapping
    coord_to_facelets = build_coord_to_facelets_map(size)

    # Get coordinates that will be rotated
    affected_coords = get_slice_mask(size, base_move, layers)

    # Start with identity permutation
    total_facelets = 6 * size * size
    permutation = list(range(total_facelets))

    # Apply rotation(s)
    for _ in range(num_rotations):
        rotated_coords = rotate_coordinates_90(
            affected_coords, axis, size, base_direction,
        )

        # Build temporary mapping for this rotation
        temp_perm = list(range(total_facelets))

        for orig_coord, new_coord in zip(
            affected_coords, rotated_coords, strict=False,
        ):
            # Get facelets at original position
            orig_facelets = coord_to_facelets.get(orig_coord, [])
            new_facelets = coord_to_facelets.get(new_coord, [])

            if len(orig_facelets) != len(new_facelets):
                continue

            # Get original axes
            orig_axes = [axis_val for _, axis_val in orig_facelets]

            # Rotate the piece orientation
            rotated_axes = rotate_piece_orientation(orig_axes, axis)

            # Map old facelets to new positions with rotated orientation
            for (orig_idx, _orig_axis), rotated_axis in zip(
                orig_facelets, rotated_axes, strict=False,
            ):
                # Find which new facelet has this axis
                for new_idx, new_axis in new_facelets:
                    if new_axis == rotated_axis:
                        temp_perm[orig_idx] = new_idx
                        break

        # Compose with existing permutation
        permutation = [temp_perm[permutation[i]] for i in range(total_facelets)]

    return permutation


def apply_permutation(state: str, permutation: list[int]) -> str:
    """
    Apply a permutation to a cube state string.

    Args:
        state: Current cube state as facelet string.
        permutation: Permutation array.

    Returns:
        New cube state after applying permutation.

    """
    new_state = [''] * len(state)
    for i, j in enumerate(permutation):
        new_state[j] = state[i]
    return ''.join(new_state)


def rotate_move(state: str, move: str, size: int = 3) -> str:
    """
    Apply a single move to a cube state.

    Args:
        state: Current cube state as facelet string.
        move: Move to apply (e.g., 'R', "U'", 'F2').
        size: Size of the cube.

    Returns:
        New cube state after applying the move.

    """
    # Check cache
    cache_key = (size, move)
    if cache_key not in _PERMUTATION_CACHE:
        _PERMUTATION_CACHE[cache_key] = calculate_permutation(size, move)

    permutation = _PERMUTATION_CACHE[cache_key]
    return apply_permutation(state, permutation)
