"""Generate initial state for different cube size."""
from cubing_algs.constants import FACE_ORDER


def get_initial_state(size: int = 3) -> str:
    """
    Get the initial solved state for a cube of given size.

    Args:
        size: The size of the cube (2, 3, 4, etc.)

    Returns:
        A string representing the solved cube state.
        For 2x2x2: 24 characters (6 faces * 4 facelets)
        For 3x3x3: 54 characters (6 faces * 9 facelets)
        For NxNxN: 6*N*N characters

    Examples:
        >>> get_initial_state(2)
        'UUUURRRRFFFFDDDDLLLLBBBB'
        >>> get_initial_state(3)
        'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

    """
    facelets_per_face = size * size

    return ''.join(face * facelets_per_face for face in FACE_ORDER)
