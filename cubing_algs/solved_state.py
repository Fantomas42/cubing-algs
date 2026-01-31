"""Generate solved state for different cube size."""
from cubing_algs.annotations import CubeFacelets
from cubing_algs.constants import FACE_ORDER


def get_solved_facelets(size: int = 3) -> CubeFacelets:
    """
    Get the facelets in solved state for a cube of given size.

    Args:
        size: The size of the cube (2, 3, 4, etc.)

    Returns:
        A string representing the solved cube state.
        For 2x2x2: 24 characters (6 faces * 4 facelets)
        For 3x3x3: 54 characters (6 faces * 9 facelets)
        For NxNxN: 6*N*N characters

    Examples:
        >>> get_solved_facelets(2)
        'UUUURRRRFFFFDDDDLLLLBBBB'
        >>> get_solved_facelets(3)
        'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

    """
    facelets_per_face = size * size

    return ''.join(face * facelets_per_face for face in FACE_ORDER)


SOLVED_FACELETS_3x3x3 = get_solved_facelets(3)
