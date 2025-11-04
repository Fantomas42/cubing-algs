"""
Face position transformation utilities.

This module provides functions to transform facelet positions when moving
between adjacent faces on a Rubik's cube. These transformations account for
the rotation and orientation changes that occur when a facelet moves from
one face to another.
"""

from collections.abc import Callable


def offset_right(position: int) -> int:
    """
    Transform a position as if rotating it 90° clockwise (right).

    Maps positions as follows (in 3x3 grid):
    0 1 2    6 3 0
    3 4 5 -> 7 4 1
    6 7 8    8 5 2

    Args:
        position: The original position (0-8).

    Returns:
        The transformed position after 90° clockwise rotation.

    """
    return {
        0: 6,
        1: 3,
        2: 0,
        3: 7,
        4: 4,
        5: 1,
        6: 8,
        7: 5,
        8: 2,
    }[position]


def offset_left(position: int) -> int:
    """
    Transform a position as if rotating it 90° counter-clockwise (left).

    Maps positions as follows (in 3x3 grid):
    0 1 2    2 5 8
    3 4 5 -> 1 4 7
    6 7 8    0 3 6

    Args:
        position: The original position (0-8).

    Returns:
        The transformed position after 90° counter-clockwise rotation.

    """
    return {
        0: 2,
        1: 5,
        2: 8,
        3: 1,
        4: 4,
        5: 7,
        6: 0,
        7: 3,
        8: 6,
    }[position]


def offset_up(position: int) -> int:
    """
    Transform a position as if flipping it vertically (up).

    Maps positions as follows (in 3x3 grid):
    0 1 2    8 7 6
    3 4 5 -> 5 4 3
    6 7 8    2 1 0

    Args:
        position: The original position (0-8).

    Returns:
        The transformed position after vertical flip.

    """
    return {
        0: 8,
        1: 7,
        2: 6,
        3: 5,
        4: 4,
        5: 3,
        6: 2,
        7: 1,
        8: 0,
    }[position]


def offset_down(position: int) -> int:
    """
    Transform a position with no change (identity transformation).

    Maps positions as follows (in 3x3 grid):
    0 1 2    0 1 2
    3 4 5 -> 3 4 5
    6 7 8    6 7 8

    Args:
        position: The original position (0-8).

    Returns:
        The same position unchanged.

    """
    return {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
    }[position]


def offset_horizontal_mirror(position: int) -> int:
    """
    Transform a position as horizontal mirror.

    Maps positions as follows (in 3x3 grid):
    0 1 2    6 7 8
    3 4 5 -> 3 4 5
    6 7 8    0 1 2

    Args:
        position: The original position (0-8).

    Returns:
        The same position unchanged.
        The transformed position after horizontal mirroring.

    """
    return {
        0: 6,
        1: 7,
        2: 8,
        3: 3,
        4: 4,
        5: 5,
        6: 0,
        7: 1,
        8: 2,
    }[position]


def offset_vertical_mirror(position: int) -> int:
    """
    Transform a position as vertical mirror.

    Maps positions as follows (in 3x3 grid):
    0 1 2    2 1 0
    3 4 5 -> 5 4 3
    6 7 8    8 7 6

    Args:
        position: The original position (0-8).

    Returns:
        The same position unchanged.
        The transformed position after vertical mirroring.

    """
    return {
        0: 2,
        1: 1,
        2: 0,
        3: 5,
        4: 4,
        5: 3,
        6: 8,
        7: 7,
        8: 6,
    }[position]


# Mapping of how positions transform when moving between adjacent faces
# For each origin face, maps destination faces to the appropriate transformation
ADJACENT_FACE_TRANSFORMATIONS: dict[str, dict[str, Callable[[int], int]]] = {
    'U': {
        'R': offset_right,
        'L': offset_left,
        'F': offset_down,
        'B': offset_up,
    },
    'R': {
        'F': offset_down,
        'B': offset_down,
        'U': offset_left,
        'D': offset_right,
    },
    'F': {
        'U': offset_down,
        'D': offset_down,
        'L': offset_down,
        'R': offset_down,
    },
    'D': {
        'L': offset_right,
        'R': offset_left,
        'F': offset_down,
        'B': offset_up,
    },
    'L': {
        'F': offset_down,
        'B': offset_down,
        'U': offset_right,
        'D': offset_left,
    },
    'B': {
        'U': offset_up,
        'D': offset_up,
        'L': offset_down,
        'R': offset_down,
    },
}

# Mapping of how positions transform when moving between opposite faces
# For each origin face, maps destination faces to the appropriate transformation
OPPOSITE_FACE_TRANSFORMATIONS: dict[str, Callable[[int], int]] = {
    'U': offset_horizontal_mirror,
    'R': offset_vertical_mirror,
    'F': offset_vertical_mirror,
    'D': offset_horizontal_mirror,
    'L': offset_vertical_mirror,
    'B': offset_vertical_mirror,
}


def transform_adjacent_position(
        original_face_name: str,
        destination_face_name: str,
        destination_face_position: int) -> int:
    """
    Transform adjacent destination face position to original face position.

    Args:
        original_face_name: The original face identifier (U/R/F/D/L/B).
        destination_face_name: The destination face identifier.
        destination_face_position: Position on the destination face (0-8).

    Returns:
        The corresponding position on the original face.

    """
    return ADJACENT_FACE_TRANSFORMATIONS[
        original_face_name
    ][
        destination_face_name
    ](
        destination_face_position,
    )


def transform_opposite_position(face_name: str, face_position: int) -> int:
    """
    Transform opposite destination face position to original face position.

    Args:
        face_name: The original face identifier (U/R/F/D/L/B).
        face_position: Position on the destination face (0-8).

    Returns:
        The corresponding position on the original face.

    """
    return OPPOSITE_FACE_TRANSFORMATIONS[
        face_name
    ](
        face_position,
    )
