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


def transform_position(original_face_name: str, destination_face_name: str,
                       destination_face_position: int) -> int:
    """
    Transform destination face position to original face position.
    """
    return ADJACENT_FACE_TRANSFORMATIONS[
        original_face_name
    ][
        destination_face_name
    ](
        destination_face_position,
    )


# Shared edges between adjacent faces
# Maps face pairs to the edge position on each face that they share
SHARED_EDGES = {
    ('U', 'R'): (5, 12),   # U right edge, R left edge
    ('U', 'F'): (7, 19),   # U bottom edge, F top edge
    ('U', 'L'): (3, 39),   # U left edge, L top edge
    ('U', 'B'): (1, 46),   # U top edge, B top edge

    ('R', 'F'): (14, 23),  # R right edge, F right edge
    ('R', 'B'): (10, 48),  # R top edge, B left edge
    ('R', 'D'): (16, 32),  # R bottom edge, D right edge

    ('F', 'L'): (21, 41),  # F left edge, L right edge
    ('F', 'D'): (25, 28),  # F bottom edge, D top edge

    ('L', 'B'): (37, 50),  # L left edge, B right edge
    ('L', 'D'): (43, 30),  # L bottom edge, D left edge

    ('B', 'D'): (52, 34),  # B bottom edge, D bottom edge
}

# Add reverse mappings
for (f1, f2), (e1, e2) in list(SHARED_EDGES.items()):
    SHARED_EDGES[(f2, f1)] = (e2, e1)


# Edge orientation priority for adjacent face pairs
# Determines which edge type (vertical/horizontal) can be reached more efficiently
# 'vertical': edges at col==1 (positions 1, 7) are prioritized
# 'horizontal': edges at row==1 (positions 3, 5) are prioritized
EDGE_ORIENTATION_PRIORITY = {
    # U/D to side faces (R/L)
    ('U', 'R'): 'vertical',
    ('U', 'L'): 'vertical',
    ('D', 'R'): 'vertical',
    ('D', 'L'): 'vertical',
    ('R', 'U'): 'vertical',
    ('R', 'D'): 'vertical',
    ('L', 'U'): 'vertical',
    ('L', 'D'): 'vertical',

    # U/D to front/back faces (F/B)
    ('U', 'F'): 'horizontal',
    ('U', 'B'): 'horizontal',
    ('D', 'F'): 'horizontal',
    ('D', 'B'): 'horizontal',
    ('F', 'U'): 'horizontal',
    ('F', 'D'): 'horizontal',
    ('B', 'U'): 'horizontal',
    ('B', 'D'): 'horizontal',

    # Side to side
    ('R', 'F'): 'vertical',
    ('R', 'B'): 'vertical',
    ('F', 'R'): 'vertical',
    ('B', 'R'): 'vertical',
    ('L', 'F'): 'vertical',
    ('L', 'B'): 'vertical',
    ('F', 'L'): 'vertical',
    ('B', 'L'): 'vertical',

    # Front to back
    ('F', 'B'): 'horizontal',
    ('B', 'F'): 'horizontal',
}
