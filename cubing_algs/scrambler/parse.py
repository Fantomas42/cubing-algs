"""Parsing for advanced scrambler piece selection."""
from cubing_algs.annotations import Permutation
from cubing_algs.annotations import PieceType
from cubing_algs.constants import CORNER_NAMES
from cubing_algs.constants import EDGE_NAMES
from cubing_algs.constants import LAYER_MAP_CORNERS
from cubing_algs.constants import LAYER_MAP_EDGES
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EP
from cubing_algs.exceptions import InvalidPieceSpecError


def parse_piece_spec(spec: str, piece_type: PieceType) -> Permutation:
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
        return SOLVED_CP.copy() if piece_type == 'corner' else SOLVED_EP.copy()

    # Parse space-separated tokens
    tokens = spec.split()
    pieces: set[int] = set()

    names = CORNER_NAMES if piece_type == 'corner' else EDGE_NAMES
    layer_map = LAYER_MAP_CORNERS if piece_type == 'corner' else LAYER_MAP_EDGES

    for token in tokens:
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
