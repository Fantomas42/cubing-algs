# ruff: noqa: PLC0415
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

from cubing_algs.constants import EDGE_FACELET_MAP
from cubing_algs.constants import FACE_EDGES_INDEX
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.constants import QTM_OPPOSITE_EDGE_OFFSETS
from cubing_algs.constants import QTM_OPPOSITE_FACE_DOUBLE_PAIRS
from cubing_algs.constants import QTM_OPPOSITE_FACE_SIMPLE_PAIRS
from cubing_algs.constants import QTM_SAME_FACE_OPPOSITE_PAIRS
from cubing_algs.face_transforms import transform_position
from cubing_algs.facelets import cubies_to_facelets

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover
    from cubing_algs.vcube import VCube  # pragma: no cover


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
    facelets_manhattan_distance: DistanceMetrics
    facelets_qtm_distance: DistanceMetrics
    facelets_face_mobility: dict[str, int]
    facelets_face_to_face_matrix: dict[str, dict[str, int]]
    facelets_symmetry: dict[str, bool]
    facelets_layer_analysis: dict[str, int]

    # Cubie analysis (piece-level impact)
    cubies_corner_permutation: list[int]
    cubies_corner_orientation: list[int]
    cubies_edge_permutation: list[int]
    cubies_edge_orientation: list[int]
    cubies_corners_moved: int
    cubies_corners_twisted: int
    cubies_edges_moved: int
    cubies_edges_flipped: int
    cubies_corner_cycles: list[list[int]]
    cubies_edge_cycles: list[list[int]]
    cubies_complexity_score: int
    cubies_suggested_approach: str
    cubies_corner_parity: int
    cubies_edge_parity: int
    cubies_parity_valid: bool
    cubies_corner_cycle_analysis: CycleAnalysis
    cubies_edge_cycle_analysis: CycleAnalysis
    cubies_patterns: list[str]


def compute_face_impact(impact_mask: str, cube: 'VCube') -> dict[str, int]:
    """
    Calculate face impact from impact mask.
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
    )


def compute_within_face_manhattan_distance(
    orig: FaceletPosition,
    final: FaceletPosition,
) -> int:
    """Calculate Manhattan distance for positions on the same face."""
    return abs(orig.row - final.row) + abs(orig.col - final.col)


def compute_opposite_face_manhattan_distance(
    orig: FaceletPosition,
    final: FaceletPosition,
    cube: 'VCube',
) -> int:
    """
    Calculate Manhattan distance for positions on opposite faces.

    Distance = 2 * cube_size + within-face distance on destination
    The factor of 2 accounts for crossing through the cube's interior.
    """
    # Distance to cross from one face to the opposite face
    cross_face_distance = cube.size * 2

    # Add the within-face distance on the destination face
    within_face_distance = abs(final.row - orig.row) + abs(final.col - orig.col)

    return cross_face_distance + within_face_distance


def compute_adjacent_face_manhattan_distance(
    orig: FaceletPosition,
    final: FaceletPosition,
    cube: 'VCube',
) -> int:
    """
    Calculate Manhattan distance for positions on adjacent faces.

    Uses face transformation to determine the aligned position,
    then calculates the shortest path accounting for edge crossing.
    """
    # Transform original position to destination face coordinate system
    translated = parse_facelet_position(
        transform_position(
            final.face_name,
            orig.face_name,
            orig.face_position,
        ),
        cube,
    )

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
    """
    if original_pos == final_pos:
        return 0

    orig = parse_facelet_position(original_pos, cube)
    final = parse_facelet_position(final_pos, cube)

    # Case 1: Same face movements
    if orig.face_index == final.face_index:
        return compute_within_face_manhattan_distance(orig, final)

    # Case 2: Opposite faces
    if orig.face_name == OPPOSITE_FACES[final.face_name]:
        return compute_opposite_face_manhattan_distance(orig, final, cube)

    # Case 3: Adjacent faces
    return compute_adjacent_face_manhattan_distance(orig, final, cube)


def compute_within_face_qtm_distance(pos_pair: tuple[int, int]) -> int:
    """Calculate QTM distance for positions on the same face."""
    if pos_pair in QTM_SAME_FACE_OPPOSITE_PAIRS:
        return 2
    return 1


def compute_opposite_face_qtm_distance(pos: int,
                                     pos_pair: tuple[int, int]) -> int:
    """Calculate QTM distance for positions on opposite faces."""
    if pos == 4:
        return 4  # Center: slice move like M2 or S2

    if pos_pair in QTM_OPPOSITE_FACE_SIMPLE_PAIRS:
        return 2
    if pos_pair in QTM_OPPOSITE_FACE_DOUBLE_PAIRS:
        return 4
    return 3


def is_edge_in_same_piece(pos1: int, pos2: int) -> bool:
    """Check if two positions belong to the same edge piece."""
    for edge_map in EDGE_FACELET_MAP:
        if pos1 in edge_map and pos2 in edge_map:
            return True
    return False


def compute_adjacent_face_edge_qtm_distance(original_pos: int, final_pos: int,
                                          orig_face_pos: int,
                                          final_face_pos: int) -> int | None:
    """
    Calculate QTM distance for edge pieces on adjacent faces.

    Returns None if distance cannot be determined by edge analysis.
    """
    # Same edge piece requires 3 quarter turns (opposite sides of piece)
    if is_edge_in_same_piece(original_pos, final_pos):
        return 3

    # Check if opposite edge is same piece as final
    opposite_edge_pos = original_pos + QTM_OPPOSITE_EDGE_OFFSETS[orig_face_pos]
    if is_edge_in_same_piece(opposite_edge_pos, final_pos):
        return 2

    # Check symmetric case: opposite of final position
    opposite_final_pos = final_pos + QTM_OPPOSITE_EDGE_OFFSETS[final_face_pos]
    if is_edge_in_same_piece(opposite_final_pos, original_pos):
        return 2

    return None


def compute_adjacent_face_qtm_distance(
    original_pos: int,
    final_pos: int,
    orig: FaceletPosition,
    final: FaceletPosition,
    cube: 'VCube',
) -> int:
    """Calculate QTM distance for positions on adjacent faces."""
    if orig.face_position == 4:
        return 2  # Center: slice move like M or S

    # Special handling for edge pieces on adjacent faces
    if orig.face_position in FACE_EDGES_INDEX:
        edge_distance = compute_adjacent_face_edge_qtm_distance(
            original_pos,
            final_pos,
            orig.face_position,
            final.face_position,
        )
        if edge_distance is not None:
            return edge_distance

    # General adjacent face handling via transformation
    translated = parse_facelet_position(
        transform_position(
            final.face_name,
            orig.face_name,
            orig.face_position,
        ),
        cube,
    )

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
    """
    if original_pos == final_pos:
        return 0

    orig = parse_facelet_position(original_pos, cube)
    final = parse_facelet_position(final_pos, cube)

    # Case 1: Same face movements
    if orig.face_index == final.face_index:
        pos_pair = (orig.face_position, final.face_position)
        return compute_within_face_qtm_distance(pos_pair)

    # Case 2: Opposite faces
    if orig.face_name == OPPOSITE_FACES[final.face_name]:
        pos_pair = (orig.face_position, final.face_position)
        return compute_opposite_face_qtm_distance(orig.face_position, pos_pair)

    # Case 3: Adjacent faces
    return compute_adjacent_face_qtm_distance(
        original_pos, final_pos, orig, final, cube,
    )


def compute_distance_metrics(
    permutations: dict[int, int],
    cube: 'VCube',
    distance_fn: Callable[[int, int, 'VCube'], int],
) -> DistanceMetrics:
    """
    Compute distance metrics for a set of permutations.
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


def find_permutation_cycles(permutation: list[int]) -> list[list[int]]:
    """
    Find cycles in a permutation.

    A cycle is a sequence of positions where each position maps to the next,
    forming a closed loop. For example, [1, 2, 0] contains the cycle [0, 1, 2]
    meaning position 0 goes to 1, 1 goes to 2, and 2 goes back to 0.
    """
    visited = [False] * len(permutation)
    cycles = []

    for i in range(len(permutation)):
        if not visited[i] and permutation[i] != i:
            cycle = []
            current = i
            while not visited[current]:
                visited[current] = True
                cycle.append(current)
                current = permutation[current]
            if len(cycle) > 1:  # pragma: no branch
                cycles.append(cycle)

    return cycles


def compute_face_to_face_matrix(
        permutations: dict[int, int],
        cube: 'VCube',
) -> dict[str, dict[str, int]]:
    """
    Compute face-to-face movement matrix.

    Tracks how many facelets from each face end up on each other face.
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
    """
    # Extract face masks
    faces = []
    for i in range(6):
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
    """
    # Center of each face (position 4 in 3x3 grid)
    center_indices = {i * cube.face_size + 4 for i in range(6)}
    edge_indices = set()
    corner_indices = set()

    for face_idx in range(6):
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


def compute_parity(permutation: list[int]) -> int:
    """
    Compute the parity of a permutation.
    """
    parity = 0
    visited = [False] * len(permutation)

    for i in range(len(permutation)):
        if visited[i] or permutation[i] == i:
            continue

        cycle_length = 0
        current = i
        while not visited[current]:
            visited[current] = True
            current = permutation[current]
            cycle_length += 1

        # Cycles of even length contribute odd parity
        if cycle_length % 2 == 0:
            parity ^= 1

    return parity


def analyze_cycles(cycles: list[list[int]]) -> CycleAnalysis:
    """
    Analyze cycle structure in detail.
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


def classify_pattern(  # noqa: PLR0912, PLR0915, PLR0914
        cp: list[int], co: list[int],
        ep: list[int], eo: list[int],
) -> list[str]:
    """
    Comprehensive pattern classification for speedcubing.

    Identifies specific cube states and patterns useful for solving.
    """
    patterns = []

    # Basic state checks
    if (cp == list(range(8)) and co == [0] * 8 and
        ep == list(range(12)) and eo == [0] * 12):
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
    corners_permuted = cp == list(range(8))
    edges_permuted = ep == list(range(12))

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
    d_corners = [4, 5, 6, 7]  # DFR, DLF, DBL, DRB
    d_corners_solved = all(
        cp[i] == i and co[i] == 0
        for i in d_corners
    )
    if d_corners_solved:
        patterns.append('FIRST_LAYER_CORNERS_SOLVED')

    # Check if first layer edges are solved
    d_edges = [4, 5, 6, 7]  # DR, DF, DL, DB
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
    if d_corners_solved and d_edges_solved:
        # Check if F2L is complete (D layer + E slice edges)
        e_slice_edges = [8, 9, 10, 11]  # FR, FL, BL, BR
        f2l_edges_solved = all(
            ep[i] == i and eo[i] == 0
            for i in e_slice_edges
        )
        if f2l_edges_solved:
            patterns.append('F2L_COMPLETE')

    # Last layer patterns
    u_corners = [0, 1, 2, 3]  # URF, UFL, ULB, UBR
    u_edges = [0, 1, 2, 3]  # UR, UF, UL, UB

    u_corners_oriented = all(co[i] == 0 for i in u_corners)
    u_edges_oriented = all(eo[i] == 0 for i in u_edges)

    if u_corners_oriented and u_edges_oriented:
        patterns.append('LAST_LAYER_ORIENTED')

    # PLL patterns (all oriented, but permuted)
    if u_corners_oriented and u_edges_oriented:
        u_corners_permuted = all(cp[i] in u_corners for i in u_corners)
        u_edges_permuted = all(ep[i] in u_edges for i in u_edges)

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


def compute_impacts(algorithm: 'Algorithm') -> ImpactData:  # noqa: PLR0914
    """
    Compute comprehensive impact metrics for an algorithm.

    Analyzes both facelet-level (visual/spatial) and cubie-level (piece)
    impacts of the algorithm on the cube state.

    Returns:
        ImpactData: Namedtuple containing comprehensive impact metrics:

        Facelet metrics (visual/spatial impact):
            - facelets_transformation_mask: Binary mask of impacted facelets
            - facelets_fixed_count: Count of unmoved facelets
            - facelets_mobilized_count: Total number of moved facelets
            - facelets_scrambled_percent: Percent of moved facelets
            - facelets_permutations: Mapping of original to final positions
            - facelets_manhattan_distances: Manhattan distance each facelet
              traveled
            - facelets_manhattan_distance_mean: Average Manhattan facelet
              displacement
            - facelets_manhattan_distance_max: Maximum Manhattan facelet
              displacement
            - facelets_manhattan_distance_sum: Total Manhattan displacement
              across all facelets
            - facelets_qtm_distances: QTM distance each facelet traveled
            - facelets_qtm_distance_mean: Average QTM facelet displacement
            - facelets_qtm_distance_max: Maximum QTM facelet displacement
            - facelets_qtm_distance_sum: Total QTM displacement across all
              facelets
            - facelets_face_mobility: Impact breakdown by face

        Cubie metrics (piece-level impact):
            - cubies_corners_moved: Number of corners out of position
            - cubies_corners_twisted: Number of misoriented corners
            - cubies_edges_moved: Number of edges out of position
            - cubies_edges_flipped: Number of flipped edges
            - cubies_corner_cycles: Permutation cycles in corner arrangement
            - cubies_edge_cycles: Permutation cycles in edge arrangement
            - cubies_complexity_score: Overall solving complexity estimate
            - cubies_suggested_approach: Recommended solving strategy
    """
    from cubing_algs.transform.degrip import degrip_full_moves
    from cubing_algs.transform.rotation import remove_ending_rotations
    from cubing_algs.transform.slice import unslice_rotation_moves
    from cubing_algs.transform.wide import unwide_rotation_moves
    from cubing_algs.vcube import VCube

    if algorithm.has_rotations:
        algorithm = algorithm.transform(
            unwide_rotation_moves,
            unslice_rotation_moves,
            degrip_full_moves,
            remove_ending_rotations,
        )

    cube = VCube()
    cube.rotate(algorithm)

    # Create unique state with each facelet having a unique character
    state_unique = ''.join(
        [
            chr(ord('A') + i)
            for i in range(cube.face_size * cube.face_number)
        ],
    )
    state_unique_moved = cubies_to_facelets(*cube.to_cubies, state_unique)

    mask = ''.join(
        '0' if f1 == f2 else '1'
        for f1, f2 in zip(state_unique, state_unique_moved, strict=True)
    )

    permutations = {}
    for original_pos in range(len(state_unique)):
        final_pos = state_unique_moved.find(
            state_unique[original_pos],
        )

        if final_pos != original_pos:
            permutations[original_pos] = final_pos

    # Compute distance metrics using helper function
    manhattan_distance = compute_distance_metrics(
        permutations, cube, compute_manhattan_distance,
    )
    qtm_distance = compute_distance_metrics(
        permutations, cube, compute_qtm_distance,
    )

    fixed_count = mask.count('0')
    mobilized_count = mask.count('1')
    # Center facelets should not move
    scrambled_percent = mobilized_count / (len(state_unique) - cube.face_number)

    face_mobility = compute_face_impact(mask, cube)

    face_to_face_matrix = compute_face_to_face_matrix(permutations, cube)
    symmetry = detect_symmetry(mask, cube)
    layer_analysis = analyze_layers(permutations, cube)

    # Cubie analysis
    cp, co, ep, eo, _so = cube.to_cubies

    # Count corners moved and twisted
    corners_moved = sum(1 for i, pos in enumerate(cp) if pos != i)
    corners_twisted = sum(1 for orientation in co if orientation != 0)

    # Count edges moved and flipped
    edges_moved = sum(1 for i, pos in enumerate(ep) if pos != i)
    edges_flipped = sum(1 for orientation in eo if orientation != 0)

    # Find permutation cycles
    corner_cycles = find_permutation_cycles(cp)
    edge_cycles = find_permutation_cycles(ep)

    # Compute complexity and approach
    complexity_score, suggested_approach = compute_cubie_complexity(
        corners_moved,
        corners_twisted,
        edges_moved,
        edges_flipped,
    )

    # New cubie analyses
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
