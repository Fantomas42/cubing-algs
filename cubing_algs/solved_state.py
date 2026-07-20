"""Generate solved states for different cube sizes."""
from cubing_algs.annotations import CubeCubiesOriented
from cubing_algs.annotations import CubeFacelets
from cubing_algs.constants import DEFAULT_CUBE_SIZE
from cubing_algs.constants import EDGE_NUMBER
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_SO

printable_cache = ''


def build_printable_chars(count: int) -> str:
    """
    Build a string of `count` unique
    printable characters starting from chr(33).

    Args:
        count: number of unique characters

    Returns:
        A string containing only printable characters.

    """
    chars: list[str] = []
    code_point = 33

    while len(chars) < count:
        char = chr(code_point)
        if char.isprintable():
            chars.append(char)
        code_point += 1

    return ''.join(chars)


def get_unique_facelets(size: int = DEFAULT_CUBE_SIZE) -> CubeFacelets:
    """
    Get the facelets with unique symbol for a cube of given size.

    Args:
        size: The size of the cube (2, 3, 4, etc.)

    Returns:
        A string representing the unique facelets.
        For 2x2x2: 24 characters (6 faces * 4 facelets)
        For 3x3x3: 54 characters (6 faces * 9 facelets)
        For NxNxN: 6*N*N characters

    Examples:
        >>> get_unique_facelets(2)
        "!"#$%&'()*+,-./012345678"
        >>> get_unique_facelets(3)
        ""!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUV"

    """
    global printable_cache  # noqa: PLW0603
    total = size * size * len(FACE_ORDER)

    if len(printable_cache) < total:
        printable_cache = build_printable_chars(total)

    return printable_cache[:total]


def get_solved_facelets(size: int = DEFAULT_CUBE_SIZE) -> CubeFacelets:
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


def get_solved_cubies(size: int = DEFAULT_CUBE_SIZE) -> CubeCubiesOriented:
    """
    Get the cubies in solved state for a cube of given size.

    Args:
        size: The size of the cube (1, 2, 3, 4, etc.)

    Returns:
        A tuple of cubies state

    Notes:
        Actually does not represent center cubies for cube > 3.

    """
    if size == 1:
        return [], [], [], [], SOLVED_SO

    edges = EDGE_NUMBER * (size - 2)

    return SOLVED_CP, SOLVED_CO, list(range(edges)), [0] * edges, SOLVED_SO


SOLVED_FACELETS_3x3x3 = get_solved_facelets(3)
SOLVED_CUBIES_3x3x3 = get_solved_cubies(3)

UNIQUE_FACELETS_3x3x3 = get_unique_facelets(3)
