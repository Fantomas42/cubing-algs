"""
Impact analysis tools for Rubik's cube algorithms.

This module provides functions to analyze the spatial impact of algorithms
on cube facelets, including which facelets are moved, how they move,
and statistical analysis of the algorithm's effect on the cube.
"""
from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import TypedDict

from cubing_algs.constants import CORNER_FACELET_MAP
from cubing_algs.constants import D_CORNERS
from cubing_algs.constants import D_EDGES
from cubing_algs.constants import E_EDGES
from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import FACE_EDGES_INDEX
from cubing_algs.constants import FACE_NUMBER
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.constants import QTM_OPPOSITE_EDGE_OFFSETS
from cubing_algs.constants import QTM_OPPOSITE_FACE_DOUBLE_PAIRS
from cubing_algs.constants import QTM_SAME_FACE_OPPOSITE_PAIRS
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.constants import SOLVED_EP
from cubing_algs.constants import U_CORNERS
from cubing_algs.constants import U_EDGES
from cubing_algs.face_transforms import transform_adjacent_position
from cubing_algs.face_transforms import transform_opposite_position
from cubing_algs.integrity import compute_parity
from cubing_algs.integrity import find_permutation_cycles

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover
    from cubing_algs.vcube import VCube  # pragma: no cover

# Precomputed lookup: facelet index → piece index for O(1) same-piece checks.
CACHED_FACELET_TO_EDGE_PIECE: dict[int, int] = {
    facelet: i
    for i, edge in enumerate(EDGE_FACELET_MAP)
    for facelet in edge
}
CACHED_FACELET_TO_CORNER_PIECE: dict[int, int] = {
    facelet: i
    for i, corner in enumerate(CORNER_FACELET_MAP)
    for facelet in corner
}


class CycleAnalysis(TypedDict):
    """Analysis of permutation cycle structure."""

    cycle_count: int
    cycle_lengths: list[int]
    min_cycle_length: int
    max_cycle_length: int
    total_pieces_in_cycles: int
    two_cycles: int
    three_cycles: int
    four_plus_cycles: int


class DistanceMetrics(NamedTuple):
    """Container for distance calculation results."""

    distances: dict[int, int]
    mean: float
    max: int
    sum: int


class FaceletPosition(NamedTuple):
    """Parsed facelet position information."""

    face_index: int
    face_name: str
    face_position: int
    row: int
    col: int

    original: int


class ImpactData(NamedTuple):
    """
    Container for comprehensive impact computation results.

    Combines facelet-based spatial analysis with cubie-based piece tracking
    to provide a complete picture of an algorithm's effect on the cube.

    Facelet metrics track visual changes on the cube surface.
    Cubie metrics track the underlying piece movements and orientations.
    """

    cube: 'VCube'

    # Facelet analysis (visual/spatial impact)
    facelets_state: str
    facelets_transformation_mask: str
    facelets_fixed_count: int
    facelets_mobilized_count: int
    facelets_scrambled_percent: float
    facelets_permutations: dict[int, int]
    facelets_face_mobility: dict[str, int]
    facelets_face_to_face_matrix: dict[str, dict[str, int]]
    facelets_symmetry: dict[str, bool]
    facelets_qtm_distance: DistanceMetrics | None
    facelets_manhattan_distance: DistanceMetrics | None
    facelets_layer_analysis: dict[str, int] | None

    # Cubie analysis (piece-level impact, 3x3x3 only)
    cubies_corner_permutation: list[int] | None
    cubies_corner_orientation: list[int] | None
    cubies_edge_permutation: list[int] | None
    cubies_edge_orientation: list[int] | None
    cubies_corners_moved: int | None
    cubies_corners_twisted: int | None
    cubies_edges_moved: int | None
    cubies_edges_flipped: int | None
    cubies_corner_cycles: list[list[int]] | None
    cubies_edge_cycles: list[list[int]] | None
    cubies_complexity_score: int | None
    cubies_suggested_approach: str | None
    cubies_corner_parity: int | None
    cubies_edge_parity: int | None
    cubies_parity_valid: bool | None
    cubies_corner_cycle_analysis: CycleAnalysis | None
    cubies_edge_cycle_analysis: CycleAnalysis | None
    cubies_patterns: list[str] | None


def compute_face_impact(impact_mask: str, cube: 'VCube') -> dict[str, int]:
    """
    Calculate face impact from impact mask.

    Args:
        impact_mask: Binary mask indicating affected facelets.
        cube: The virtual cube to analyze.

    Returns:
        Dictionary mapping face names to counts of affected facelets.

    """
    face_impact = {}

    for i, face_name in enumerate(FACE_ORDER):
        start_idx = i * cube.face_size
        end_idx = start_idx + cube.face_size
        face_mask = impact_mask[start_idx:end_idx]
        face_impact[face_name] = face_mask.count('1')

    return face_impact


def parse_facelet_position(position: int, cube: 'VCube') -> FaceletPosition:
    """
    Parse a facelet position into face, row, and column components.

    Args:
        position: The facelet position index (0-53).
        cube: The virtual cube for size context.

    Returns:
        FaceletPosition with parsed components.

    """
    face_index = position // cube.face_size
    face_name = FACE_ORDER[face_index]
    position_in_face = position % cube.face_size
    row = position_in_face // cube.size
    col = position_in_face % cube.size

    return FaceletPosition(
        face_index=face_index,
        face_name=face_name,
        face_position=position_in_face,
        row=row,
        col=col,
        original=position,
    )


def positions_on_same_piece(pos1: int, pos2: int) -> bool:
    """
    Check if two positions are on the same physical piece (edge or corner).

    Returns True if the positions are on the same edge or corner piece,
    meaning they are the same physical location viewed from different faces.

    Args:
        pos1: The original facelet position index.
        pos2: The final facelet position index.

    Returns:
        True if both positions are on the same physical piece.

    """
    e1 = CACHED_FACELET_TO_EDGE_PIECE.get(pos1)
    if e1 is not None and e1 == CACHED_FACELET_TO_EDGE_PIECE.get(pos2):
        return True

    c1 = CACHED_FACELET_TO_CORNER_PIECE.get(pos1)
    return c1 is not None and c1 == CACHED_FACELET_TO_CORNER_PIECE.get(pos2)


def positions_on_adjacent_corners(pos1: int, pos2: int, cube: 'VCube') -> bool:
    """
    Check if two positions are on corners that share an edge.

    Adjacent corners share exactly 2 faces (they're connected by an edge).

    Args:
        pos1: The first facelet position index.
        pos2: The second facelet position index.
        cube: The virtual cube for size context.

    Returns:
        True if positions are on adjacent corners.

    """
    corner1 = None
    corner2 = None

    for corner in CORNER_FACELET_MAP:
        if pos1 in corner:
            corner1 = corner
        if pos2 in corner:
            corner2 = corner

    if corner1 is None or corner2 is None:
        return False

    if corner1 == corner2:  # Same corner
        return False

    # Get the faces for each corner
    faces1 = {p // cube.face_size for p in corner1}
    faces2 = {p // cube.face_size for p in corner2}

    # Adjacent corners share exactly 2 faces (an edge)
    return len(faces1 & faces2) == 2


def compute_within_face_manhattan_distance(
        orig: FaceletPosition,
        final: FaceletPosition,
) -> int:
    """
    Calculate Manhattan distance for positions on the same face.

    Args:
        orig: The original facelet position.
        final: The final facelet position.

    Returns:
        Manhattan distance in grid units.

    """
    return abs(orig.row - final.row) + abs(orig.col - final.col)


def compute_opposite_face_manhattan_distance(
        orig: FaceletPosition,
        final: FaceletPosition,
        cube: 'VCube',
) -> int:
    """
    Calculate Manhattan distance for positions on opposite faces.

    Uses position transformation to determine the aligned reference point
    on the destination face, then calculates cross-face and within-face
    components of the distance.

    For centers: Returns 2 * cube_size (6 for 3x3x3).
    For others: Base cross-face distance (4) + within-face distance.

    Args:
        orig: The original facelet position.
        final: The final facelet position.
        cube: The virtual cube for size context.

    Returns:
        Manhattan distance across opposite faces.

    """
    if orig.face_position == cube.center_index:
        return cube.size * 2

    translated_pos = transform_opposite_position(
        final.face_name,
        final.face_position,
    )
    translated = parse_facelet_position(translated_pos, cube)

    within_face_distance = abs(
        translated.row - orig.row,
    ) + abs(
        translated.col - orig.col,
    )

    return within_face_distance + cube.size + 1


def compute_adjacent_face_manhattan_distance(
        orig: FaceletPosition,
        final: FaceletPosition,
        cube: 'VCube',
) -> int:
    """
    Calculate Manhattan distance for positions on adjacent faces.

    Uses face transformation to determine the aligned position,
    then calculates the shortest path accounting for edge crossing.

    Args:
        orig: The parsed original facelet position.
        final: The parsed final facelet position.
        cube: The virtual cube for size context.

    Returns:
        Manhattan distance across adjacent faces.

    """
    if positions_on_same_piece(orig.original, final.original):
        return 1

    # Check if positions are on adjacent corners (corners sharing an edge)
    if positions_on_adjacent_corners(orig.original, final.original, cube):
        return 3

    # Transform original position to destination face coordinate system
    translated_face_pos = transform_adjacent_position(
        final.face_name,
        orig.face_name,
        orig.face_position,
    )
    # Convert face position to global position
    translated_pos = final.face_index * cube.face_size + translated_face_pos
    translated = parse_facelet_position(translated_pos, cube)

    if positions_on_same_piece(translated_pos, final.original):
        return 3

    # Distance components:
    # 1. Distance to reach the edge (minimum distance to any edge position)
    # 2. Distance from edge to final position
    #
    # For adjacent faces, we add cube.size as the cross-face component
    # plus the within-face distance between transformed and final positions
    within_face_distance = abs(
        translated.row - final.row,
    ) + abs(
        translated.col - final.col,
    )

    return cube.size + within_face_distance


def compute_manhattan_distance(original_pos: int, final_pos: int,
                               cube: 'VCube') -> int:
    """
    Calculate Manhattan displacement distance between two positions.

    Manhattan distance measures the sum of absolute differences in row and
    column coordinates, extended across faces. For cross-face movements,
    it accounts for the minimum path through adjacent or opposite faces.

    Args:
        original_pos: The original facelet position index.
        final_pos: The final facelet position index.
        cube: The virtual cube for size context.

    Returns:
        Manhattan distance between the positions.

    """
    if original_pos == final_pos:
        return 0

    orig = parse_facelet_position(original_pos, cube)
    final = parse_facelet_position(final_pos, cube)

    # Case 1: Same face movements
    if orig.face_index == final.face_index:
        return compute_within_face_manhattan_distance(
            orig, final,
        )

    # Case 2: Opposite faces
    if orig.face_name == OPPOSITE_FACES[final.face_name]:
        return compute_opposite_face_manhattan_distance(
            orig, final, cube,
        )

    # Case 3: Adjacent faces
    return compute_adjacent_face_manhattan_distance(
        orig, final, cube,
    )


def compute_within_face_qtm_distance(
        orig: FaceletPosition,
        final: FaceletPosition) -> int:
    """
    Calculate QTM distance for positions on the same face.

    Args:
        orig: The parsed original facelet position.
        final: The parsed final facelet position.

    Returns:
        QTM distance (1 or 2 quarter turns).

    """
    key = (orig.face_position, final.face_position)

    if key in QTM_SAME_FACE_OPPOSITE_PAIRS:
        return 2

    return 1


def compute_opposite_face_qtm_distance(
        orig: FaceletPosition,
        final: FaceletPosition) -> int:
    """
    Calculate QTM distance for positions on opposite faces.

    Args:
        orig: The parsed original facelet position.
        final: The parsed final facelet position.

    Returns:
        QTM distance (2-4 quarter turns).

    """
    if orig.face_position == 4:
        return 4  # Center: slice move like M2 or S2

    if orig.face_position == final.face_position:
        return 2

    key = (orig.face_position, final.face_position)

    if key in QTM_OPPOSITE_FACE_DOUBLE_PAIRS:
        return 2

    return 3


def compute_adjacent_face_edge_qtm_distance(
        original_pos: int, final_pos: int,
        orig_face_pos: int,
        final_face_pos: int) -> int | None:
    """
    Calculate QTM distance for edge pieces on adjacent faces.

    Returns None if distance cannot be determined by edge analysis.

    Args:
        original_pos: The original facelet position index.
        final_pos: The final facelet position index.
        orig_face_pos: Position on the original face (0-8).
        final_face_pos: Position on the final face (0-8).

    Returns:
        QTM distance, or None if cannot be determined.

    """
    # Same edge piece requires 3 quarter turns (opposite sides of piece)
    if positions_on_same_piece(original_pos, final_pos):
        return 3

    # Check if opposite edge is same piece as final
    opposite_edge_pos = original_pos + QTM_OPPOSITE_EDGE_OFFSETS[orig_face_pos]
    if positions_on_same_piece(opposite_edge_pos, final_pos):
        return 2

    # Check symmetric case: opposite of final position
    opposite_final_pos = final_pos + QTM_OPPOSITE_EDGE_OFFSETS[final_face_pos]
    if positions_on_same_piece(opposite_final_pos, original_pos):
        return 2

    return None


def compute_adjacent_face_qtm_distance(
        orig: FaceletPosition,
        final: FaceletPosition,
        cube: 'VCube',
) -> int:
    """
    Calculate QTM distance for positions on adjacent faces.

    Args:
        orig: The parsed original facelet position.
        final: The parsed final facelet position.
        cube: The virtual cube for size context.

    Returns:
        QTM distance in quarter turns.

    """
    if orig.face_position == 4:
        return 2  # Center: slice move like M or S

    # Special handling for edge pieces on adjacent faces
    if orig.face_position in FACE_EDGES_INDEX:
        edge_distance = compute_adjacent_face_edge_qtm_distance(
            orig.original,
            final.original,
            orig.face_position,
            final.face_position,
        )
        if edge_distance is not None:
            return edge_distance

    # General adjacent face handling via transformation
    translated_face_pos = transform_adjacent_position(
        final.face_name,
        orig.face_name,
        orig.face_position,
    )
    # Convert face position to global position
    translated_pos = final.face_index * cube.face_size + translated_face_pos
    translated = parse_facelet_position(translated_pos, cube)

    if translated.face_position == final.face_position:
        return 1

    # Check distance after one transformation
    pos_pair = (translated.face_position, final.face_position)
    if pos_pair in QTM_SAME_FACE_OPPOSITE_PAIRS:
        return 3

    return 2


def compute_qtm_distance(original_pos: int, final_pos: int,
                         cube: 'VCube') -> int:
    """
    Calculate QTM (Quarter Turn Metric) distance between two positions.

    QTM distance represents the minimum number of quarter turns needed
    to move a facelet from its original position to its final position.

    Args:
        original_pos: The original facelet position index.
        final_pos: The final facelet position index.
        cube: The virtual cube for size context.

    Returns:
        Minimum number of quarter turns required.

    """
    if original_pos == final_pos:
        return 0

    orig = parse_facelet_position(original_pos, cube)
    final = parse_facelet_position(final_pos, cube)

    # Case 1: Same face movements
    if orig.face_index == final.face_index:
        return compute_within_face_qtm_distance(
            orig, final,
        )

    # Case 2: Opposite faces
    if orig.face_name == OPPOSITE_FACES[final.face_name]:
        return compute_opposite_face_qtm_distance(
            orig, final,
        )

    # Case 3: Adjacent faces
    return compute_adjacent_face_qtm_distance(
        orig, final, cube,
    )


def compute_distance_metrics(
    permutations: dict[int, int],
    cube: 'VCube',
    distance_fn: Callable[[int, int, 'VCube'], int],
) -> DistanceMetrics:
    """
    Compute distance metrics for a set of permutations.

    Args:
        permutations: Dictionary mapping original to final positions.
        cube: The virtual cube for size context.
        distance_fn: Function to compute distance between two positions.

    Returns:
        DistanceMetrics containing distances, mean, max, and sum.

    """
    distances = {
        original_pos: distance_fn(original_pos, final_pos, cube)
        for original_pos, final_pos in permutations.items()
    }

    distance_values = list(distances.values())
    distance_sum = sum(distance_values)
    distance_mean = (
        distance_sum / len(distance_values)
        if distance_values else 0.0
    )
    distance_max = max(distance_values) if distance_values else 0

    return DistanceMetrics(
        distances=distances,
        mean=distance_mean,
        max=distance_max,
        sum=distance_sum,
    )


def compute_face_to_face_matrix(
        permutations: dict[int, int],
        cube: 'VCube',
) -> dict[str, dict[str, int]]:
    """
    Compute face-to-face movement matrix.

    Tracks how many facelets from each face end up on each other face.

    Args:
        permutations: Dictionary mapping original to final positions.
        cube: The virtual cube for size context.

    Returns:
        Nested dictionary: matrix[orig_face][dest_face] = count.

    """
    matrix: dict[str, dict[str, int]] = {
        face: dict.fromkeys(FACE_ORDER, 0)
        for face in FACE_ORDER
    }

    for orig_pos, final_pos in permutations.items():
        orig_face = FACE_ORDER[orig_pos // cube.face_size]
        final_face = FACE_ORDER[final_pos // cube.face_size]
        matrix[orig_face][final_face] += 1

    return matrix


def detect_symmetry(mask: str, cube: 'VCube') -> dict[str, bool]:
    """
    Detect symmetry patterns in the transformation mask.

    Checks for rotational and mirror symmetries in the impact pattern.

    Args:
        mask: Binary mask string indicating affected facelets.
        cube: The virtual cube for size context.

    Returns:
        Dictionary with symmetry flags (all_faces_same,
        opposite_faces_symmetric, etc).

    """
    # Extract face masks
    faces = []
    for i in range(FACE_NUMBER):
        start = i * cube.face_size
        end = start + cube.face_size
        faces.append(mask[start:end])

    # Check for full symmetry (all faces same pattern)
    all_same = all(face == faces[0] for face in faces)

    # Check for opposite face symmetry
    opposite_symmetry = (
        faces[0] == faces[3]  # U == D
        and faces[1] == faces[4]  # R == L
        and faces[2] == faces[5]  # F == B
    )

    # Check if pattern is empty or full
    is_empty = mask == '0' * len(mask)
    is_full = mask == '1' * len(mask)

    return {
        'all_faces_same': all_same,
        'opposite_faces_symmetric': opposite_symmetry,
        'no_impact': is_empty,
        'full_impact': is_full,
    }


def analyze_layers(
        permutations: dict[int, int],
        cube: 'VCube',
) -> dict[str, int]:
    """
    Analyze impact by cube layers.

    Separates facelets into outer layer (edges/corners) and center pieces.

    Args:
        permutations: Dictionary mapping original to final positions.
        cube: The virtual cube for size context.

    Returns:
        Dictionary with layer counts (centers_moved, outer_layer_moved, etc).

    """
    # Center of each face (position 4 in 3x3 grid)
    center_indices = {
        i * cube.face_size + cube.center_index
        for i in range(FACE_NUMBER)
    }
    edge_indices = set()
    corner_indices = set()

    for face_idx in range(FACE_NUMBER):
        face_start = face_idx * cube.face_size
        # Corners: positions 0, 2, 6, 8 in each face
        corner_indices.update({
            face_start + 0, face_start + 2,
            face_start + 6, face_start + 8,
        })
        # Edges: positions 1, 3, 5, 7 in each face
        edge_indices.update({
            face_start + 1, face_start + 3,
            face_start + 5, face_start + 7,
        })

    centers_moved = sum(
        1 for pos in permutations
        if pos in center_indices
    )
    edges_moved = sum(
        1 for pos in permutations
        if pos in edge_indices
    )
    corners_moved = sum(
        1 for pos in permutations
        if pos in corner_indices
    )

    return {
        'centers_moved': centers_moved,
        'edges_moved': edges_moved,
        'corners_moved': corners_moved,
    }


def analyze_cycles(cycles: list[list[int]]) -> CycleAnalysis:
    """
    Analyze cycle structure in detail.

    Args:
        cycles: List of cycles, each cycle is a list of position indices.

    Returns:
        CycleAnalysis with detailed cycle statistics.

    """
    if not cycles:
        return {
            'cycle_count': 0,
            'cycle_lengths': [],
            'min_cycle_length': 0,
            'max_cycle_length': 0,
            'total_pieces_in_cycles': 0,
            'two_cycles': 0,
            'three_cycles': 0,
            'four_plus_cycles': 0,
        }

    cycle_lengths = [len(c) for c in cycles]

    return {
        'cycle_count': len(cycles),
        'cycle_lengths': cycle_lengths,
        'min_cycle_length': min(cycle_lengths),
        'max_cycle_length': max(cycle_lengths),
        'total_pieces_in_cycles': sum(cycle_lengths),
        'two_cycles': sum(1 for length in cycle_lengths if length == 2),
        'three_cycles': sum(1 for length in cycle_lengths if length == 3),
        'four_plus_cycles': sum(1 for length in cycle_lengths if length >= 4),
    }


def classify_pattern(  # noqa: C901, PLR0912, PLR0915
        cp: list[int], co: list[int],
        ep: list[int], eo: list[int],
) -> list[str]:
    """
    Comprehensive pattern classification for speedcubing.

    Identifies specific cube states and patterns useful for solving.

    Args:
        cp: Corner permutation.
        co: Corner orientation.
        ep: Edge permutation.
        eo: Edge orientation.

    Returns:
        List of pattern names identifying the cube state.

    """
    patterns = []

    # Basic state checks
    if (cp == SOLVED_CP and co == SOLVED_CO and
        ep == SOLVED_EP and eo == SOLVED_EO):
        patterns.append('SOLVED')
        return patterns  # If solved, no other patterns apply

    # Orientation patterns
    all_corners_oriented = all(orientation == 0 for orientation in co)
    all_edges_oriented = all(orientation == 0 for orientation in eo)

    if all_corners_oriented and all_edges_oriented:
        patterns.append('ALL_ORIENTED')

    if all_corners_oriented:
        patterns.append('CORNERS_ORIENTED')

    if all_edges_oriented:
        patterns.append('EDGES_ORIENTED')

    # Permutation patterns
    corners_permuted = cp == SOLVED_CP
    edges_permuted = ep == SOLVED_EP

    if corners_permuted and edges_permuted:
        patterns.append('ALL_PERMUTED')

    if corners_permuted:
        patterns.append('CORNERS_PERMUTED')

    if edges_permuted:
        patterns.append('EDGES_PERMUTED')

    # CFOP-specific patterns
    if all_corners_oriented and not all_edges_oriented:
        patterns.append('OLL_CORNERS_DONE')

    if all_edges_oriented and not all_corners_oriented:
        patterns.append('OLL_EDGES_DONE')

    if (
            all_corners_oriented
            and all_edges_oriented
            and not (corners_permuted and edges_permuted)
    ):
        patterns.append('OLL_COMPLETE_PLL_REMAINING')

    if (
            corners_permuted and edges_permuted
            and (not all_corners_oriented or not all_edges_oriented)
    ):
        patterns.append('PERMUTED_BUT_MISORIENTED')

    # Layer-by-layer patterns
    # Check if first layer (D face) corners are solved
    d_corners_solved = all(
        cp[i] == i and co[i] == 0
        for i in D_CORNERS
    )
    if d_corners_solved:
        patterns.append('FIRST_LAYER_CORNERS_SOLVED')

    # Check if first layer edges are solved
    d_edges = D_EDGES
    d_edges_solved = all(
        ep[i] == i and eo[i] == 0
        for i in d_edges
    )
    if d_edges_solved:
        patterns.append('FIRST_LAYER_EDGES_SOLVED')

    if d_corners_solved and d_edges_solved:
        patterns.append('FIRST_LAYER_COMPLETE')

    # Check for cross (D edges solved)
    if d_edges_solved:
        patterns.append('CROSS_SOLVED')

    # F2L specific patterns
    f2l_edges_solved = False
    if d_corners_solved and d_edges_solved:
        # Check if F2L is complete (D layer + E slice edges)
        f2l_edges_solved = all(
            ep[i] == i and eo[i] == 0
            for i in E_EDGES
        )
        if f2l_edges_solved:
            patterns.append('F2L_COMPLETE')

    # Last layer patterns
    u_corners_oriented = all(co[i] == 0 for i in U_CORNERS)
    u_edges_oriented = all(eo[i] == 0 for i in U_EDGES)

    if u_corners_oriented and u_edges_oriented:
        patterns.append('LAST_LAYER_ORIENTED')

    # PLL patterns (all oriented, but permuted)
    if u_corners_oriented and u_edges_oriented:
        u_corners_permuted = all(cp[i] in U_CORNERS for i in U_CORNERS)
        u_edges_permuted = all(ep[i] in U_EDGES for i in U_EDGES)

        if not u_corners_permuted or not u_edges_permuted:
            patterns.append('PLL_CASE')

            # Specific PLL types
            if u_corners_permuted and not u_edges_permuted:
                patterns.append('PLL_EDGES_ONLY')

            if not u_corners_permuted and u_edges_permuted:
                patterns.append('PLL_CORNERS_ONLY')

    # OLL patterns (last layer not oriented)
    if ((not u_corners_oriented or not u_edges_oriented)
            and d_corners_solved and d_edges_solved and f2l_edges_solved):
        patterns.append('OLL_CASE')

    # Special patterns
    # Checkerboard-like (many pieces moved)
    if len([i for i, pos in enumerate(cp) if pos != i]) >= 6:
        patterns.append('HIGHLY_SCRAMBLED')

    # Minimal scramble
    if len([i for i, pos in enumerate(cp) if pos != i]) <= 2:
        patterns.append('MINIMALLY_SCRAMBLED')

    # Check permutation structure (orientation constraints)
    corner_cycles = find_permutation_cycles(cp)
    edge_cycles = find_permutation_cycles(ep)

    if len(corner_cycles) == 1 and len(corner_cycles[0]) == len(cp):
        patterns.append('SINGLE_CORNER_CYCLE')

    if len(edge_cycles) == 1 and len(edge_cycles[0]) == len(ep):
        patterns.append('SINGLE_EDGE_CYCLE')

    # Check for swaps (2-cycles)
    if len(corner_cycles) == 1 and len(corner_cycles[0]) == 2:
        patterns.append('SINGLE_CORNER_SWAP')

    if len(edge_cycles) == 1 and len(edge_cycles[0]) == 2:
        patterns.append('SINGLE_EDGE_SWAP')

    # Three-cycles (common in commutators)  # noqa: ERA001
    if any(len(cycle) == 3 for cycle in corner_cycles):
        patterns.append('CORNER_THREE_CYCLE')

    if any(len(cycle) == 3 for cycle in edge_cycles):
        patterns.append('EDGE_THREE_CYCLE')

    if not patterns:
        patterns.append('UNCLASSIFIED')

    return patterns


def compute_cubie_complexity(
    corners_moved: int, corners_twisted: int,
    edges_moved: int, edges_flipped: int,
) -> tuple[int, str]:
    """
    Compute complexity score and suggested solving approach.

    Based on the pattern recognition approach from the notebook's
    "Optimization with Cubies" section.

    Args:
        corners_moved: Number of corners out of place.
        corners_twisted: Number of corners incorrectly oriented.
        edges_moved: Number of edges out of place.
        edges_flipped: Number of edges incorrectly oriented.

    Returns:
        Tuple of (complexity_score, suggested_approach).

    """
    complexity = corners_moved + corners_twisted + edges_moved + edges_flipped

    if complexity == 0:
        approach = 'Solved state'
    elif corners_twisted == 0 and edges_flipped == 0:
        approach = 'PLL case - permutation only, use permutation algorithms'
    elif corners_moved == 0 and edges_moved == 0:
        approach = 'OLL case - orientation only, use orientation algorithms'
    elif complexity < 8:
        approach = 'Simple case - direct algorithms may be sufficient'
    else:
        approach = 'Complex case - multi-stage solving approach recommended'

    return complexity, approach


def compute_impacts(algorithm: 'Algorithm',  # noqa: PLR0914, PLR0915
                    size: int = 3) -> ImpactData:
    """
    Compute comprehensive impact metrics for an algorithm.

    Analyzes facelet-level (visual/spatial) impacts for any cube size.
    Cubie-level (piece) analysis is only available for 3x3x3 cubes.

    Args:
        algorithm: The algorithm to analyze.
        size: Size of the cube (default 3).

    Returns:
        ImpactData with facelet metrics for all sizes.
        Cubie metrics and distance metrics are None for non-3x3x3.

    """
    from cubing_algs.masks import compute_algorithm_mask  # noqa: PLC0415
    from cubing_algs.solved_state import get_unique_facelets  # noqa: PLC0415
    from cubing_algs.transform.pause import unpause_moves  # noqa: PLC0415
    from cubing_algs.transform.timing import untime_moves  # noqa: PLC0415
    from cubing_algs.vcube import VCube  # noqa: PLC0415

    cleaned_algorithm = algorithm.transform(
        unpause_moves,
        untime_moves,
    )

    cube = VCube(size=size)
    cube.rotate(cleaned_algorithm)

    mask, transformed_state = compute_algorithm_mask(
        cleaned_algorithm, size,
    )

    unique_facelets = get_unique_facelets(size)
    permutations: dict[int, int] = {}
    for original_pos in range(len(unique_facelets)):
        final_pos = transformed_state.find(
            unique_facelets[original_pos],
        )

        if final_pos != original_pos:
            permutations[original_pos] = final_pos

    # Facelet metrics (size-agnostic)
    fixed_count = mask.count('0')
    mobilized_count = mask.count('1')
    # Odd-sized cubes have fixed center facelets (one per face)
    immovable_count = cube.face_number if cube.has_fixed_centers else 0
    scrambled_percent = mobilized_count / (
        len(unique_facelets) - immovable_count
    )

    face_mobility = compute_face_impact(mask, cube)
    face_to_face_matrix = compute_face_to_face_matrix(permutations, cube)
    symmetry = detect_symmetry(mask, cube)

    # 3x3x3-specific analysis (distances, layers, cubies)
    manhattan_distance: DistanceMetrics | None = None
    qtm_distance: DistanceMetrics | None = None
    layer_analysis: dict[str, int] | None = None
    cp: list[int] | None = None
    co: list[int] | None = None
    ep: list[int] | None = None
    eo: list[int] | None = None
    corners_moved: int | None = None
    corners_twisted: int | None = None
    edges_moved: int | None = None
    edges_flipped: int | None = None
    corner_cycles: list[list[int]] | None = None
    edge_cycles: list[list[int]] | None = None
    complexity_score: int | None = None
    suggested_approach: str | None = None
    corner_parity: int | None = None
    edge_parity: int | None = None
    parity_valid: bool | None = None
    corner_cycle_analysis: CycleAnalysis | None = None
    edge_cycle_analysis: CycleAnalysis | None = None
    patterns: list[str] | None = None

    if size == 3:
        oriented_cube = cube.oriented_copy('UF')

        manhattan_distance = compute_distance_metrics(
            permutations, oriented_cube, compute_manhattan_distance,
        )
        qtm_distance = compute_distance_metrics(
            permutations, oriented_cube, compute_qtm_distance,
        )
        layer_analysis = analyze_layers(permutations, oriented_cube)

        cp, co, ep, eo, _so = oriented_cube.cubies

        corners_moved = sum(1 for i, pos in enumerate(cp) if pos != i)
        corners_twisted = sum(1 for orientation in co if orientation != 0)
        edges_moved = sum(1 for i, pos in enumerate(ep) if pos != i)
        edges_flipped = sum(1 for orientation in eo if orientation != 0)

        corner_cycles = find_permutation_cycles(cp)
        edge_cycles = find_permutation_cycles(ep)

        complexity_score, suggested_approach = compute_cubie_complexity(
            corners_moved,
            corners_twisted,
            edges_moved,
            edges_flipped,
        )

        corner_parity = compute_parity(cp)
        edge_parity = compute_parity(ep)
        parity_valid = corner_parity == edge_parity
        corner_cycle_analysis = analyze_cycles(corner_cycles)
        edge_cycle_analysis = analyze_cycles(edge_cycles)
        patterns = classify_pattern(cp, co, ep, eo)

    return ImpactData(
        cube=cube,

        # Facelet analysis
        facelets_state=cube.state,
        facelets_transformation_mask=mask,
        facelets_fixed_count=fixed_count,
        facelets_mobilized_count=mobilized_count,
        facelets_scrambled_percent=scrambled_percent,
        facelets_permutations=permutations,
        facelets_manhattan_distance=manhattan_distance,
        facelets_qtm_distance=qtm_distance,
        facelets_face_mobility=face_mobility,
        facelets_face_to_face_matrix=face_to_face_matrix,
        facelets_symmetry=symmetry,
        facelets_layer_analysis=layer_analysis,

        # Cubie analysis
        cubies_corner_permutation=cp,
        cubies_corner_orientation=co,
        cubies_edge_permutation=ep,
        cubies_edge_orientation=eo,
        cubies_corners_moved=corners_moved,
        cubies_corners_twisted=corners_twisted,
        cubies_edges_moved=edges_moved,
        cubies_edges_flipped=edges_flipped,
        cubies_corner_cycles=corner_cycles,
        cubies_edge_cycles=edge_cycles,
        cubies_complexity_score=complexity_score,
        cubies_suggested_approach=suggested_approach,
        cubies_corner_parity=corner_parity,
        cubies_edge_parity=edge_parity,
        cubies_parity_valid=parity_valid,
        cubies_corner_cycle_analysis=corner_cycle_analysis,
        cubies_edge_cycle_analysis=edge_cycle_analysis,
        cubies_patterns=patterns,
    )
