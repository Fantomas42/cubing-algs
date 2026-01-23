"""Utility functions for advanced scrambler modules."""
import kociemba

from cubing_algs.exceptions import InvalidPieceSpecError
from cubing_algs.initial_state import INITIAL_STATE_3x3x3
from cubing_algs.vcube import VCube

CORNER_NAMES: list[str] = [
    'URF', 'UFL', 'ULB', 'UBR',
    'DFR', 'DLF', 'DBL', 'DRB',
]
EDGE_NAMES: list[str] = [
    'UR', 'UF', 'UL', 'UB',
    'DR', 'DF', 'DL', 'DB',
    'FR', 'FL', 'BL', 'BR',
]

# Layer piece groups
U_CORNERS: list[int] = [0, 1, 2, 3]  # URF, UFL, ULB, UBR
D_CORNERS: list[int] = [4, 5, 6, 7]  # DFR, DLF, DBL, DRB
R_CORNERS: list[int] = [0, 3, 4, 7]  # URF, UBR, DFR, DRB
L_CORNERS: list[int] = [1, 2, 5, 6]  # UFL, ULB, DLF, DBL
F_CORNERS: list[int] = [0, 1, 4, 5]  # URF, UFL, DFR, DLF
B_CORNERS: list[int] = [2, 3, 6, 7]  # ULB, UBR, DBL, DRB

U_EDGES: list[int] = [0, 1, 2, 3]    # UR, UF, UL, UB
D_EDGES: list[int] = [4, 5, 6, 7]    # DR, DF, DL, DB
R_EDGES: list[int] = [0, 4, 8, 11]   # UR, DR, FR, BR
L_EDGES: list[int] = [2, 6, 9, 10]   # UL, DL, FL, BL
F_EDGES: list[int] = [1, 5, 8, 9]    # UF, DF, FR, FL
B_EDGES: list[int] = [3, 7, 10, 11]  # UB, DB, BL, BR
E_EDGES: list[int] = [8, 9, 10, 11]  # FR, FL, BL, BR (middle slice)

ALL_CORNERS: list[int] = list(range(8))
ALL_EDGES: list[int] = list(range(12))

# Layer maps for piece specification parsing (module-level for efficiency)
LAYER_MAP_CORNERS: dict[str, list[int]] = {
    'U': U_CORNERS,
    'D': D_CORNERS,
    'R': R_CORNERS,
    'L': L_CORNERS,
    'F': F_CORNERS,
    'B': B_CORNERS,
}

LAYER_MAP_EDGES: dict[str, list[int]] = {
    'U': U_EDGES,
    'D': D_EDGES,
    'R': R_EDGES,
    'L': L_EDGES,
    'F': F_EDGES,
    'B': B_EDGES,
    'E': E_EDGES,
}


def parse_piece_spec(spec: str, piece_type: str) -> list[int]:
    """
    Parse piece specification string into list of cubie indices.

    Supports various formats:
    - "all" or empty string: All pieces of that type
    - "U", "D", "R", "L", "F", "B": All pieces on that layer
    - "URF UBR": Specific pieces by name (space-separated)
    - "U DFR": Mix of layer and specific pieces

    Args:
        spec: Space-separated piece specification string.
        piece_type: Either "corner" or "edge".

    Returns:
        List of cubie indices (in cubing_algs ordering).

    Raises:
        InvalidPieceSpecError: If piece type is invalid
        or piece name not recognized.

    Example:
        >>> parse_piece_spec("U", "corner")
        [0, 1, 2, 3]  # URF, UFL, ULB, UBR
        >>> parse_piece_spec("URF UBR", "corner")
        [0, 3]
        >>> parse_piece_spec("all", "edge")
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    """
    if piece_type not in {'corner', 'edge'}:
        msg = f"piece_type must be 'corner' or 'edge', got '{piece_type}'"
        raise InvalidPieceSpecError(msg)

    spec = spec.strip().upper()

    # Handle "all" or empty spec
    if spec in {'ALL', 'EACH', 'EVERY', 'ANY', ''}:
        return ALL_CORNERS if piece_type == 'corner' else ALL_EDGES

    # Parse space-separated tokens
    tokens = spec.split()
    pieces: set[int] = set()

    names = CORNER_NAMES if piece_type == 'corner' else EDGE_NAMES
    layer_map = LAYER_MAP_CORNERS if piece_type == 'corner' else LAYER_MAP_EDGES

    for token_raw in tokens:
        token = token_raw.strip()
        if not token:
            continue

        # Check if it's a layer specifier
        if len(token) == 1 and token in layer_map:
            pieces.update(layer_map[token])
        else:
            # It's a specific piece name
            try:
                idx = names.index(token)
                pieces.add(idx)
            except ValueError:
                msg = (
                    f"Unknown {piece_type} piece '{token}'. "
                    f"Valid {piece_type}s: {', '.join(names)}"
                )
                raise InvalidPieceSpecError(msg) from None

    return sorted(pieces)


def vcube_to_kociemba_string(cube: VCube) -> str:
    """
    Convert VCube state to Kociemba solver format.

    The Kociemba format is a 54-character string representing the cube state
    in a specific facelet ordering: URFDLB (U face, then R, then F, etc.).
    Each face is read in row-major order (left-to-right, top-to-bottom).

    Args:
        cube: VCube instance (must be 3x3x3).

    Returns:
        54-character string in Kociemba format (URFDLB ordering).

    Raises:
        ValueError: If cube is not 3x3x3.

    """
    if cube.size != 3:
        msg = (
            f'Kociemba solver only supports 3x3x3 cubes, '
            f'got {cube.size}x{cube.size}x{cube.size}'
        )
        raise ValueError(msg)

    # VCube uses URFDLB ordering, which matches Kociemba
    # Just need to ensure we return the state string directly
    return cube.state


def solve_to_algorithm(kociemba_state: str) -> str:
    """
    Generate solving algorithm for a given cube state using Kociemba solver.

    This function requires the kociemba package to be installed.
    Install with: pip install kociemba

    Args:
        kociemba_state: Cube state in Kociemba format (54-character string).

    Returns:
        Algorithm string to solve the cube (space-separated moves).

    """
    if kociemba_state == INITIAL_STATE_3x3x3:
        return ''

    solution: str = kociemba.solve(kociemba_state)
    return solution
