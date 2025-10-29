import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.impacts import DistanceMetrics
from cubing_algs.impacts import ImpactData
from cubing_algs.impacts import analyze_cycles
from cubing_algs.impacts import analyze_layers
from cubing_algs.impacts import classify_pattern
from cubing_algs.impacts import compute_cubie_complexity
from cubing_algs.impacts import compute_face_impact
from cubing_algs.impacts import compute_face_to_face_matrix
from cubing_algs.impacts import compute_impacts
from cubing_algs.impacts import compute_manhattan_distance
from cubing_algs.impacts import compute_parity
from cubing_algs.impacts import compute_qtm_distance
from cubing_algs.impacts import detect_symmetry
from cubing_algs.impacts import find_permutation_cycles
from cubing_algs.vcube import VCube


class TestImpactData(unittest.TestCase):
    """Test the ImpactData NamedTuple structure and properties."""

    def test_impact_data_structure(self) -> None:
        """Test ImpactData can be created with all required fields."""
        cube = VCube()
        impact_data = ImpactData(
            cube=cube,
            facelets_state=cube.state,
            facelets_transformation_mask='0' * 54,
            facelets_fixed_count=54,
            facelets_mobilized_count=0,
            facelets_scrambled_percent=0.0,
            facelets_permutations={},
            facelets_manhattan_distance=DistanceMetrics(
                distances={},
                mean=0.0,
                max=0,
                sum=0,
            ),
            facelets_qtm_distance=DistanceMetrics(
                distances={},
                mean=0.0,
                max=0,
                sum=0,
            ),
            facelets_face_mobility={
                'U': 0, 'R': 0, 'F': 0,
                'D': 0, 'L': 0, 'B': 0,
            },
            facelets_face_to_face_matrix={},
            facelets_symmetry={},
            facelets_layer_analysis={},
            cubies_corner_permutation=list(range(8)),
            cubies_corner_orientation=[0] * 8,
            cubies_edge_permutation=list(range(12)),
            cubies_edge_orientation=[0] * 12,
            cubies_corners_moved=0,
            cubies_corners_twisted=0,
            cubies_edges_moved=0,
            cubies_edges_flipped=0,
            cubies_corner_cycles=[],
            cubies_edge_cycles=[],
            cubies_complexity_score=0,
            cubies_suggested_approach='Solved state',
            cubies_corner_parity=0,
            cubies_edge_parity=0,
            cubies_parity_valid=True,
            cubies_corner_cycle_analysis={
                'cycle_count': 0,
                'cycle_lengths': [],
                'min_cycle_length': 0,
                'max_cycle_length': 0,
                'total_pieces_in_cycles': 0,
                'two_cycles': 0,
                'three_cycles': 0,
                'four_plus_cycles': 0,
            },
            cubies_edge_cycle_analysis={
                'cycle_count': 0,
                'cycle_lengths': [],
                'min_cycle_length': 0,
                'max_cycle_length': 0,
                'total_pieces_in_cycles': 0,
                'two_cycles': 0,
                'three_cycles': 0,
                'four_plus_cycles': 0,
            },
            cubies_patterns=['SOLVED'],
        )

        self.assertIsInstance(impact_data.cube, VCube)
        self.assertEqual(impact_data.facelets_transformation_mask, '0' * 54)
        self.assertEqual(impact_data.facelets_fixed_count, 54)
        self.assertEqual(impact_data.facelets_mobilized_count, 0)
        self.assertEqual(impact_data.facelets_scrambled_percent, 0.0)
        self.assertEqual(impact_data.facelets_permutations, {})
        self.assertIsInstance(
            impact_data.facelets_manhattan_distance,
            DistanceMetrics,
        )
        self.assertEqual(impact_data.facelets_manhattan_distance.distances, {})
        self.assertEqual(impact_data.facelets_manhattan_distance.mean, 0.0)
        self.assertEqual(impact_data.facelets_manhattan_distance.max, 0)
        self.assertEqual(impact_data.facelets_manhattan_distance.sum, 0)
        self.assertIsInstance(
            impact_data.facelets_qtm_distance,
            DistanceMetrics,
        )
        self.assertEqual(impact_data.facelets_qtm_distance.distances, {})
        self.assertEqual(impact_data.facelets_qtm_distance.mean, 0.0)
        self.assertEqual(impact_data.facelets_qtm_distance.max, 0)
        self.assertEqual(impact_data.facelets_qtm_distance.sum, 0)
        self.assertIsInstance(impact_data.facelets_face_mobility, dict)
        self.assertEqual(impact_data.cubies_corners_moved, 0)
        self.assertEqual(impact_data.cubies_corners_twisted, 0)
        self.assertEqual(impact_data.cubies_edges_moved, 0)
        self.assertEqual(impact_data.cubies_edges_flipped, 0)

    def test_impact_data_field_access(self) -> None:
        """Test individual field access on ImpactData."""
        cube = VCube()
        face_mobility = {'U': 1, 'R': 2, 'F': 3, 'D': 4, 'L': 5, 'B': 6}

        impact_data = ImpactData(
            cube=cube,
            facelets_state=cube.state,
            facelets_transformation_mask='1' * 20 + '0' * 34,
            facelets_fixed_count=34,
            facelets_mobilized_count=20,
            facelets_scrambled_percent=20.0 / 54.0,
            facelets_permutations={0: 10, 1: 11},
            facelets_manhattan_distance=DistanceMetrics(
                distances={0: 2, 1: 3},
                mean=2.5,
                max=3,
                sum=5,
            ),
            facelets_qtm_distance=DistanceMetrics(
                distances={0: 1, 1: 2},
                mean=1.5,
                max=2,
                sum=3,
            ),
            facelets_face_mobility=face_mobility,
            facelets_face_to_face_matrix={'U': {'R': 1, 'F': 2}},
            facelets_symmetry={'all_faces_same': False},
            facelets_layer_analysis={
                'centers_moved': 1,
                'edges_moved': 2,
                'corners_moved': 3,
            },
            cubies_corner_permutation=[0, 1, 2, 3, 4, 5, 6, 7],
            cubies_corner_orientation=[0, 1, 0, 0, 0, 0, 0, 0],
            cubies_edge_permutation=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            cubies_edge_orientation=[0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            cubies_corners_moved=2,
            cubies_corners_twisted=1,
            cubies_edges_moved=3,
            cubies_edges_flipped=1,
            cubies_corner_cycles=[[0, 1]],
            cubies_edge_cycles=[[0, 1, 2]],
            cubies_complexity_score=7,
            cubies_suggested_approach=(
                'Simple case - direct algorithms may be sufficient'
            ),
            cubies_corner_parity=0,
            cubies_edge_parity=0,
            cubies_parity_valid=True,
            cubies_corner_cycle_analysis={
                'cycle_count': 1,
                'cycle_lengths': [2],
                'min_cycle_length': 2,
                'max_cycle_length': 2,
                'total_pieces_in_cycles': 2,
                'two_cycles': 1,
                'three_cycles': 0,
                'four_plus_cycles': 0,
            },
            cubies_edge_cycle_analysis={
                'cycle_count': 1,
                'cycle_lengths': [3],
                'min_cycle_length': 3,
                'max_cycle_length': 3,
                'total_pieces_in_cycles': 3,
                'two_cycles': 0,
                'three_cycles': 1,
                'four_plus_cycles': 0,
            },
            cubies_patterns=['EDGES_ORIENTED', 'CORNERS_PERMUTED'],
        )

        # Test all fields are accessible
        self.assertEqual(len(impact_data.facelets_transformation_mask), 54)
        self.assertEqual(impact_data.facelets_fixed_count, 34)
        self.assertEqual(impact_data.facelets_mobilized_count, 20)
        self.assertAlmostEqual(
            impact_data.facelets_scrambled_percent,
            20.0 / 54.0,
        )
        self.assertEqual(impact_data.facelets_permutations[0], 10)
        self.assertEqual(
            impact_data.facelets_manhattan_distance.distances[1],
            3,
        )
        self.assertEqual(impact_data.facelets_manhattan_distance.mean, 2.5)
        self.assertEqual(impact_data.facelets_manhattan_distance.max, 3)
        self.assertEqual(impact_data.facelets_manhattan_distance.sum, 5)
        self.assertEqual(impact_data.facelets_qtm_distance.distances[1], 2)
        self.assertEqual(impact_data.facelets_qtm_distance.mean, 1.5)
        self.assertEqual(impact_data.facelets_qtm_distance.max, 2)
        self.assertEqual(impact_data.facelets_qtm_distance.sum, 3)
        self.assertEqual(impact_data.facelets_face_mobility['U'], 1)
        self.assertEqual(impact_data.cubies_corners_moved, 2)
        self.assertEqual(impact_data.cubies_complexity_score, 7)


class TestComputeFaceImpact(unittest.TestCase):
    """Test the compute_face_impact function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_all_zeros_mask(self) -> None:
        """Test compute_face_impact with all zeros (no movement)."""
        mask = '0' * 54
        result = compute_face_impact(mask, self.cube)

        expected = dict.fromkeys(FACE_ORDER, 0)
        self.assertEqual(result, expected)

    def test_all_ones_mask(self) -> None:
        """Test compute_face_impact with all ones (complete movement)."""
        mask = '1' * 54
        result = compute_face_impact(mask, self.cube)

        expected = dict.fromkeys(FACE_ORDER, 9)
        self.assertEqual(result, expected)

    def test_single_face_impact(self) -> None:
        """Test compute_face_impact with only one face affected."""
        # Only U face (first 9 positions) affected
        mask = '1' * 9 + '0' * 45
        result = compute_face_impact(mask, self.cube)

        expected = {'U': 9, 'R': 0, 'F': 0, 'D': 0, 'L': 0, 'B': 0}
        self.assertEqual(result, expected)

    def test_partial_face_impact(self) -> None:
        """Test compute_face_impact with partial face movements."""
        # 3 facelets from U, 5 from R, 1 from F
        mask = '111000000' + '111110000' + '100000000' + '0' * 27
        result = compute_face_impact(mask, self.cube)

        expected = {'U': 3, 'R': 5, 'F': 1, 'D': 0, 'L': 0, 'B': 0}
        self.assertEqual(result, expected)

    def test_alternating_pattern(self) -> None:
        """Test compute_face_impact with alternating pattern."""
        # Alternating 0 and 1 across all faces
        mask = ''.join('01' * 27)  # 54 characters total
        result = compute_face_impact(mask, self.cube)

        # Each face should have 4 or 5 ones (depending on the face position)
        for _face, count in result.items():
            self.assertIn(count, [4, 5])

        # Total should be 27
        self.assertEqual(sum(result.values()), 27)

    def test_empty_mask(self) -> None:
        """Test compute_face_impact with empty mask."""
        mask = ''
        result = compute_face_impact(mask, self.cube)

        expected = dict.fromkeys(FACE_ORDER, 0)
        self.assertEqual(result, expected)

    def test_face_order_consistency(self) -> None:
        """Test that face impact follows FACE_ORDER consistently."""
        mask = '1' * 54
        result = compute_face_impact(mask, self.cube)

        # Should have entries for all faces in FACE_ORDER
        self.assertEqual(list(result.keys()), FACE_ORDER)


class TestComputeManhattanDistance(unittest.TestCase):
    """Test the compute_manhattan_distance function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_same_position_distance(self) -> None:
        """Test distance between same position is zero."""
        distance = compute_manhattan_distance(0, 0, self.cube)
        self.assertEqual(distance, 0)

        distance = compute_manhattan_distance(26, 26, self.cube)
        self.assertEqual(distance, 0)

        distance = compute_manhattan_distance(53, 53, self.cube)
        self.assertEqual(distance, 0)

    def test_same_face_manhattan_distance(self) -> None:
        """Test Manhattan distance within the same face."""
        # U face positions (0-8): positions are laid out as:
        # 0 1 2
        # 3 4 5
        # 6 7 8

        # Adjacent positions (row or column neighbors)
        # Same row
        distance = compute_manhattan_distance(0, 1, self.cube)
        self.assertEqual(distance, 1)

        # Same column
        distance = compute_manhattan_distance(1, 4, self.cube)
        self.assertEqual(distance, 1)

        # Adjacent
        distance = compute_manhattan_distance(4, 5, self.cube)
        self.assertEqual(distance, 1)

        # Center diagonal
        distance = compute_manhattan_distance(0, 4, self.cube)
        self.assertEqual(distance, 2)

        # Opposite corners
        distance = compute_manhattan_distance(0, 8, self.cube)
        self.assertEqual(distance, 4)

    def test_different_face_distance(self) -> None:
        """Test distance between different faces."""
        cube_size = self.cube.size

        # From U face (position 0) to R face (position 9)
        # Should be cube_size + manhattan distance
        distance = compute_manhattan_distance(0, 9, self.cube)
        self.assertEqual(distance, cube_size + 0)  # Same relative position

        # From U face corner to R face corner
        # U top-right to R top-right
        distance = compute_manhattan_distance(2, 11, self.cube)
        self.assertEqual(distance, cube_size + 0)

    def test_opposite_face_distance(self) -> None:
        """Test distance between opposite faces."""
        cube_size = self.cube.size

        # U and D are opposite faces
        u_center = 4  # U face center
        d_center = 31  # D face center (27 + 4)

        distance = compute_manhattan_distance(u_center, d_center, self.cube)
        # Should be cube_size * 2 (opposite factor) + manhattan distance
        self.assertEqual(distance, cube_size * 2 + 0)

    def test_face_boundaries(self) -> None:
        """Test distance calculations at face boundaries."""
        # Test first position of each face
        for i in range(6):
            face_start = i * 9
            distance = compute_manhattan_distance(
                face_start, face_start, self.cube,
            )
            self.assertEqual(distance, 0)

        # Test last position of each face
        for i in range(6):
            face_end = i * 9 + 8
            distance = compute_manhattan_distance(face_end, face_end, self.cube)
            self.assertEqual(distance, 0)

    def test_edge_cases_positions(self) -> None:
        """Test edge cases with extreme positions."""
        # First position to last position
        distance = compute_manhattan_distance(0, 53, self.cube)
        self.assertEqual(distance, 7)

        # Cross face movement
        distance = compute_manhattan_distance(8, 9, self.cube)  # U to R face
        self.assertEqual(distance, 7)

    def test_distance_symmetry_property(self) -> None:
        """Test distance calculation handles position ordering correctly."""
        # Distance should be based on relative positions, not order
        distance1 = compute_manhattan_distance(0, 10, self.cube)
        distance2 = compute_manhattan_distance(10, 0, self.cube)

        # Note: This is not necessarily symmetric due to the algorithm design
        # but both should be positive when positions differ
        self.assertEqual(distance1, 4)
        self.assertEqual(distance2, 4)


class TestComputeQtmDistance(unittest.TestCase):
    """Test the compute_qtm_distance function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_same_position_returns_zero(self) -> None:
        """Test that distance from a position to itself is zero."""
        # Test corner positions
        distance = compute_qtm_distance(0, 0, self.cube)
        self.assertEqual(distance, 0)

        distance = compute_qtm_distance(8, 8, self.cube)
        self.assertEqual(distance, 0)

        # Test edge positions
        distance = compute_qtm_distance(1, 1, self.cube)
        self.assertEqual(distance, 0)

        distance = compute_qtm_distance(7, 7, self.cube)
        self.assertEqual(distance, 0)

        # Test across different faces
        distance = compute_qtm_distance(26, 26, self.cube)
        self.assertEqual(distance, 0)

        distance = compute_qtm_distance(53, 53, self.cube)
        self.assertEqual(distance, 0)

    def test_same_face_opposite_corners_return_two(self) -> None:
        """
        Test that opposite corner positions on same face return 2.

        Opposite corner pairs: (0, 8), (8, 0), (2, 6), (6, 2)
        """
        # U face (positions 0-8)
        distance = compute_qtm_distance(0, 8, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(8, 0, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(2, 6, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(6, 2, self.cube)
        self.assertEqual(distance, 2)

    def test_same_face_opposite_edges_return_two(self) -> None:
        """
        Test that opposite edge positions on same face return 2.

        Opposite edge pairs: (1, 7), (7, 1), (3, 5), (5, 3)
        """
        # U face (positions 0-8)
        distance = compute_qtm_distance(1, 7, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(7, 1, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(3, 5, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(5, 3, self.cube)
        self.assertEqual(distance, 2)

    def test_same_face_adjacent_corners_return_one(self) -> None:
        """
        Test that adjacent corner positions on same face return 1.

        Corner positions on a face: 0, 2, 6, 8
        Adjacent pairs: (0,2), (2,8), (8,6), (6,0)
        """
        # U face adjacent corners
        distance = compute_qtm_distance(0, 2, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(2, 0, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(2, 8, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(8, 2, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(8, 6, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(6, 8, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(6, 0, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(0, 6, self.cube)
        self.assertEqual(distance, 1)

    def test_same_face_adjacent_edges_return_one(self) -> None:
        """
        Test that adjacent edge positions on same face return 1.

        Edge positions on a face: 1, 3, 5, 7
        Adjacent pairs: (1,3), (3,7), (7,5), (5,1)
        """
        # U face adjacent edges
        distance = compute_qtm_distance(1, 3, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(3, 1, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(3, 7, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(7, 3, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(7, 5, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(5, 7, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(5, 1, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(1, 5, self.cube)
        self.assertEqual(distance, 1)

    def test_same_face_opposite_corners_on_r_face(self) -> None:
        """Test opposite corners on R face (positions 9-17)."""
        # R face starts at position 9
        distance = compute_qtm_distance(9, 17, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(17, 9, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(11, 15, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(15, 11, self.cube)
        self.assertEqual(distance, 2)

    def test_same_face_opposite_edges_on_f_face(self) -> None:
        """Test opposite edges on F face (positions 18-26)."""
        # F face starts at position 18
        distance = compute_qtm_distance(19, 25, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(25, 19, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(21, 23, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(23, 21, self.cube)
        self.assertEqual(distance, 2)

    def test_same_face_adjacent_corners_on_d_face(self) -> None:
        """Test adjacent corners on D face (positions 27-35)."""
        # D face starts at position 27
        distance = compute_qtm_distance(27, 29, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(29, 35, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(35, 33, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(33, 27, self.cube)
        self.assertEqual(distance, 1)

    def test_same_face_adjacent_edges_on_l_face(self) -> None:
        """Test adjacent edges on L face (positions 36-44)."""
        # L face starts at position 36
        distance = compute_qtm_distance(37, 39, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(39, 43, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(43, 41, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(41, 37, self.cube)
        self.assertEqual(distance, 1)

    def test_same_face_opposite_corners_on_b_face(self) -> None:
        """Test opposite corners on B face (positions 45-53)."""
        # B face starts at position 45
        distance = compute_qtm_distance(45, 53, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(53, 45, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(47, 51, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(51, 47, self.cube)
        self.assertEqual(distance, 2)

    def test_cross_face_corner_to_corner(self) -> None:
        """
        Test cross-face corner movements.
        """
        # Corner on U face to corner on R face
        distance = compute_qtm_distance(0, 9, self.cube)
        self.assertEqual(distance, 2)

        # Corner on U face to corner on D face (opposite faces)
        distance = compute_qtm_distance(0, 27, self.cube)
        self.assertEqual(distance, 2)

        # Corner on F face to corner on B face (opposite faces)
        distance = compute_qtm_distance(18, 45, self.cube)
        self.assertEqual(distance, 2)

    def test_cross_face_edge_to_edge(self) -> None:
        """
        Test cross-face edge movements.
        """
        # Edge on U face to edge on R face
        distance = compute_qtm_distance(1, 10, self.cube)
        self.assertEqual(distance, 2)

        # Edge on U face to edge on D face (opposite faces)
        distance = compute_qtm_distance(1, 28, self.cube)
        self.assertEqual(distance, 2)

        # Edge on L face to edge on R face (opposite faces)
        distance = compute_qtm_distance(37, 10, self.cube)
        self.assertEqual(distance, 2)

    def test_cross_face_adjacent_faces(self) -> None:
        """
        Test cross-face movements between adjacent faces.

        Adjacent faces share an edge (e.g., U-R, U-F, R-F).
        """
        # U to R (adjacent faces)
        distance = compute_qtm_distance(2, 9, self.cube)
        self.assertEqual(distance, 3)

        # U to F (adjacent faces)
        distance = compute_qtm_distance(6, 20, self.cube)
        self.assertEqual(distance, 3)

        # R to F (adjacent faces)
        distance = compute_qtm_distance(17, 18, self.cube)
        self.assertEqual(distance, 3)

    def test_cross_face_opposite_faces(self) -> None:
        """
        Test cross-face movements between opposite faces return 0.

        Opposite face pairs: U-D, R-L, F-B
        """
        # U to D
        distance = compute_qtm_distance(0, 35, self.cube)
        self.assertEqual(distance, 4)

        # R to L
        distance = compute_qtm_distance(9, 44, self.cube)
        self.assertEqual(distance, 4)

        # F to B
        distance = compute_qtm_distance(26, 45, self.cube)
        self.assertEqual(distance, 4)

    def test_boundary_positions_to_themselves(self) -> None:
        """Test boundary positions (first and last) to themselves."""
        # First corner position
        distance = compute_qtm_distance(0, 0, self.cube)
        self.assertEqual(distance, 0)

        # Last corner position
        distance = compute_qtm_distance(53, 53, self.cube)
        self.assertEqual(distance, 0)

        # First edge position on U face
        distance = compute_qtm_distance(1, 1, self.cube)
        self.assertEqual(distance, 0)

        # Last edge position on B face
        distance = compute_qtm_distance(52, 52, self.cube)
        self.assertEqual(distance, 0)

    def test_first_to_last_position_cross_face(self) -> None:
        """Test distance from first cube position to last cube position."""
        # Position 0 (U face top-left corner) to position 53
        # (B face bottom-right corner)
        distance = compute_qtm_distance(0, 53, self.cube)
        self.assertEqual(distance, 1)

    def test_all_faces_have_same_logic(self) -> None:
        """
        Test that the same-face logic works consistently across all faces.

        Verify opposite corners return 2 on each face.
        """
        # Test opposite corners on each face
        face_starts = [0, 9, 18, 27, 36, 45]  # U, R, F, D, L, B

        for face_start in face_starts:
            # Opposite corners (0,8) and (2,6)
            distance = compute_qtm_distance(
                face_start + 0, face_start + 8, self.cube,
            )
            self.assertEqual(distance, 2)

            distance = compute_qtm_distance(
                face_start + 2, face_start + 6, self.cube,
            )
            self.assertEqual(distance, 2)

    def test_all_faces_adjacent_edges_logic(self) -> None:
        """
        Test that adjacent edge logic works consistently across all faces.

        Verify adjacent edges return 1 on each face.
        """
        # Test adjacent edges on each face
        face_starts = [0, 9, 18, 27, 36, 45]  # U, R, F, D, L, B

        for face_start in face_starts:
            # Adjacent edges (1,3), (3,7), (5,7), (1,5)
            distance = compute_qtm_distance(
                face_start + 1, face_start + 3, self.cube,
            )
            self.assertEqual(distance, 1)

            distance = compute_qtm_distance(
                face_start + 3, face_start + 7, self.cube,
            )
            self.assertEqual(distance, 1)

            distance = compute_qtm_distance(
                face_start + 5, face_start + 7, self.cube,
            )
            self.assertEqual(distance, 1)

            distance = compute_qtm_distance(
                face_start + 1, face_start + 5, self.cube,
            )
            self.assertEqual(distance, 1)

    def test_all_faces_opposite_edges_logic(self) -> None:
        """
        Test that opposite edge logic works consistently across all faces.

        Verify opposite edges return 2 on each face.
        """
        # Test opposite edges on each face
        face_starts = [0, 9, 18, 27, 36, 45]  # U, R, F, D, L, B

        for face_start in face_starts:
            # Opposite edges (1,7) and (3,5)
            distance = compute_qtm_distance(
                face_start + 1, face_start + 7, self.cube,
            )
            self.assertEqual(distance, 2)

            distance = compute_qtm_distance(
                face_start + 3, face_start + 5, self.cube,
            )
            self.assertEqual(distance, 2)

    def test_corner_movements_across_multiple_faces(self) -> None:
        """
        Test corner to corner movements work correctly across different faces.
        """
        # Same face corner movements
        distance = compute_qtm_distance(0, 2, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(9, 17, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(27, 33, self.cube)
        self.assertEqual(distance, 1)

        # Cross right face
        distance = compute_qtm_distance(0, 11, self.cube)
        self.assertEqual(distance, 1)

    def test_edge_movements_across_multiple_faces(self) -> None:
        """Test edge to edge movements work correctly across different faces."""
        # Same face edge movements
        distance = compute_qtm_distance(1, 5, self.cube)
        self.assertEqual(distance, 1)

        distance = compute_qtm_distance(19, 25, self.cube)
        self.assertEqual(distance, 2)

        distance = compute_qtm_distance(37, 43, self.cube)
        self.assertEqual(distance, 2)

        # Cross front face
        distance = compute_qtm_distance(1, 19, self.cube)
        self.assertEqual(distance, 2)

    def test_qtm_distance_same_face_all_positions(self) -> None:
        """
        Test QTM distance for all 81 position pairs on the same face.

        Face layout (3x3 grid):
        0 1 2    (corners: 0,2,6,8  edges: 1,3,5,7  center: 4)
        3 4 5
        6 7 8

        Expected distances based on geometry:
        - Same position: 0 QTM
        - Center to center: 0 QTM
        - Adjacent positions (1 step around face): 1 QTM
        - Opposite positions (diagonal across face): 2 QTM

        Geometric reasoning:
        - Adjacent corners (e.g., 0→2, 2→8, 8→6, 6→0): 1 QTM (90° rotation)
        - Opposite corners (e.g., 0→8, 2→6): 2 QTM (180° rotation)
        - Adjacent edges (e.g., 1→3, 3→7, 7→5, 5→1): 1 QTM (90° rotation)
        - Opposite edges (e.g., 1→7, 3→5): 2 QTM (180° rotation)
        """
        # Test on U face (positions 0-8)
        test_cases = [
            # Same position (distance = 0)
            (0, 0, 0), (1, 1, 0), (2, 2, 0), (3, 3, 0), (4, 4, 0),
            (5, 5, 0), (6, 6, 0), (7, 7, 0), (8, 8, 0),

            # Corner to corner movements
            # Adjacent corners (1 QTM - 90° rotation)
            (0, 2, 1), (2, 0, 1),  # top-left to top-right
            (2, 8, 1), (8, 2, 1),  # top-right to bottom-right
            (8, 6, 1), (6, 8, 1),  # bottom-right to bottom-left
            (6, 0, 1), (0, 6, 1),  # bottom-left to top-left
            # Opposite corners (2 QTM - 180° rotation)
            (0, 8, 2), (8, 0, 2),  # top-left to bottom-right (diagonal)
            (2, 6, 2), (6, 2, 2),  # top-right to bottom-left (diagonal)

            # Edge to edge movements
            # Adjacent edges (1 QTM - 90° rotation)
            (1, 3, 1), (3, 1, 1),  # top to left
            (3, 7, 1), (7, 3, 1),  # left to bottom
            (7, 5, 1), (5, 7, 1),  # bottom to right
            (5, 1, 1), (1, 5, 1),  # right to top
            # Opposite edges (2 QTM - 180° rotation)
            (1, 7, 2), (7, 1, 2),  # top to bottom
            (3, 5, 2), (5, 3, 2),  # left to right

            # Center to center (same position)
            (4, 4, 0),

            # Corner to edge movements (1 QTM - adjacent positions)
            (0, 1, 1), (1, 0, 1),  # top-left corner to top edge
            (0, 3, 1), (3, 0, 1),  # top-left corner to left edge
            (2, 1, 1), (1, 2, 1),  # top-right corner to top edge
            (2, 5, 1), (5, 2, 1),  # top-right corner to right edge
            (6, 3, 1), (3, 6, 1),  # bottom-left corner to left edge
            (6, 7, 1), (7, 6, 1),  # bottom-left corner to bottom edge
            (8, 5, 1), (5, 8, 1),  # bottom-right corner to right edge
            (8, 7, 1), (7, 8, 1),  # bottom-right corner to bottom edge
        ]

        for orig_pos, final_pos, expected_distance in test_cases:
            with self.subTest(orig=orig_pos, final=final_pos):
                distance = compute_qtm_distance(orig_pos, final_pos, self.cube)
                self.assertEqual(
                    distance, expected_distance,
                    f'Distance from { orig_pos } to { final_pos } should be '
                    f'{ expected_distance } QTM but got { distance }',
                )

    def test_qtm_distance_opposite_faces_corners_comprehensive(self) -> None:
        """
        Test QTM distance for all corner-to-corner pairs between opposite faces.

        Opposite face pairs: U-D (0-27), R-L (9-36), F-B (18-45)
        Corner positions: 0, 2, 6, 8 (relative to face start)

        Geometric reasoning for opposite faces:
        - Aligned corners (same relative position): 2 QTM
          Example: U corner 0 → D corner 0 (both top-left in their orientation)
        - 90° rotated: 3 QTM
          Example: U corner 0 → D corner 2 (requires rotation + flip)
        - 180° rotated (fully opposite): 4 QTM
          Example: U corner 0 → D corner 8 (diagonal opposite)

        Cube physics constraint: Corners can only move to corner positions.
        """
        # U face to D face (opposite faces)
        # U corners: 0, 2, 6, 8  |  D corners: 27, 29, 33, 35
        test_cases = [
            # Aligned positions (2 QTM)
            (0, 27, 2), (27, 0, 2),  # top-left to top-left
            (2, 29, 2), (29, 2, 2),  # top-right to top-right
            (6, 33, 2), (33, 6, 2),  # bottom-left to bottom-left
            (8, 35, 2), (35, 8, 2),  # bottom-right to bottom-right

            # 90° rotated positions (3 QTM)
            (0, 29, 3), (29, 0, 3),  # top-left to top-right
            (0, 33, 3), (33, 0, 3),  # top-left to bottom-left
            (2, 27, 3), (27, 2, 3),  # top-right to top-left
            (2, 35, 3), (35, 2, 3),  # top-right to bottom-right
            (6, 27, 3), (27, 6, 3),  # bottom-left to top-left
            (6, 35, 3), (35, 6, 3),  # bottom-left to bottom-right
            (8, 29, 3), (29, 8, 3),  # bottom-right to top-right
            (8, 33, 3), (33, 8, 3),  # bottom-right to bottom-left

            # 180° rotated positions (4 QTM - diagonal opposite)
            (0, 35, 4), (35, 0, 4),  # top-left to bottom-right
            (2, 33, 4), (33, 2, 4),  # top-right to bottom-left
            (6, 29, 4), (29, 6, 4),  # bottom-left to top-right
            (8, 27, 4), (27, 8, 4),  # bottom-right to top-left
        ]

        # R face to L face (opposite faces)
        # R corners: 9, 11, 15, 17  |  L corners: 36, 38, 42, 44
        test_cases.extend([
            # Aligned positions (2 QTM)
            (9, 36, 2), (36, 9, 2),
            (11, 38, 2), (38, 11, 2),
            (15, 42, 2), (42, 15, 2),
            (17, 44, 2), (44, 17, 2),

            # 90° rotated positions (3 QTM)
            (9, 38, 3), (38, 9, 3),
            (9, 42, 3), (42, 9, 3),
            (11, 36, 3), (36, 11, 3),
            (11, 44, 3), (44, 11, 3),
            (15, 36, 3), (36, 15, 3),
            (15, 44, 3), (44, 15, 3),
            (17, 38, 3), (38, 17, 3),
            (17, 42, 3), (42, 17, 3),

            # 180° rotated positions (4 QTM)
            (9, 44, 4), (44, 9, 4),
            (11, 42, 4), (42, 11, 4),
            (15, 38, 4), (38, 15, 4),
            (17, 36, 4), (36, 17, 4),
        ])

        # F face to B face (opposite faces)
        # F corners: 18, 20, 24, 26  |  B corners: 45, 47, 51, 53
        test_cases.extend([
            # Aligned positions (2 QTM)
            (18, 45, 2), (45, 18, 2),
            (20, 47, 2), (47, 20, 2),
            (24, 51, 2), (51, 24, 2),
            (26, 53, 2), (53, 26, 2),

            # 90° rotated positions (3 QTM)
            (18, 47, 3), (47, 18, 3),
            (18, 51, 3), (51, 18, 3),
            (20, 45, 3), (45, 20, 3),
            (20, 53, 3), (53, 20, 3),
            (24, 45, 3), (45, 24, 3),
            (24, 53, 3), (53, 24, 3),
            (26, 47, 3), (47, 26, 3),
            (26, 51, 3), (51, 26, 3),

            # 180° rotated positions (4 QTM)
            (18, 53, 4), (53, 18, 4),
            (20, 51, 4), (51, 20, 4),
            (24, 47, 4), (47, 24, 4),
            (26, 45, 4), (45, 26, 4),
        ])

        for orig_pos, final_pos, expected_distance in test_cases:
            with self.subTest(orig=orig_pos, final=final_pos):
                distance = compute_qtm_distance(orig_pos, final_pos, self.cube)
                self.assertEqual(
                    distance, expected_distance,
                    f'Corner distance from { orig_pos } to { final_pos } '
                    f'should be { expected_distance } QTM but got { distance }',
                )

    def test_qtm_distance_opposite_faces_edges_comprehensive(self) -> None:
        """
        Test QTM distance for all edge-to-edge pairs between opposite faces.

        Opposite face pairs: U-D (0-27), R-L (9-36), F-B (18-45)
        Edge positions: 1, 3, 5, 7 (relative to face start)

        Geometric reasoning for opposite faces:
        - Aligned edges (same relative position): 2 QTM
          Example: U edge 1 → D edge 1 (both top edge in their orientation)
        - 90° rotated: 3 QTM
          Example: U edge 1 → D edge 3 (requires rotation + flip)
        - 180° rotated (fully opposite): 4 QTM
          Example: U edge 1 → D edge 7 (opposite edge)

        Cube physics constraint: Edges can only move to edge positions.
        """
        # U face to D face (opposite faces)
        # U edges: 1, 3, 5, 7  |  D edges: 28, 30, 32, 34
        test_cases = [
            # Aligned positions (2 QTM)
            (1, 28, 2), (28, 1, 2),  # top to top
            (7, 34, 2), (34, 7, 2),  # bottom to bottom
            (3, 32, 2), (32, 3, 2),  # left to right
            (5, 30, 2), (30, 5, 2),  # right to left

            # 90° rotated positions (3 QTM)
            (1, 30, 3), (30, 1, 3),  # top to left
            (1, 32, 3), (32, 1, 3),  # top to right
            (3, 28, 3), (28, 3, 3),  # left to top
            (3, 34, 3), (34, 3, 3),  # left to bottom
            (5, 28, 3), (28, 5, 3),  # right to top
            (5, 34, 3), (34, 5, 3),  # right to bottom
            (7, 30, 3), (30, 7, 3),  # bottom to left
            (7, 32, 3), (32, 7, 3),  # bottom to right

            # 180° rotated positions (4 QTM - opposite edge)
            (1, 34, 4), (34, 1, 4),  # top to bottom
            (7, 28, 4), (28, 7, 4),  # bottom to top
            (3, 30, 4), (30, 3, 4),  # left to left
            (5, 32, 4), (32, 5, 4),  # right to right
        ]

        # R face to L face (opposite faces)
        # R edges: 10, 12, 14, 16  |  L edges: 37, 39, 41, 43
        test_cases.extend([
            # Aligned positions (2 QTM)
            (10, 37, 2), (37, 10, 2),
            (16, 43, 2), (43, 16, 2),
            (12, 41, 2), (41, 12, 2),
            (14, 39, 2), (39, 14, 2),

            # 90° rotated positions (3 QTM)
            (10, 39, 3), (39, 10, 3),
            (10, 41, 3), (41, 10, 3),
            (12, 37, 3), (37, 12, 3),
            (12, 43, 3), (43, 12, 3),
            (14, 37, 3), (37, 14, 3),
            (14, 43, 3), (43, 14, 3),
            (16, 39, 3), (39, 16, 3),
            (16, 41, 3), (41, 16, 3),

            # 180° rotated positions (4 QTM)
            (10, 43, 4), (43, 10, 4),
            (16, 37, 4), (37, 16, 4),
            (12, 39, 4), (39, 12, 4),
            (14, 41, 4), (41, 14, 4),
        ])

        # F face to B face (opposite faces)
        # F edges: 19, 21, 23, 25  |  B edges: 46, 48, 50, 52
        test_cases.extend([
            # Aligned positions (2 QTM)
            (19, 46, 2), (46, 19, 2),
            (25, 52, 2), (52, 25, 2),
            (21, 50, 2), (50, 21, 2),
            (23, 48, 2), (48, 23, 2),

            # 90° rotated positions (3 QTM)
            (19, 48, 3), (48, 19, 3),
            (19, 50, 3), (50, 19, 3),
            (21, 46, 3), (46, 21, 3),
            (21, 52, 3), (52, 21, 3),
            (23, 46, 3), (46, 23, 3),
            (23, 52, 3), (52, 23, 3),
            (25, 48, 3), (48, 25, 3),
            (25, 50, 3), (50, 25, 3),

            # 180° rotated positions (4 QTM)
            (19, 52, 4), (52, 19, 4),
            (25, 46, 4), (46, 25, 4),
            (21, 48, 4), (48, 21, 4),
            (23, 50, 4), (50, 23, 4),
        ])

        for orig_pos, final_pos, expected_distance in test_cases:
            with self.subTest(orig=orig_pos, final=final_pos):
                distance = compute_qtm_distance(orig_pos, final_pos, self.cube)
                self.assertEqual(
                    distance, expected_distance,
                    f'Edge distance from { orig_pos } to { final_pos } '
                    f'should be { expected_distance } QTM but got { distance }',
                )

    def test_qtm_distance_opposite_faces_center(self) -> None:
        """
        Test QTM distance for center-to-center between opposite faces.

        Center position: 4 (relative to face start)

        Geometric reasoning:
        - Center to center on opposite faces: 4 QTM
          (flip the cube along that axis, with M2, S2 or E2)

        Note: Centers don't have rotation orientation like corners/edges,
        so there's only one distance value (4 QTM) for opposite face centers.
        """
        test_cases = [
            # U face (4) to D face (31) - opposite faces
            (4, 31, 4), (31, 4, 4),

            # R face (13) to L face (40) - opposite faces
            (13, 40, 4), (40, 13, 4),

            # F face (22) to B face (49) - opposite faces
            (22, 49, 4), (49, 22, 4),
        ]

        for orig_pos, final_pos, expected_distance in test_cases:
            with self.subTest(orig=orig_pos, final=final_pos):
                distance = compute_qtm_distance(orig_pos, final_pos, self.cube)
                self.assertEqual(
                    distance, expected_distance,
                    f'Center distance from { orig_pos } to { final_pos } '
                    f'should be { expected_distance } QTM but got { distance }',
                )

    def test_qtm_distance_center_to_center_same_face(self) -> None:
        """
        Test center to center on the same face (always 0 QTM).

        Each face has only one center position, so center to center
        on the same face is the same position.
        """
        # Test center to center on each face
        face_centers = [4, 13, 22, 31, 40, 49]  # U, R, F, D, L, B

        for center_pos in face_centers:
            with self.subTest(face_center=center_pos):
                distance = compute_qtm_distance(
                    center_pos, center_pos, self.cube,
                )
                self.assertEqual(
                    distance, 0,
                    f'Center to itself should be 0 QTM but got { distance }',
                )

    def test_qtm_distance_all_faces_consistency(self) -> None:
        """
        Test that QTM distance logic is consistent across all faces.

        Verifies that the same relative position movements produce the same
        distances regardless of which face they're on.
        """
        face_starts = [0, 9, 18, 27, 36, 45]  # U, R, F, D, L, B

        for face_start in face_starts:
            with self.subTest(face_start=face_start):
                # Test a few representative patterns
                # Adjacent corners: 1 QTM
                self.assertEqual(
                    compute_qtm_distance(
                        face_start + 0,
                        face_start + 2, self.cube,
                    ), 1,
                )
                # Opposite corners: 2 QTM
                self.assertEqual(
                    compute_qtm_distance(
                        face_start + 0,
                        face_start + 8,
                        self.cube,
                    ), 2,
                )
                # Adjacent edges: 1 QTM
                self.assertEqual(
                    compute_qtm_distance(
                        face_start + 1,
                        face_start + 3,
                        self.cube,
                    ), 1,
                )
                # Opposite edges: 2 QTM
                self.assertEqual(
                    compute_qtm_distance(
                        face_start + 1,
                        face_start + 7,
                        self.cube,
                    ), 2,
                )

    def test_qtm_distance_adjacent_faces_corners_comprehensive(self) -> None:
        """
        Test QTM distance for all corner-to-corner pairs between adjacent faces.

        Adjacent face pairs: U-R, U-F, U-L, U-B, R-F, R-B, F-L, F-D, L-B, L-D, B-D, D-R

        Geometric reasoning for adjacent faces:
        - Corners on adjacent faces can share a physical corner piece
        - Shared corner (on the edge between faces): varies based on alignment
        - Non-shared corners: varies based on position

        Corner positions: 0, 2, 6, 8 (relative to face start)
        """
        test_cases = []

        # U face (0-8) to R face (9-17) - adjacent faces (share right edge)
        # U corners: 0, 2, 6, 8  |  R corners: 9, 11, 15, 17
        # U corner 2 and R corner 9 share physical corner (top-right U, top-left R)
        # U corner 8 and R corner 15 share physical corner (bottom-right U, bottom-left R)
        test_cases.extend([
            # Shared corners (should be shortest distance)
            (2, 9, 1), (9, 2, 1),    # top-right U to top-left R (shared)
            (8, 15, 1), (15, 8, 1),  # bottom-right U to bottom-left R (shared)

            # Adjacent to shared (one rotation away)
            (0, 9, 2), (9, 0, 2),    # top-left U to top-left R
            (2, 11, 2), (11, 2, 2),  # top-right U to top-right R
            (6, 15, 2), (15, 6, 2),  # bottom-left U to bottom-left R
            (8, 17, 2), (17, 8, 2),  # bottom-right U to bottom-right R

            # Diagonal relationships
            (0, 11, 3), (11, 0, 3),  # top-left U to top-right R
            (0, 15, 3), (15, 0, 3),  # top-left U to bottom-left R
            (0, 17, 3), (17, 0, 3),  # top-left U to bottom-right R
            (2, 15, 3), (15, 2, 3),  # top-right U to bottom-left R
            (2, 17, 3), (17, 2, 3),  # top-right U to bottom-right R
            (6, 9, 3), (9, 6, 3),    # bottom-left U to top-left R
            (6, 11, 3), (11, 6, 3),  # bottom-left U to top-right R
            (6, 17, 3), (17, 6, 3),  # bottom-left U to bottom-right R
            (8, 9, 3), (9, 8, 3),    # bottom-right U to top-left R
            (8, 11, 3), (11, 8, 3),  # bottom-right U to top-right R
        ])

        # U face (0-8) to F face (18-26) - adjacent faces (share front edge)
        # U corners: 0, 2, 6, 8  |  F corners: 18, 20, 24, 26
        # U corner 6 and F corner 18 share physical corner
        # U corner 8 and F corner 20 share physical corner
        test_cases.extend([
            # Shared corners
            (6, 18, 1), (18, 6, 1),  # bottom-left U to top-left F (shared)
            (8, 20, 1), (20, 8, 1),  # bottom-right U to top-right F (shared)

            # Adjacent to shared
            (0, 18, 2), (18, 0, 2),  # top-left U to top-left F
            (2, 20, 2), (20, 2, 2),  # top-right U to top-right F
            (6, 20, 2), (20, 6, 2),  # bottom-left U to top-right F
            (8, 18, 2), (18, 8, 2),  # bottom-right U to top-left F

            # Other relationships
            (0, 20, 3), (20, 0, 3),  # top-left U to top-right F
            (0, 24, 3), (24, 0, 3),  # top-left U to bottom-left F
            (0, 26, 3), (26, 0, 3),  # top-left U to bottom-right F
            (2, 18, 3), (18, 2, 3),  # top-right U to top-left F
            (2, 24, 3), (24, 2, 3),  # top-right U to bottom-left F
            (2, 26, 3), (26, 2, 3),  # top-right U to bottom-right F
            (6, 24, 3), (24, 6, 3),  # bottom-left U to bottom-left F
            (6, 26, 3), (26, 6, 3),  # bottom-left U to bottom-right F
            (8, 24, 3), (24, 8, 3),  # bottom-right U to bottom-left F
            (8, 26, 3), (26, 8, 3),  # bottom-right U to bottom-right F
        ])

        # U face (0-8) to L face (36-44) - adjacent faces (share left edge)
        # U corners: 0, 2, 6, 8  |  L corners: 36, 38, 42, 44
        # U corner 0 and L corner 38 share physical corner
        # U corner 6 and L corner 44 share physical corner
        test_cases.extend([
            # Shared corners
            (0, 38, 1), (38, 0, 1),  # top-left U to top-right L (shared)
            (6, 44, 1), (44, 6, 1),  # bottom-left U to bottom-right L (shared)

            # Adjacent to shared
            (0, 36, 2), (36, 0, 2),  # top-left U to top-left L
            (0, 42, 2), (42, 0, 2),  # top-left U to bottom-left L
            (0, 44, 2), (44, 0, 2),  # top-left U to bottom-right L
            (2, 38, 2), (38, 2, 2),  # top-right U to top-right L
            (6, 36, 2), (36, 6, 2),  # bottom-left U to top-left L
            (6, 38, 2), (38, 6, 2),  # bottom-left U to top-right L
            (6, 42, 2), (42, 6, 2),  # bottom-left U to bottom-left L
            (8, 44, 2), (44, 8, 2),  # bottom-right U to bottom-right L

            # Other relationships
            (2, 36, 3), (36, 2, 3),  # top-right U to top-left L
            (2, 42, 3), (42, 2, 3),  # top-right U to bottom-left L
            (2, 44, 3), (44, 2, 3),  # top-right U to bottom-right L
            (8, 36, 3), (36, 8, 3),  # bottom-right U to top-left L
            (8, 38, 3), (38, 8, 3),  # bottom-right U to top-right L
            (8, 42, 3), (42, 8, 3),  # bottom-right U to bottom-left L
        ])

        # U face (0-8) to B face (45-53) - adjacent faces (share back edge)
        # U corners: 0, 2, 6, 8  |  B corners: 45, 47, 51, 53
        # U corner 0 and B corner 47 share physical corner
        # U corner 2 and B corner 45 share physical corner
        test_cases.extend([
            # Shared corners
            (0, 47, 1), (47, 0, 1),  # top-left U to top-right B (shared)
            (2, 45, 1), (45, 2, 1),  # top-right U to top-left B (shared)

            # Adjacent to shared
            (0, 45, 2), (45, 0, 2),  # top-left U to top-left B
            (0, 51, 2), (51, 0, 2),  # top-left U to bottom-left B
            (0, 53, 2), (53, 0, 2),  # top-left U to bottom-right B
            (2, 47, 2), (47, 2, 2),  # top-right U to top-right B
            (2, 51, 2), (51, 2, 2),  # top-right U to bottom-left B
            (2, 53, 2), (53, 2, 2),  # top-right U to bottom-right B

            # Other relationships
            (6, 45, 3), (45, 6, 3),  # bottom-left U to top-left B
            (6, 47, 3), (47, 6, 3),  # bottom-left U to top-right B
            (6, 51, 3), (51, 6, 3),  # bottom-left U to bottom-left B
            (6, 53, 3), (53, 6, 3),  # bottom-left U to bottom-right B
            (8, 45, 3), (45, 8, 3),  # bottom-right U to top-left B
            (8, 47, 3), (47, 8, 3),  # bottom-right U to top-right B
            (8, 51, 3), (51, 8, 3),  # bottom-right U to bottom-left B
            (8, 53, 3), (53, 8, 3),  # bottom-right U to bottom-right B
        ])

        # R face (9-17) to F face (18-26) - adjacent faces
        # R corners: 9, 11, 15, 17  |  F corners: 18, 20, 24, 26
        # R corner 17 and F corner 20 share physical corner
        # R corner 15 and F corner 26 share physical corner
        test_cases.extend([
            # Shared corners
            (17, 20, 1), (20, 17, 1),  # bottom-right R to top-right F (shared)
            (15, 26, 1), (26, 15, 1),  # bottom-left R to bottom-right F (shared)

            # Adjacent and other relationships
            (9, 18, 2), (18, 9, 2),
            (9, 20, 2), (20, 9, 2),
            (9, 24, 3), (24, 9, 3),
            (9, 26, 3), (26, 9, 3),
            (11, 18, 3), (18, 11, 3),
            (11, 20, 3), (20, 11, 3),
            (11, 24, 3), (24, 11, 3),
            (11, 26, 3), (26, 11, 3),
            (15, 18, 3), (18, 15, 3),
            (15, 20, 3), (20, 15, 3),
            (15, 24, 2), (24, 15, 2),
            (17, 18, 3), (18, 17, 3),
            (17, 24, 3), (24, 17, 3),
            (17, 26, 2), (26, 17, 2),
        ])

        # R face (9-17) to B face (45-53) - adjacent faces
        # R corners: 9, 11, 15, 17  |  B corners: 45, 47, 51, 53
        test_cases.extend([
            # Shared corners
            (11, 45, 1), (45, 11, 1),  # top-right R to top-left B (shared)
            (17, 51, 1), (51, 17, 1),  # bottom-right R to bottom-left B (shared)

            # Adjacent and other relationships
            (9, 45, 2), (45, 9, 2),
            (9, 47, 2), (47, 9, 2),
            (9, 51, 3), (51, 9, 3),
            (9, 53, 3), (53, 9, 3),
            (11, 47, 2), (47, 11, 2),
            (11, 51, 2), (51, 11, 2),
            (11, 53, 3), (53, 11, 3),
            (15, 45, 3), (45, 15, 3),
            (15, 47, 3), (47, 15, 3),
            (15, 51, 2), (51, 15, 2),
            (15, 53, 2), (53, 15, 2),
            (17, 45, 3), (45, 17, 3),
            (17, 47, 3), (47, 17, 3),
            (17, 53, 2), (53, 17, 2),
        ])

        # F face (18-26) to L face (36-44) - adjacent faces
        # F corners: 18, 20, 24, 26  |  L corners: 36, 38, 42, 44
        test_cases.extend([
            # Shared corners
            (18, 42, 1), (42, 18, 1),  # top-left F to bottom-left L (shared)
            (24, 44, 1), (44, 24, 1),  # bottom-left F to bottom-right L (shared)

            # Adjacent and other relationships
            (18, 36, 3), (36, 18, 3),
            (18, 38, 2), (38, 18, 2),
            (18, 44, 2), (44, 18, 2),
            (20, 36, 3), (36, 20, 3),
            (20, 38, 3), (38, 20, 3),
            (20, 42, 3), (42, 20, 3),
            (20, 44, 3), (44, 20, 3),
            (24, 36, 3), (36, 24, 3),
            (24, 38, 3), (38, 24, 3),
            (24, 42, 2), (42, 24, 2),
            (26, 36, 3), (36, 26, 3),
            (26, 38, 3), (38, 26, 3),
            (26, 42, 3), (42, 26, 3),
            (26, 44, 2), (44, 26, 2),
        ])

        # D face (27-35) to R face (9-17) - adjacent faces
        # D corners: 27, 29, 33, 35  |  R corners: 9, 11, 15, 17
        test_cases.extend([
            # Shared corners
            (29, 15, 1), (15, 29, 1),  # top-right D to bottom-left R (shared)
            (35, 17, 1), (17, 35, 1),  # bottom-right D to bottom-right R (shared)

            # Adjacent and other relationships
            (27, 9, 3), (9, 27, 3),
            (27, 11, 3), (11, 27, 3),
            (27, 15, 2), (15, 27, 2),
            (27, 17, 2), (17, 27, 2),
            (29, 9, 3), (9, 29, 3),
            (29, 11, 3), (11, 29, 3),
            (29, 17, 2), (17, 29, 2),
            (33, 9, 2), (9, 33, 2),
            (33, 11, 3), (11, 33, 3),
            (33, 15, 3), (15, 33, 3),
            (33, 17, 3), (17, 33, 3),
            (35, 9, 2), (9, 35, 2),
            (35, 11, 3), (11, 35, 3),
            (35, 15, 2), (15, 35, 2),
        ])

        # D face (27-35) to F face (18-26) - adjacent faces
        # D corners: 27, 29, 33, 35  |  F corners: 18, 20, 24, 26
        test_cases.extend([
            # Shared corners
            (27, 24, 1), (24, 27, 1),  # top-left D to bottom-left F (shared)
            (29, 26, 1), (26, 29, 1),  # top-right D to bottom-right F (shared)

            # Adjacent and other relationships
            (27, 18, 3), (18, 27, 3),
            (27, 20, 3), (20, 27, 3),
            (27, 26, 2), (26, 27, 2),
            (29, 18, 3), (18, 29, 3),
            (29, 20, 3), (20, 29, 3),
            (29, 24, 2), (24, 29, 2),
            (33, 18, 2), (18, 33, 2),
            (33, 20, 3), (20, 33, 3),
            (33, 24, 3), (24, 33, 3),
            (33, 26, 3), (26, 33, 3),
            (35, 18, 3), (18, 35, 3),
            (35, 20, 2), (20, 35, 2),
            (35, 24, 3), (24, 35, 3),
            (35, 26, 3), (26, 35, 3),
        ])

        # D face (27-35) to L face (36-44) - adjacent faces
        # D corners: 27, 29, 33, 35  |  L corners: 36, 38, 42, 44
        test_cases.extend([
            # Shared corners
            (27, 42, 1), (42, 27, 1),  # top-left D to bottom-left L (shared)
            (33, 36, 1), (36, 33, 1),  # bottom-left D to top-left L (shared)

            # Adjacent and other relationships
            (27, 36, 2), (36, 27, 2),
            (27, 38, 3), (38, 27, 3),
            (27, 44, 3), (44, 27, 3),
            (29, 36, 3), (36, 29, 3),
            (29, 38, 3), (38, 29, 3),
            (29, 42, 3), (42, 29, 3),
            (29, 44, 3), (44, 29, 3),
            (33, 38, 2), (38, 33, 2),
            (33, 42, 2), (42, 33, 2),
            (33, 44, 3), (44, 33, 3),
            (35, 36, 3), (36, 35, 3),
            (35, 38, 3), (38, 35, 3),
            (35, 42, 3), (42, 35, 3),
            (35, 44, 3), (44, 35, 3),
        ])

        # D face (27-35) to B face (45-53) - adjacent faces
        # D corners: 27, 29, 33, 35  |  B corners: 45, 47, 51, 53
        test_cases.extend([
            # Shared corners
            (33, 51, 1), (51, 33, 1),  # bottom-left D to bottom-left B (shared)
            (35, 53, 1), (53, 35, 1),  # bottom-right D to bottom-right B (shared)

            # Adjacent and other relationships
            (27, 45, 3), (45, 27, 3),
            (27, 47, 3), (47, 27, 3),
            (27, 51, 2), (51, 27, 2),
            (27, 53, 2), (53, 27, 2),
            (29, 45, 3), (45, 29, 3),
            (29, 47, 3), (47, 29, 3),
            (29, 51, 2), (51, 29, 2),
            (29, 53, 2), (53, 29, 2),
            (33, 45, 2), (45, 33, 2),
            (33, 47, 3), (47, 33, 3),
            (33, 53, 2), (53, 33, 2),
            (35, 45, 3), (45, 35, 3),
            (35, 47, 2), (47, 35, 2),
            (35, 51, 2), (51, 35, 2),
        ])

        # L face (36-44) to B face (45-53) - adjacent faces
        # L corners: 36, 38, 42, 44  |  B corners: 45, 47, 51, 53
        test_cases.extend([
            # Shared corners
            (36, 47, 1), (47, 36, 1),  # top-left L to top-right B (shared)
            (42, 53, 1), (53, 42, 1),  # bottom-left L to bottom-right B (shared)

            # Adjacent and other relationships
            (36, 45, 2), (45, 36, 2),
            (36, 51, 3), (51, 36, 3),
            (36, 53, 2), (53, 36, 2),
            (38, 45, 2), (45, 38, 2),
            (38, 47, 2), (47, 38, 2),
            (38, 51, 3), (51, 38, 3),
            (38, 53, 3), (53, 38, 3),
            (42, 45, 3), (45, 42, 3),
            (42, 47, 2), (47, 42, 2),
            (42, 51, 2), (51, 42, 2),
            (44, 45, 3), (45, 44, 3),
            (44, 47, 3), (47, 44, 3),
            (44, 51, 2), (51, 44, 2),
            (44, 53, 2), (53, 44, 2),
        ])

        for orig_pos, final_pos, expected_distance in test_cases:
            with self.subTest(orig=orig_pos, final=final_pos):
                distance = compute_qtm_distance(orig_pos, final_pos, self.cube)
                self.assertEqual(
                    distance, expected_distance,
                    f'Corner distance from {orig_pos} to {final_pos} '
                    f'should be {expected_distance} QTM but got {distance}',
                )

    def test_qtm_distance_adjacent_faces_edges_comprehensive(self) -> None:
        """
        Test QTM distance for all edge-to-edge pairs between adjacent faces.

        Edge positions: 1, 3, 5, 7 (relative to face start)

        Geometric reasoning for adjacent faces:
        - Edges on adjacent faces can share a physical edge piece
        - Shared edges should have distance 1
        - Non-shared edges vary based on position
        """
        test_cases = []

        # U face (0-8) to R face (9-17) - adjacent faces
        # U edges: 1, 3, 5, 7  |  R edges: 10, 12, 14, 16
        # U edge 5 and R edge 12 share physical edge (right U, left R)
        test_cases.extend([
            (1, 10, 2), (10, 1, 2),  # top U to top R
            (1, 12, 3), (12, 1, 3),  # top U to left R
            (1, 14, 1), (14, 1, 1),  # top U to right R
            (1, 16, 2), (16, 1, 2),  # top U to bottom R

            (3, 10, 2), (10, 3, 2),  # left U to top R
            (3, 12, 2), (12, 3, 2),  # left U to left R
            (3, 14, 2), (14, 3, 2),  # left U to right R
            (3, 16, 3), (16, 3, 3),  # left U to bottom R

            (5, 10, 3), (10, 5, 3),  # right U to top R
            (5, 12, 2), (12, 5, 2),  # right U to left R
            (5, 14, 2), (14, 5, 2),  # right U to right R
            (5, 16, 2), (16, 5, 2),  # right U to bottom R

            (7, 10, 2), (10, 7, 2),  # bottom U to top R
            (7, 12, 1), (12, 7, 1),  # bottom U to left R
            (7, 14, 3), (14, 7, 3),  # bottom U to right R
            (7, 16, 2), (16, 7, 2),  # bottom U to bottom R
        ])

        # U face (0-8) to F face (18-26) - adjacent faces
        # U edges: 1, 3, 5, 7  |  F edges: 19, 21, 23, 25
        # U edge 7 and F edge 19 share physical edge (bottom U, top F)
        test_cases.extend([
            (1, 19, 2), (19, 1, 2),  # top U to top F
            (1, 21, 2), (21, 1, 2),  # top U to left F
            (1, 23, 2), (23, 1, 2),  # top U to right F
            (1, 25, 3), (25, 1, 3),  # top U to bottom F

            (3, 19, 2), (19, 3, 2),  # left U to top F
            (3, 21, 1), (21, 3, 1),  # left U to left F
            (3, 23, 3), (23, 3, 3),  # left U to right F
            (3, 25, 2), (25, 3, 2),  # left U to bottom F

            (5, 19, 2), (19, 5, 2),  # right U to top F
            (5, 21, 3), (21, 5, 3),  # right U to left F
            (5, 23, 1), (23, 5, 1),  # right U to right F
            (5, 25, 2), (25, 5, 2),  # right U to bottom F

            (7, 19, 3), (19, 7, 3),  # bottom U to top
            (7, 21, 2), (21, 7, 2),  # bottom U to left F
            (7, 23, 2), (23, 7, 2),  # bottom U to right F
            (7, 25, 2), (25, 7, 2),  # bottom U to bottom F
        ])

        # U face (0-8) to L face (36-44) - adjacent faces
        # U edges: 1, 3, 5, 7  |  L edges: 37, 39, 41, 43
        # U edge 3 and L edge 39 share physical edge (left U, top L)
        test_cases.extend([
            (1, 37, 2), (37, 1, 2),  # top U to left L
            (1, 39, 1), (39, 1, 1),  # top U to top L
            (1, 41, 3), (41, 1, 3),  # top U to right L
            (1, 43, 2), (43, 1, 2),  # top U to bottom L

            (3, 37, 3), (37, 3, 3),  # left U to left L
            (3, 39, 2), (39, 3, 2),  # left U to top L
            (3, 41, 2), (41, 3, 2),  # left U to right L
            (3, 43, 2), (43, 3, 2),  # left U to bottom L

            (5, 37, 2), (37, 5, 2),  # right U to left L
            (5, 39, 2), (39, 5, 2),  # right U to top L
            (5, 41, 2), (41, 5, 2),  # right U to right L
            (5, 43, 3), (43, 5, 3),  # right U to bottom L

            (7, 37, 2), (37, 7, 2),  # bottom U to left L
            (7, 39, 3), (39, 7, 3),  # bottom U to top L
            (7, 41, 1), (41, 7, 1),  # bottom U to right L
            (7, 43, 2), (43, 7, 2),  # bottom U to bottom L
        ])

        # U face (0-8) to B face (45-53) - adjacent faces
        # U edges: 1, 3, 5, 7  |  B edges: 46, 48, 50, 52
        # U edge 1 and B edge 46 share physical edge (top U, top B)
        test_cases.extend([
            (1, 46, 3), (46, 1, 3),  # top U to top B
            (1, 48, 2), (48, 1, 2),  # top U to left B
            (1, 50, 2), (50, 1, 2),  # top U to right B
            (1, 52, 2), (52, 1, 2),  # top U to bottom B

            (3, 46, 2), (46, 3, 2),  # left U to top B
            (3, 48, 3), (48, 3, 3),  # left U to left B
            (3, 50, 1), (50, 3, 1),  # left U to right B
            (3, 52, 2), (52, 3, 2),  # left U to bottom B

            (5, 46, 2), (46, 5, 2),  # right U to top B
            (5, 48, 1), (48, 5, 1),  # right U to left B
            (5, 50, 3), (50, 5, 3),  # right U to right B
            (5, 52, 2), (52, 5, 2),  # right U to bottom B

            (7, 46, 2), (46, 7, 2),  # bottom U to top B
            (7, 48, 2), (48, 7, 2),  # bottom U to left B
            (7, 50, 2), (50, 7, 2),  # bottom U to right B
            (7, 52, 3), (52, 7, 3),  # bottom U to bottom B
        ])

        # R face (9-17) to F face (18-26) - adjacent faces
        # R edges: 10, 12, 14, 16  |  F edges: 19, 21, 23, 25
        # R edge 14 and F edge 23 share physical edge (right R, right F)
        test_cases.extend([
            (10, 19, 1), (19, 10, 1),
            (10, 21, 2), (21, 10, 2),
            (10, 23, 2), (23, 10, 2),
            (10, 25, 3), (25, 10, 3),

            (12, 19, 2), (19, 12, 2),
            (12, 21, 2), (21, 12, 2),
            (12, 23, 3), (23, 12, 3),
            (12, 25, 2), (25, 12, 2),

            (14, 19, 2), (19, 14, 2),
            (14, 21, 3), (21, 14, 3),
            (14, 23, 2), (23, 14, 2),
            (14, 25, 2), (25, 14, 2),

            (16, 19, 3), (19, 16, 3),
            (16, 21, 2), (21, 16, 2),
            (16, 23, 2), (23, 16, 2),
            (16, 25, 1), (25, 16, 1),
        ])

        # R face (9-17) to B face (45-53) - adjacent faces
        # R edges: 10, 12, 14, 16  |  B edges: 46, 48, 50, 52
        # R edge 10 and B edge 48 share physical edge
        test_cases.extend([
            (10, 46, 1), (46, 10, 1),
            (10, 48, 2), (48, 10, 2),
            (10, 50, 2), (50, 10, 2),
            (10, 52, 3), (52, 10, 3),

            (12, 46, 2), (46, 12, 2),
            (12, 48, 2), (48, 12, 2),
            (12, 50, 3), (50, 12, 3),
            (12, 52, 2), (52, 12, 2),

            (14, 46, 2), (46, 14, 2),
            (14, 48, 3), (48, 14, 3),
            (14, 50, 2), (50, 14, 2),
            (14, 52, 2), (52, 14, 2),

            (16, 46, 3), (46, 16, 3),
            (16, 48, 2), (48, 16, 2),
            (16, 50, 2), (50, 16, 2),
            (16, 52, 1), (52, 16, 1),
        ])

        # F face (18-26) to L face (36-44) - adjacent faces
        # F edges: 19, 21, 23, 25  |  L edges: 37, 39, 41, 43
        # F edge 21 and L edge 41 share physical edge
        test_cases.extend([
            (19, 37, 1), (37, 19, 1),
            (19, 39, 2), (39, 19, 2),
            (19, 41, 2), (41, 19, 2),
            (19, 43, 3), (43, 19, 3),

            (21, 37, 2), (37, 21, 2),
            (21, 39, 2), (39, 21, 2),
            (21, 41, 3), (41, 21, 3),
            (21, 43, 2), (43, 21, 2),

            (23, 37, 2), (37, 23, 2),
            (23, 39, 3), (39, 23, 3),
            (23, 41, 2), (41, 23, 2),
            (23, 43, 2), (43, 23, 2),

            (25, 37, 3), (37, 25, 3),
            (25, 39, 2), (39, 25, 2),
            (25, 41, 2), (41, 25, 2),
            (25, 43, 1), (43, 25, 1),
        ])

        # D face (27-35) to R face (9-17) - adjacent faces
        # D edges: 28, 30, 32, 34  |  R edges: 10, 12, 14, 16
        # D edge 32 and R edge 16 share physical edge
        test_cases.extend([
            (28, 10, 2), (10, 28, 2),
            (28, 12, 1), (12, 28, 1),
            (28, 14, 3), (14, 28, 3),
            (28, 16, 2), (16, 28, 2),

            (30, 10, 3), (10, 30, 3),
            (30, 12, 2), (12, 30, 2),
            (30, 14, 2), (14, 30, 2),
            (30, 16, 2), (16, 30, 2),

            (32, 10, 2), (10, 32, 2),
            (32, 12, 2), (12, 32, 2),
            (32, 14, 2), (14, 32, 2),
            (32, 16, 3), (16, 32, 3),

            (34, 10, 2), (10, 34, 2),
            (34, 12, 3), (12, 34, 3),
            (34, 14, 1), (14, 34, 1),
            (34, 16, 2), (16, 34, 2),
        ])

        # D face (27-35) to F face (18-26) - adjacent faces
        # D edges: 28, 30, 32, 34  |  F edges: 19, 21, 23, 25
        # D edge 28 and F edge 25 share physical edge
        test_cases.extend([
            (28, 19, 2), (19, 28, 2),
            (28, 21, 2), (21, 28, 2),
            (28, 23, 2), (23, 28, 2),
            (28, 25, 3), (25, 28, 3),

            (30, 19, 2), (19, 30, 2),
            (30, 21, 1), (21, 30, 1),
            (30, 23, 3), (23, 30, 3),
            (30, 25, 2), (25, 30, 2),

            (32, 19, 2), (19, 32, 2),
            (32, 21, 3), (21, 32, 3),
            (32, 23, 1), (23, 32, 1),
            (32, 25, 2), (25, 32, 2),

            (34, 19, 3), (19, 34, 3),
            (34, 21, 2), (21, 34, 2),
            (34, 23, 2), (23, 34, 2),
            (34, 25, 2), (25, 34, 2),
        ])

        # D face (27-35) to L face (36-44) - adjacent faces
        # D edges: 28, 30, 32, 34  |  L edges: 37, 39, 41, 43
        # D edge 30 and L edge 43 share physical edge
        test_cases.extend([
            (28, 37, 2), (37, 28, 2),
            (28, 39, 3), (39, 28, 3),
            (28, 41, 1), (41, 28, 1),
            (28, 43, 2), (43, 28, 2),

            (30, 37, 2), (37, 30, 2),
            (30, 39, 2), (39, 30, 2),
            (30, 41, 2), (41, 30, 2),
            (30, 43, 3), (43, 30, 3),

            (32, 37, 3), (37, 32, 3),
            (32, 39, 2), (39, 32, 2),
            (32, 41, 2), (41, 32, 2),
            (32, 43, 2), (43, 32, 2),

            (34, 37, 2), (37, 34, 2),
            (34, 39, 1), (39, 34, 1),
            (34, 41, 3), (41, 34, 3),
            (34, 43, 2), (43, 34, 2),
        ])

        # D face (27-35) to B face (45-53) - adjacent faces
        # D edges: 28, 30, 32, 34  |  B edges: 46, 48, 50, 52
        # D edge 34 and B edge 52 share physical edge
        test_cases.extend([
            (28, 46, 3), (46, 28, 3),
            (28, 48, 2), (48, 28, 2),
            (28, 50, 2), (50, 28, 2),
            (28, 52, 2), (52, 28, 2),

            (30, 46, 2), (46, 30, 2),
            (30, 48, 3), (48, 30, 3),
            (30, 50, 1), (50, 30, 1),
            (30, 52, 2), (52, 30, 2),

            (32, 46, 2), (46, 32, 2),
            (32, 48, 1), (48, 32, 1),
            (32, 50, 3), (50, 32, 3),
            (32, 52, 2), (52, 32, 2),

            (34, 46, 2), (46, 34, 2),
            (34, 48, 2), (48, 34, 2),
            (34, 50, 2), (50, 34, 2),
            (34, 52, 3), (52, 34, 3),
        ])

        # L face (36-44) to B face (45-53) - adjacent faces
        # L edges: 37, 39, 41, 43  |  B edges: 46, 48, 50, 52
        # L edge 37 and B edge 50 share physical edge
        test_cases.extend([
            (37, 46, 1), (46, 37, 1),
            (37, 48, 2), (48, 37, 2),
            (37, 50, 2), (50, 37, 2),
            (37, 52, 3), (52, 37, 3),

            (39, 46, 2), (46, 39, 2),
            (39, 48, 2), (48, 39, 2),
            (39, 50, 3), (50, 39, 3),
            (39, 52, 2), (52, 39, 2),

            (41, 46, 2), (46, 41, 2),
            (41, 48, 3), (48, 41, 3),
            (41, 50, 2), (50, 41, 2),
            (41, 52, 2), (52, 41, 2),

            (43, 46, 3), (46, 43, 3),
            (43, 48, 2), (48, 43, 2),
            (43, 50, 2), (50, 43, 2),
            (43, 52, 1), (52, 43, 1),
        ])

        for orig_pos, final_pos, expected_distance in test_cases:
            with self.subTest(orig=orig_pos, final=final_pos):
                distance = compute_qtm_distance(orig_pos, final_pos, self.cube)
                self.assertEqual(
                    distance, expected_distance,
                    f'Edge distance from {orig_pos} to {final_pos} '
                    f'should be {expected_distance} QTM but got {distance}',
                )

    def test_qtm_distance_adjacent_faces_centers(self) -> None:
        """
        Test QTM distance for center-to-center between adjacent faces.

        Center position: 4 (relative to face start)

        Geometric reasoning:
        - Center to center on adjacent faces: 2 QTM
          (Single face turn to move center from one face to adjacent)
        """
        test_cases = []

        # All adjacent face pairs for centers
        # U-R, U-F, U-L, U-B
        test_cases.extend([
            (4, 13, 2), (13, 4, 2),    # U to R
            (4, 22, 2), (22, 4, 2),    # U to F
            (4, 40, 2), (40, 4, 2),    # U to L
            (4, 49, 2), (49, 4, 2),    # U to B
        ])

        # R-F, R-B, R-D
        test_cases.extend([
            (13, 22, 2), (22, 13, 2),  # R to F
            (13, 49, 2), (49, 13, 2),  # R to B
            (13, 31, 2), (31, 13, 2),  # R to D
        ])

        # F-L, F-D
        test_cases.extend([
            (22, 40, 2), (40, 22, 2),  # F to L
            (22, 31, 2), (31, 22, 2),  # F to D
        ])

        # L-B, L-D
        test_cases.extend([
            (40, 49, 2), (49, 40, 2),  # L to B
            (40, 31, 2), (31, 40, 2),  # L to D
        ])

        # B-D
        test_cases.extend([
            (49, 31, 2), (31, 49, 2),  # B to D
        ])

        for orig_pos, final_pos, expected_distance in test_cases:
            with self.subTest(orig=orig_pos, final=final_pos):
                distance = compute_qtm_distance(orig_pos, final_pos, self.cube)
                self.assertEqual(
                    distance, expected_distance,
                    f'Center distance from {orig_pos} to {final_pos} '
                    f'should be {expected_distance} QTM but got {distance}',
                )


class TestRotationOnlyAlgorithms(unittest.TestCase):
    """Test that rotation-only algorithms have zero facelet displacement."""

    def test_all_single_rotations_zero_displacement(self) -> None:
        """Test all single rotation axes have zero displacement."""
        rotations = [
            'x', 'y', 'z',
            "x'", "y'", "z'",
            'x2', 'y2', 'z2',
            'x y', 'y z', 'x z',
        ]

        for rotation_str in rotations:
            with self.subTest(rotation=rotation_str):
                algorithm = Algorithm.parse_moves(rotation_str)
                result = compute_impacts(algorithm)

                self.assertEqual(
                    result.facelets_manhattan_distance.sum, 0,
                    f"Rotation '{rotation_str}' should have zero "
                    "Manhattan displacement",
                )
                self.assertEqual(
                    result.facelets_qtm_distance.sum, 0,
                    f"Rotation '{rotation_str}' should have zero "
                    "QTM displacement",
                )
                self.assertEqual(
                    result.facelets_mobilized_count, 0,
                    f"Rotation '{rotation_str}' should have zero "
                    "mobilized facelets",
                )

    def test_rotation_plus_moves_same_distance_as_moves_only(self) -> None:
        """Test that rotation + moves has same distance as moves only."""
        # Test with a simple scramble
        scramble = "R U R' U'"
        rotations = ['x', 'y', 'z', 'x2', 'y2', 'z2']

        # Get baseline distance (no rotation)
        baseline_algo = Algorithm.parse_moves(scramble)
        baseline_result = compute_impacts(baseline_algo)

        for rotation_str in rotations:
            with self.subTest(rotation=rotation_str):
                # Apply rotation before scramble
                rotated_algo = Algorithm.parse_moves(
                    f'{ rotation_str } { scramble }',
                )
                rotated_result = compute_impacts(rotated_algo)

                # Distance metrics should be identical
                self.assertEqual(
                    rotated_result.facelets_manhattan_distance.sum,
                    baseline_result.facelets_manhattan_distance.sum,
                    'Manhattan distance should be same with pre-rotation '
                    f"{ rotation_str }'",
                )
                self.assertEqual(
                    rotated_result.facelets_qtm_distance.sum,
                    baseline_result.facelets_qtm_distance.sum,
                    'QTM distance should be same with pre-rotation '
                    f"'{ rotation_str }'",
                )
                self.assertEqual(
                    rotated_result.facelets_mobilized_count,
                    baseline_result.facelets_mobilized_count,
                    'Mobilized count should be same with pre-rotation '
                    f"'{ rotation_str }'",
                )

    def test_moves_plus_rotation_same_distance_as_moves_only(self) -> None:
        """Test that moves + rotation has same distance as moves only."""
        # Test with a simple scramble
        scramble = "R U R' U'"
        rotations = ['x', 'y', 'z', 'x2', 'y2', 'z2']

        # Get baseline distance (no rotation)
        baseline_algo = Algorithm.parse_moves(scramble)
        baseline_result = compute_impacts(baseline_algo)

        for rotation_str in rotations:
            with self.subTest(rotation=rotation_str):
                # Apply rotation after scramble
                rotated_algo = Algorithm.parse_moves(
                    f'{scramble} {rotation_str}',
                )
                rotated_result = compute_impacts(rotated_algo)

                # Distance metrics should be identical
                self.assertEqual(
                    rotated_result.facelets_manhattan_distance.sum,
                    baseline_result.facelets_manhattan_distance.sum,
                    'Manhattan distance should be same with post-rotation '
                    f"'{ rotation_str }'",
                )
                self.assertEqual(
                    rotated_result.facelets_qtm_distance.sum,
                    baseline_result.facelets_qtm_distance.sum,
                    'QTM distance should be same with post-rotation '
                    f"'{ rotation_str }'",
                )
                self.assertEqual(
                    rotated_result.facelets_mobilized_count,
                    baseline_result.facelets_mobilized_count,
                    'Mobilized count should be same with post-rotation'
                    f"'{ rotation_str }'",
                )


class TestComputeImpacts(unittest.TestCase):
    """Test the compute_impacts function."""

    def test_empty_algorithm_no_impact(self) -> None:
        """Test that empty algorithm produces no impact."""
        algorithm = Algorithm()
        result = compute_impacts(algorithm)

        self.assertEqual(result.facelets_fixed_count, 54)
        self.assertEqual(result.facelets_mobilized_count, 0)
        self.assertEqual(result.facelets_scrambled_percent, 0.0)
        self.assertEqual(result.facelets_permutations, {})
        self.assertEqual(result.facelets_manhattan_distance.distances, {})
        self.assertEqual(result.facelets_manhattan_distance.mean, 0.0)
        self.assertEqual(result.facelets_manhattan_distance.max, 0)
        self.assertEqual(result.facelets_manhattan_distance.sum, 0)
        self.assertEqual(result.facelets_qtm_distance.distances, {})
        self.assertEqual(result.facelets_qtm_distance.mean, 0.0)
        self.assertEqual(result.facelets_qtm_distance.max, 0)
        self.assertEqual(result.facelets_qtm_distance.sum, 0)
        self.assertEqual(result.facelets_transformation_mask, '0' * 54)

        # All faces should have zero mobility
        for face_mobility in result.facelets_face_mobility.values():
            self.assertEqual(face_mobility, 0)

    def test_single_move_impact(self) -> None:
        """Test impact of a single move."""
        algorithm = Algorithm.parse_moves('R')
        result = compute_impacts(algorithm)

        # A single R move should affect some facelets
        self.assertGreater(result.facelets_mobilized_count, 0)
        self.assertLess(result.facelets_mobilized_count, 54)
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )
        expected_percent = result.facelets_mobilized_count / 48
        self.assertAlmostEqual(
            result.facelets_scrambled_percent,
            expected_percent,
        )

        # Should have some permutations
        self.assertGreater(len(result.facelets_permutations), 0)

        # Should have distance metrics
        if result.facelets_manhattan_distance.distances:
            self.assertGreater(result.facelets_manhattan_distance.mean, 0)
            self.assertGreater(result.facelets_manhattan_distance.max, 0)
            self.assertGreater(result.facelets_manhattan_distance.sum, 0)

    def test_double_move_impact(self) -> None:
        """Test impact of a double move."""
        algorithm = Algorithm.parse_moves('R2')
        result = compute_impacts(algorithm)

        self.assertGreater(result.facelets_mobilized_count, 0)
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )

        # Should have permutations
        self.assertGreater(len(result.facelets_permutations), 0)

    def test_face_move_distances(self) -> None:
        """
        Test that R2 should affect the same facelets as R
        but with more distances.
        """
        algo_r = Algorithm.parse_moves('R')
        result_r = compute_impacts(algo_r)

        algo_r2 = Algorithm.parse_moves('R2')
        result_r2 = compute_impacts(algo_r2)

        algo_rp = Algorithm.parse_moves("R'")
        result_rp = compute_impacts(algo_rp)

        self.assertGreater(
            result_r2.facelets_manhattan_distance.sum,
            result_r.facelets_manhattan_distance.sum,
        )
        self.assertEqual(
            result_r.facelets_manhattan_distance.sum,
            result_rp.facelets_manhattan_distance.sum,
        )

    def test_inverse_moves_cancel(self) -> None:
        """Test that inverse moves cancel each other out."""
        algorithm = Algorithm.parse_moves("R R'")
        result = compute_impacts(algorithm)

        # Should have no impact (moves cancel out)
        self.assertEqual(result.facelets_mobilized_count, 0)
        self.assertEqual(result.facelets_fixed_count, 54)
        self.assertEqual(result.facelets_scrambled_percent, 0.0)
        self.assertEqual(result.facelets_permutations, {})
        self.assertEqual(result.facelets_manhattan_distance.distances, {})
        self.assertEqual(result.facelets_manhattan_distance.mean, 0.0)
        self.assertEqual(result.facelets_manhattan_distance.max, 0)
        self.assertEqual(result.facelets_manhattan_distance.sum, 0)

    def test_four_moves_cancel(self) -> None:
        """Test that four identical moves cancel out."""
        algorithm = Algorithm.parse_moves('R R R R')
        result = compute_impacts(algorithm)

        # Four R moves should return to original state
        self.assertEqual(result.facelets_mobilized_count, 0)
        self.assertEqual(result.facelets_fixed_count, 54)
        self.assertEqual(result.facelets_scrambled_percent, 0.0)

    def test_complex_algorithm_impact(self) -> None:
        """Test impact of a complex algorithm."""
        algorithm = Algorithm.parse_moves("R U R' U'")
        result = compute_impacts(algorithm)

        # This is a common algorithm that should affect multiple faces
        self.assertGreater(result.facelets_mobilized_count, 0)
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )

        # Should have distance metrics
        if result.facelets_manhattan_distance.distances:
            self.assertGreaterEqual(result.facelets_manhattan_distance.mean, 0)
            self.assertGreaterEqual(result.facelets_manhattan_distance.max, 0)
            self.assertGreaterEqual(result.facelets_manhattan_distance.sum, 0)

    def test_algorithm_with_rotations(self) -> None:
        """Test impact of algorithm with cube rotations."""
        algorithm = Algorithm.parse_moves("x R U R' U' x'")
        result = compute_impacts(algorithm)

        # Should have some impact
        self.assertGreater(result.facelets_mobilized_count, 0)
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )

    def test_algorithm_with_incomplete_rotations(self) -> None:
        """Test impact of algorithm with cube rotations."""
        algorithm = Algorithm.parse_moves("x R U R' U'")
        result = compute_impacts(algorithm)

        self.assertEqual(result.facelets_scrambled_percent, 0.375)

        algorithm_no_x = Algorithm.parse_moves("R U R' U'")
        result_no_x = compute_impacts(algorithm_no_x)

        self.assertEqual(result_no_x.facelets_scrambled_percent, 0.375)

    def test_algorithm_with_single_rotation(self) -> None:
        """Test impact of algorithm with cube rotations."""
        algorithm = Algorithm.parse_moves('x')
        result = compute_impacts(algorithm)

        # Rotations removed
        self.assertEqual(result.facelets_mobilized_count, 0)

    def test_permutation_consistency(self) -> None:
        """Test that permutations are consistent with movement mask."""
        algorithm = Algorithm.parse_moves('R')
        result = compute_impacts(algorithm)

        # Number of permutations should equal mobilized count
        self.assertEqual(
            len(result.facelets_permutations),
            result.facelets_mobilized_count,
        )

        # Permutation positions should correspond to '1's in mask
        moved_positions = [
            i for i, char in enumerate(result.facelets_transformation_mask)
            if char == '1'
        ]
        self.assertEqual(
            set(result.facelets_permutations.keys()),
            set(moved_positions),
        )

    def test_distance_calculation_consistency(self) -> None:
        """Test that distance calculations are consistent."""
        algorithm = Algorithm.parse_moves('R U')
        result = compute_impacts(algorithm)

        if result.facelets_manhattan_distance.distances:
            # Distance mean should match manual calculation
            values = list(result.facelets_manhattan_distance.distances.values())
            calculated_mean = sum(values) / len(values)
            self.assertAlmostEqual(
                result.facelets_manhattan_distance.mean,
                calculated_mean,
            )

            # Distance sum should match
            distance_sum = sum(
                result.facelets_manhattan_distance.distances.values(),
            )
            self.assertEqual(
                result.facelets_manhattan_distance.sum,
                distance_sum,
            )

            # Distance max should match
            distance_max = max(
                result.facelets_manhattan_distance.distances.values(),
            )
            self.assertEqual(
                result.facelets_manhattan_distance.max,
                distance_max,
            )

    def test_face_mobility_consistency(self) -> None:
        """Test that face mobility sums correctly."""
        algorithm = Algorithm.parse_moves('R U F')
        result = compute_impacts(algorithm)

        # Sum of face mobility should equal mobilized count
        total_face_mobility = sum(result.facelets_face_mobility.values())
        self.assertEqual(total_face_mobility, result.facelets_mobilized_count)

        # Face mobility should have all faces
        self.assertEqual(
            set(result.facelets_face_mobility.keys()),
            set(FACE_ORDER),
        )

    def test_scrambled_percent_bounds(self) -> None:
        """Test that scrambled percent is within valid bounds."""
        algorithms = [
            Algorithm(),  # Empty
            Algorithm.parse_moves('R'),  # Single move
            # Complex algorithm
            Algorithm.parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'"),
        ]

        for algorithm in algorithms:
            result = compute_impacts(algorithm)

            # Should be between 0 and 1
            self.assertGreaterEqual(result.facelets_scrambled_percent, 0.0)
            self.assertLessEqual(result.facelets_scrambled_percent, 1.0)

            # Should match calculation
            expected_percent = result.facelets_mobilized_count / 48
            self.assertAlmostEqual(
                result.facelets_scrambled_percent,
                expected_percent,
            )

    def test_transformation_mask_length(self) -> None:
        """Test that transformation mask always has correct length."""
        algorithms = [
            Algorithm(),
            Algorithm.parse_moves('R'),
            Algorithm.parse_moves("R U R' U'"),
            Algorithm.parse_moves('M E S'),
        ]

        for algorithm in algorithms:
            result = compute_impacts(algorithm)
            self.assertEqual(len(result.facelets_transformation_mask), 54)

            # Should only contain '0' and '1'
            valid_chars = all(
                char in '01' for char in result.facelets_transformation_mask
            )
            self.assertTrue(valid_chars)

    def test_vcube_state_preservation(self) -> None:
        """Test that the returned VCube reflects the algorithm application."""
        algorithm = Algorithm.parse_moves("R U R' U'")
        result = compute_impacts(algorithm)

        # The cube should be in the state after applying the algorithm
        expected_cube = VCube()
        expected_cube.rotate(algorithm)

        self.assertEqual(result.cube.state, expected_cube.state)

    def test_edge_case_wide_moves(self) -> None:
        """Test impact calculation with wide moves."""
        algorithm = Algorithm.parse_moves('Rw')
        result = compute_impacts(algorithm)

        # Wide moves should affect more facelets than regular moves
        self.assertGreater(result.facelets_mobilized_count, 0)
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )

    def test_edge_case_slice_moves(self) -> None:
        """Test impact calculation with slice moves."""
        algorithm = Algorithm.parse_moves('M')
        result = compute_impacts(algorithm)

        # Slice moves should affect some facelets
        self.assertGreater(result.facelets_mobilized_count, 0)
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )

    def test_distance_values_non_negative(self) -> None:
        """Test that all distance values are non-negative."""
        algorithm = Algorithm.parse_moves('R U F D L B')
        result = compute_impacts(algorithm)

        for distance in result.facelets_manhattan_distance.distances.values():
            self.assertGreaterEqual(distance, 0)

        self.assertGreaterEqual(result.facelets_manhattan_distance.mean, 0)
        self.assertGreaterEqual(result.facelets_manhattan_distance.max, 0)
        self.assertGreaterEqual(result.facelets_manhattan_distance.sum, 0)

    def test_empty_permutations_empty_distances(self) -> None:
        """Test when no moves occur, permutations and distances are empty."""
        algorithm = Algorithm.parse_moves("R R'")  # Cancel out
        result = compute_impacts(algorithm)

        self.assertEqual(result.facelets_permutations, {})
        self.assertEqual(result.facelets_manhattan_distance.distances, {})
        self.assertEqual(result.facelets_manhattan_distance.mean, 0.0)
        self.assertEqual(result.facelets_manhattan_distance.max, 0)
        self.assertEqual(result.facelets_manhattan_distance.sum, 0)


class TestComputeImpactsEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for the impacts module."""

    def test_very_long_algorithm(self) -> None:
        """Test impact calculation with very long algorithm."""
        # Create a long algorithm with many moves
        moves = ['R', 'U', "R'", "U'"] * 25  # 100 moves
        algorithm = Algorithm.parse_moves(' '.join(moves))
        result = compute_impacts(algorithm)

        # Should still work correctly
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )
        self.assertGreaterEqual(result.facelets_scrambled_percent, 0.0)
        self.assertLessEqual(result.facelets_scrambled_percent, 1.0)

    def test_algorithm_with_all_move_types(self) -> None:
        """Test algorithm containing all types of moves."""
        algorithm = Algorithm.parse_moves('R U F D L B M E S x y z Rw Uw Fw')
        result = compute_impacts(algorithm)

        # Should handle all move types
        self.assertEqual(
            result.facelets_fixed_count + result.facelets_mobilized_count,
            54,
        )
        self.assertIsInstance(result.facelets_face_mobility, dict)
        self.assertEqual(len(result.facelets_face_mobility), 6)

    def test_identical_algorithms_identical_results(self) -> None:
        """Test that identical algorithms produce identical results."""
        algorithm1 = Algorithm.parse_moves("R U R' U'")
        algorithm2 = Algorithm.parse_moves("R U R' U'")

        result1 = compute_impacts(algorithm1)
        result2 = compute_impacts(algorithm2)

        self.assertEqual(
            result1.facelets_transformation_mask,
            result2.facelets_transformation_mask,
        )
        self.assertEqual(
            result1.facelets_fixed_count,
            result2.facelets_fixed_count,
        )
        self.assertEqual(
            result1.facelets_mobilized_count,
            result2.facelets_mobilized_count,
        )
        self.assertEqual(
            result1.facelets_permutations,
            result2.facelets_permutations,
        )
        self.assertEqual(
            result1.facelets_manhattan_distance.distances,
            result2.facelets_manhattan_distance.distances,
        )
        self.assertEqual(
            result1.facelets_face_mobility,
            result2.facelets_face_mobility,
        )

    def test_numeric_precision(self) -> None:
        """Test numeric precision in distance calculations."""
        # Complex algorithm for testing precision
        algorithm = Algorithm.parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F'",
        )
        result = compute_impacts(algorithm)

        if result.facelets_manhattan_distance.distances:
            # Mean should be precise
            manual_mean = (
                sum(result.facelets_manhattan_distance.distances.values())
                / len(result.facelets_manhattan_distance.distances)
            )
            self.assertAlmostEqual(
                result.facelets_manhattan_distance.mean,
                manual_mean,
                places=10,
            )

            # Sum should be exact
            distance_sum = sum(
                result.facelets_manhattan_distance.distances.values(),
            )
            self.assertEqual(
                result.facelets_manhattan_distance.sum,
                distance_sum,
            )

    def test_face_mobility_edge_cases(self) -> None:
        """Test face mobility calculation edge cases."""
        # Test with algorithm that might affect only certain faces
        algorithm = Algorithm.parse_moves('R R R R')  # Should cancel out
        result = compute_impacts(algorithm)

        # All face mobility should be 0
        for _face, mobility in result.facelets_face_mobility.items():
            self.assertEqual(mobility, 0)

    def test_algorithm_commutativity_check(self) -> None:
        """Test different algorithm orders can produce different impacts."""
        algorithm1 = Algorithm.parse_moves('R U')
        algorithm2 = Algorithm.parse_moves('U R')

        result1 = compute_impacts(algorithm1)
        result2 = compute_impacts(algorithm2)

        # Results may be different (cube operations are not commutative)
        # But both should be valid
        self.assertEqual(
            result1.facelets_fixed_count + result1.facelets_mobilized_count,
            54,
        )
        self.assertEqual(
            result2.facelets_fixed_count + result2.facelets_mobilized_count,
            54,
        )


class TestFindPermutationCycles(unittest.TestCase):
    """Test the find_permutation_cycles function."""

    def test_identity_permutation(self) -> None:
        """Test permutation where nothing moves."""
        permutation = list(range(8))
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(cycles, [])

    def test_single_two_cycle(self) -> None:
        """Test single swap (2-cycle)."""
        permutation = [1, 0, 2, 3, 4, 5, 6, 7]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 2)
        self.assertIn(0, cycles[0])
        self.assertIn(1, cycles[0])

    def test_single_three_cycle(self) -> None:
        """Test single 3-cycle."""
        permutation = [1, 2, 0, 3, 4, 5, 6, 7]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 3)
        self.assertEqual(set(cycles[0]), {0, 1, 2})

    def test_multiple_cycles(self) -> None:
        """Test multiple independent cycles."""
        permutation = [1, 0, 3, 2, 5, 4, 6, 7]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(len(cycles), 3)
        cycle_sets = [set(cycle) for cycle in cycles]
        self.assertIn({0, 1}, cycle_sets)
        self.assertIn({2, 3}, cycle_sets)
        self.assertIn({4, 5}, cycle_sets)

    def test_single_long_cycle(self) -> None:
        """Test single cycle involving all elements."""
        permutation = [1, 2, 3, 4, 5, 6, 7, 0]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 8)

    def test_four_cycle(self) -> None:
        """Test 4-cycle."""
        permutation = [1, 2, 3, 0, 4, 5, 6, 7]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(len(cycles[0]), 4)
        self.assertEqual(set(cycles[0]), {0, 1, 2, 3})

    def test_mixed_cycles(self) -> None:
        """Test mix of different cycle lengths."""
        permutation = [1, 0, 3, 4, 2, 5, 6, 7]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(len(cycles), 2)
        cycle_lengths = sorted([len(c) for c in cycles])
        self.assertEqual(cycle_lengths, [2, 3])

    def test_empty_permutation(self) -> None:
        """Test empty permutation."""
        permutation: list[int] = []
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(cycles, [])

    def test_single_element(self) -> None:
        """Test single element permutation."""
        permutation = [0]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(cycles, [])


class TestComputeFaceToFaceMatrix(unittest.TestCase):
    """Test the compute_face_to_face_matrix function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_empty_permutations(self) -> None:
        """Test with no permutations."""
        matrix = compute_face_to_face_matrix({}, self.cube)
        for face in FACE_ORDER:
            self.assertIn(face, matrix)
            for target_face in FACE_ORDER:
                self.assertEqual(matrix[face][target_face], 0)

    def test_same_face_permutation(self) -> None:
        """Test permutation within same face."""
        permutations = {0: 1, 1: 2, 2: 0}
        matrix = compute_face_to_face_matrix(permutations, self.cube)
        self.assertEqual(matrix['U']['U'], 3)
        for face in ['R', 'F', 'D', 'L', 'B']:
            self.assertEqual(matrix['U'][face], 0)

    def test_cross_face_permutation(self) -> None:
        """Test permutation across different faces."""
        permutations = {0: 9, 9: 18, 18: 0}
        matrix = compute_face_to_face_matrix(permutations, self.cube)
        self.assertEqual(matrix['U']['R'], 1)
        self.assertEqual(matrix['R']['F'], 1)
        self.assertEqual(matrix['F']['U'], 1)

    def test_multiple_face_transfers(self) -> None:
        """Test multiple facelets moving to different faces."""
        permutations = {
            0: 9,
            1: 10,
            2: 18,
            3: 19,
        }
        matrix = compute_face_to_face_matrix(permutations, self.cube)
        self.assertEqual(matrix['U']['R'], 2)
        self.assertEqual(matrix['U']['F'], 2)

    def test_matrix_structure(self) -> None:
        """Test matrix has correct structure."""
        permutations = {0: 1}
        matrix = compute_face_to_face_matrix(permutations, self.cube)
        self.assertEqual(len(matrix), 6)
        for face in FACE_ORDER:
            self.assertIn(face, matrix)
            self.assertEqual(len(matrix[face]), 6)
            for target_face in FACE_ORDER:
                self.assertIn(target_face, matrix[face])


class TestDetectSymmetry(unittest.TestCase):
    """Test the detect_symmetry function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_empty_mask(self) -> None:
        """Test mask with no impact."""
        mask = '0' * 54
        result = detect_symmetry(mask, self.cube)
        self.assertTrue(result['no_impact'])
        self.assertFalse(result['full_impact'])
        self.assertTrue(result['all_faces_same'])
        self.assertTrue(result['opposite_faces_symmetric'])

    def test_full_mask(self) -> None:
        """Test mask with complete impact."""
        mask = '1' * 54
        result = detect_symmetry(mask, self.cube)
        self.assertFalse(result['no_impact'])
        self.assertTrue(result['full_impact'])
        self.assertTrue(result['all_faces_same'])
        self.assertTrue(result['opposite_faces_symmetric'])

    def test_all_faces_same_pattern(self) -> None:
        """Test same pattern on all faces."""
        pattern = '101010101'
        mask = pattern * 6
        result = detect_symmetry(mask, self.cube)
        self.assertTrue(result['all_faces_same'])
        self.assertFalse(result['no_impact'])
        self.assertFalse(result['full_impact'])

    def test_opposite_faces_symmetric(self) -> None:
        """Test opposite faces have same pattern."""
        u_face = '111000000'
        r_face = '000111000'
        f_face = '000000111'
        d_face = '111000000'
        l_face = '000111000'
        b_face = '000000111'
        mask = u_face + r_face + f_face + d_face + l_face + b_face
        result = detect_symmetry(mask, self.cube)
        self.assertTrue(result['opposite_faces_symmetric'])
        self.assertFalse(result['all_faces_same'])

    def test_no_symmetry(self) -> None:
        """Test pattern with no symmetry."""
        mask = '1' * 10 + '0' * 44
        result = detect_symmetry(mask, self.cube)
        self.assertFalse(result['all_faces_same'])
        self.assertFalse(result['opposite_faces_symmetric'])
        self.assertFalse(result['no_impact'])
        self.assertFalse(result['full_impact'])

    def test_partial_pattern(self) -> None:
        """Test partial impact pattern."""
        mask = '1' * 27 + '0' * 27
        result = detect_symmetry(mask, self.cube)
        self.assertFalse(result['no_impact'])
        self.assertFalse(result['full_impact'])


class TestAnalyzeLayers(unittest.TestCase):
    """Test the analyze_layers function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_no_permutations(self) -> None:
        """Test with no permutations."""
        result = analyze_layers({}, self.cube)
        self.assertEqual(result['centers_moved'], 0)
        self.assertEqual(result['edges_moved'], 0)
        self.assertEqual(result['corners_moved'], 0)

    def test_only_centers_moved(self) -> None:
        """Test when only center pieces move."""
        permutations = {4: 13, 13: 4}
        result = analyze_layers(permutations, self.cube)
        self.assertEqual(result['centers_moved'], 2)
        self.assertEqual(result['edges_moved'], 0)
        self.assertEqual(result['corners_moved'], 0)

    def test_only_edges_moved(self) -> None:
        """Test when only edge pieces move."""
        permutations = {1: 3, 3: 1, 5: 7, 7: 5}
        result = analyze_layers(permutations, self.cube)
        self.assertEqual(result['centers_moved'], 0)
        self.assertEqual(result['edges_moved'], 4)
        self.assertEqual(result['corners_moved'], 0)

    def test_only_corners_moved(self) -> None:
        """Test when only corner pieces move."""
        permutations = {0: 2, 2: 0, 6: 8, 8: 6}
        result = analyze_layers(permutations, self.cube)
        self.assertEqual(result['centers_moved'], 0)
        self.assertEqual(result['edges_moved'], 0)
        self.assertEqual(result['corners_moved'], 4)

    def test_mixed_layer_movement(self) -> None:
        """Test when different layer types move."""
        permutations = {
            0: 1,
            1: 2,
            4: 13,
        }
        result = analyze_layers(permutations, self.cube)
        self.assertEqual(result['centers_moved'], 1)
        self.assertEqual(result['edges_moved'], 1)
        self.assertEqual(result['corners_moved'], 1)

    def test_all_corners_moved(self) -> None:
        """Test all corner positions move."""
        corner_positions = []
        for face_idx in range(6):
            face_start = face_idx * 9
            corner_positions.extend([
                face_start + 0, face_start + 2,
                face_start + 6, face_start + 8,
            ])
        permutations = {pos: (pos + 1) % 54 for pos in corner_positions}
        result = analyze_layers(permutations, self.cube)
        self.assertEqual(result['corners_moved'], 24)


class TestComputeParity(unittest.TestCase):
    """Test the compute_parity function."""

    def test_identity_permutation(self) -> None:
        """Test identity permutation has even parity."""
        permutation = list(range(8))
        parity = compute_parity(permutation)
        self.assertEqual(parity, 0)

    def test_single_swap_odd_parity(self) -> None:
        """Test single swap has odd parity."""
        permutation = [1, 0, 2, 3, 4, 5, 6, 7]
        parity = compute_parity(permutation)
        self.assertEqual(parity, 1)

    def test_two_swaps_even_parity(self) -> None:
        """Test two swaps have even parity."""
        permutation = [1, 0, 3, 2, 4, 5, 6, 7]
        parity = compute_parity(permutation)
        self.assertEqual(parity, 0)

    def test_three_cycle_even_parity(self) -> None:
        """Test 3-cycle has even parity."""
        permutation = [1, 2, 0, 3, 4, 5, 6, 7]
        parity = compute_parity(permutation)
        self.assertEqual(parity, 0)

    def test_four_cycle_odd_parity(self) -> None:
        """Test 4-cycle has odd parity."""
        permutation = [1, 2, 3, 0, 4, 5, 6, 7]
        parity = compute_parity(permutation)
        self.assertEqual(parity, 1)

    def test_five_cycle_even_parity(self) -> None:
        """Test 5-cycle has even parity."""
        permutation = [1, 2, 3, 4, 0, 5, 6, 7]
        parity = compute_parity(permutation)
        self.assertEqual(parity, 0)

    def test_empty_permutation(self) -> None:
        """Test empty permutation."""
        permutation: list[int] = []
        parity = compute_parity(permutation)
        self.assertEqual(parity, 0)

    def test_complex_permutation(self) -> None:
        """Test complex permutation."""
        permutation = [1, 0, 3, 2, 5, 4, 7, 6]
        parity = compute_parity(permutation)
        self.assertEqual(parity, 0)


class TestAnalyzeCycles(unittest.TestCase):
    """Test the analyze_cycles function."""

    def test_empty_cycles(self) -> None:
        """Test with no cycles."""
        result = analyze_cycles([])
        self.assertEqual(result['cycle_count'], 0)
        self.assertEqual(result['cycle_lengths'], [])
        self.assertEqual(result['min_cycle_length'], 0)
        self.assertEqual(result['max_cycle_length'], 0)
        self.assertEqual(result['total_pieces_in_cycles'], 0)
        self.assertEqual(result['two_cycles'], 0)
        self.assertEqual(result['three_cycles'], 0)
        self.assertEqual(result['four_plus_cycles'], 0)

    def test_single_two_cycle(self) -> None:
        """Test single 2-cycle analysis."""
        cycles = [[0, 1]]
        result = analyze_cycles(cycles)
        self.assertEqual(result['cycle_count'], 1)
        self.assertEqual(result['cycle_lengths'], [2])
        self.assertEqual(result['min_cycle_length'], 2)
        self.assertEqual(result['max_cycle_length'], 2)
        self.assertEqual(result['total_pieces_in_cycles'], 2)
        self.assertEqual(result['two_cycles'], 1)
        self.assertEqual(result['three_cycles'], 0)
        self.assertEqual(result['four_plus_cycles'], 0)

    def test_single_three_cycle(self) -> None:
        """Test single 3-cycle analysis."""
        cycles = [[0, 1, 2]]
        result = analyze_cycles(cycles)
        self.assertEqual(result['cycle_count'], 1)
        self.assertEqual(result['cycle_lengths'], [3])
        self.assertEqual(result['min_cycle_length'], 3)
        self.assertEqual(result['max_cycle_length'], 3)
        self.assertEqual(result['total_pieces_in_cycles'], 3)
        self.assertEqual(result['two_cycles'], 0)
        self.assertEqual(result['three_cycles'], 1)
        self.assertEqual(result['four_plus_cycles'], 0)

    def test_single_four_plus_cycle(self) -> None:
        """Test 4+ cycle analysis."""
        cycles = [[0, 1, 2, 3]]
        result = analyze_cycles(cycles)
        self.assertEqual(result['cycle_count'], 1)
        self.assertEqual(result['cycle_lengths'], [4])
        self.assertEqual(result['min_cycle_length'], 4)
        self.assertEqual(result['max_cycle_length'], 4)
        self.assertEqual(result['total_pieces_in_cycles'], 4)
        self.assertEqual(result['two_cycles'], 0)
        self.assertEqual(result['three_cycles'], 0)
        self.assertEqual(result['four_plus_cycles'], 1)

    def test_multiple_mixed_cycles(self) -> None:
        """Test multiple cycles of different lengths."""
        cycles = [[0, 1], [2, 3, 4], [5, 6, 7, 8, 9]]
        result = analyze_cycles(cycles)
        self.assertEqual(result['cycle_count'], 3)
        self.assertEqual(result['cycle_lengths'], [2, 3, 5])
        self.assertEqual(result['min_cycle_length'], 2)
        self.assertEqual(result['max_cycle_length'], 5)
        self.assertEqual(result['total_pieces_in_cycles'], 10)
        self.assertEqual(result['two_cycles'], 1)
        self.assertEqual(result['three_cycles'], 1)
        self.assertEqual(result['four_plus_cycles'], 1)

    def test_multiple_two_cycles(self) -> None:
        """Test multiple 2-cycles."""
        cycles = [[0, 1], [2, 3], [4, 5]]
        result = analyze_cycles(cycles)
        self.assertEqual(result['cycle_count'], 3)
        self.assertEqual(result['two_cycles'], 3)
        self.assertEqual(result['three_cycles'], 0)
        self.assertEqual(result['four_plus_cycles'], 0)

    def test_long_cycle(self) -> None:
        """Test long cycle."""
        cycles = [[0, 1, 2, 3, 4, 5, 6, 7]]
        result = analyze_cycles(cycles)
        self.assertEqual(result['cycle_count'], 1)
        self.assertEqual(result['min_cycle_length'], 8)
        self.assertEqual(result['max_cycle_length'], 8)
        self.assertEqual(result['four_plus_cycles'], 1)


class TestClassifyPattern(unittest.TestCase):
    """Test the classify_pattern function."""

    def test_solved_state(self) -> None:
        """Test solved cube pattern."""
        cp = list(range(8))
        co = [0] * 8
        ep = list(range(12))
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('SOLVED', patterns)
        self.assertEqual(len(patterns), 1)

    def test_all_oriented(self) -> None:
        """Test all pieces oriented but not permuted."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('ALL_ORIENTED', patterns)

    def test_corners_oriented_only(self) -> None:
        """Test only corners oriented."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('CORNERS_ORIENTED', patterns)
        self.assertNotIn('ALL_ORIENTED', patterns)

    def test_edges_oriented_only(self) -> None:
        """Test only edges oriented."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [1, 0, 0, 0, 0, 0, 0, 0]
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('EDGES_ORIENTED', patterns)
        self.assertNotIn('ALL_ORIENTED', patterns)

    def test_all_permuted(self) -> None:
        """Test all pieces permuted but misoriented."""
        cp = list(range(8))
        co = [1, 0, 0, 0, 0, 0, 0, 0]
        ep = list(range(12))
        eo = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('ALL_PERMUTED', patterns)

    def test_corners_permuted_only(self) -> None:
        """Test only corners permuted."""
        cp = list(range(8))
        co = [1, 0, 0, 0, 0, 0, 0, 0]
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('CORNERS_PERMUTED', patterns)
        self.assertNotIn('ALL_PERMUTED', patterns)

    def test_edges_permuted_only(self) -> None:
        """Test only edges permuted."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = list(range(12))
        eo = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('EDGES_PERMUTED', patterns)
        self.assertNotIn('ALL_PERMUTED', patterns)

    def test_oll_corners_done(self) -> None:
        """Test OLL with corners oriented."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('OLL_CORNERS_DONE', patterns)

    def test_oll_edges_done(self) -> None:
        """Test OLL with edges oriented."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [1, 0, 0, 0, 0, 0, 0, 0]
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('OLL_EDGES_DONE', patterns)

    def test_oll_complete_pll_remaining(self) -> None:
        """Test OLL complete but PLL remaining."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('OLL_COMPLETE_PLL_REMAINING', patterns)

    def test_permuted_but_misoriented(self) -> None:
        """Test pieces permuted but misoriented."""
        cp = list(range(8))
        co = [1, 0, 0, 0, 0, 0, 0, 0]
        ep = list(range(12))
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('PERMUTED_BUT_MISORIENTED', patterns)

    def test_first_layer_corners_solved(self) -> None:
        """Test first layer corners solved."""
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('FIRST_LAYER_CORNERS_SOLVED', patterns)

    def test_first_layer_edges_solved(self) -> None:
        """Test first layer edges solved."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('FIRST_LAYER_EDGES_SOLVED', patterns)

    def test_first_layer_complete(self) -> None:
        """Test first layer complete."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('FIRST_LAYER_COMPLETE', patterns)

    def test_cross_solved(self) -> None:
        """Test cross solved."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('CROSS_SOLVED', patterns)

    def test_f2l_complete(self) -> None:
        """Test F2L complete."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('F2L_COMPLETE', patterns)

    def test_last_layer_oriented(self) -> None:
        """Test last layer oriented."""
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('LAST_LAYER_ORIENTED', patterns)

    def test_pll_case(self) -> None:
        """Test PLL case detection - last layer oriented but not permuted."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        # This gets OLL_COMPLETE_PLL_REMAINING instead of PLL_CASE
        # because it's oriented but not permuted
        self.assertIn('OLL_COMPLETE_PLL_REMAINING', patterns)

    def test_pll_edges_only(self) -> None:
        """Test PLL with edges needing permutation outside U layer."""
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = [0, 4, 2, 3, 1, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('PLL_EDGES_ONLY', patterns)

    def test_pll_corners_only(self) -> None:
        """Test PLL with corners needing permutation outside U layer."""
        cp = [0, 4, 2, 3, 1, 5, 6, 7]
        co = [0] * 8
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('PLL_CORNERS_ONLY', patterns)

    def test_oll_case(self) -> None:
        """Test OLL case detection."""
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [1, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('OLL_CASE', patterns)

    def test_oll_case_with_f2l_incomplete(self) -> None:
        """Test OLL case when F2L is not complete."""
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [1, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 9, 8, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertNotIn('OLL_CASE', patterns)

    def test_highly_scrambled(self) -> None:
        """Test highly scrambled pattern."""
        cp = [7, 6, 5, 4, 3, 2, 1, 0]
        co = [0] * 8
        ep = list(range(12))
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('HIGHLY_SCRAMBLED', patterns)

    def test_minimally_scrambled(self) -> None:
        """Test minimally scrambled pattern."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = list(range(12))
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('MINIMALLY_SCRAMBLED', patterns)

    def test_single_corner_cycle(self) -> None:
        """Test single cycle involving all corners."""
        cp = [1, 2, 3, 4, 5, 6, 7, 0]
        co = [0] * 8
        ep = list(range(12))
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('SINGLE_CORNER_CYCLE', patterns)

    def test_single_edge_cycle(self) -> None:
        """Test single cycle involving all edges."""
        cp = list(range(8))
        co = [0] * 8
        ep = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('SINGLE_EDGE_CYCLE', patterns)

    def test_single_corner_swap(self) -> None:
        """Test single corner swap."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = list(range(12))
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('SINGLE_CORNER_SWAP', patterns)

    def test_single_edge_swap(self) -> None:
        """Test single edge swap."""
        cp = list(range(8))
        co = [0] * 8
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('SINGLE_EDGE_SWAP', patterns)

    def test_corner_three_cycle(self) -> None:
        """Test corner 3-cycle pattern."""
        cp = [1, 2, 0, 3, 4, 5, 6, 7]
        co = [0] * 8
        ep = list(range(12))
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('CORNER_THREE_CYCLE', patterns)

    def test_edge_three_cycle(self) -> None:
        """Test edge 3-cycle pattern."""
        cp = list(range(8))
        co = [0] * 8
        ep = [1, 2, 0, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0] * 12
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('EDGE_THREE_CYCLE', patterns)

    def test_unclassified_pattern(self) -> None:
        """Test pattern that doesn't match standard classifications."""
        cp = [0, 2, 1, 3, 5, 4, 6, 7]
        co = [1, 1, 1, 0, 0, 0, 0, 0]
        ep = [2, 1, 0, 3, 5, 4, 6, 7, 8, 9, 10, 11]
        eo = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        patterns = classify_pattern(cp, co, ep, eo)
        self.assertIn('UNCLASSIFIED', patterns)


class TestComputeCubieComplexity(unittest.TestCase):
    """Test the compute_cubie_complexity function."""

    def test_solved_state_complexity(self) -> None:
        """Test complexity of solved state."""
        complexity, approach = compute_cubie_complexity(0, 0, 0, 0)
        self.assertEqual(complexity, 0)
        self.assertEqual(approach, 'Solved state')

    def test_pll_case_complexity(self) -> None:
        """Test PLL case (permutation only)."""
        complexity, approach = compute_cubie_complexity(2, 0, 3, 0)
        self.assertEqual(complexity, 5)
        self.assertEqual(
            approach,
            'PLL case - permutation only, use permutation algorithms',
        )

    def test_oll_case_complexity(self) -> None:
        """Test OLL case (orientation only)."""
        complexity, approach = compute_cubie_complexity(0, 2, 0, 3)
        self.assertEqual(complexity, 5)
        self.assertEqual(
            approach,
            'OLL case - orientation only, use orientation algorithms',
        )

    def test_simple_case_complexity(self) -> None:
        """Test simple case with low complexity."""
        complexity, approach = compute_cubie_complexity(2, 1, 2, 2)
        self.assertEqual(complexity, 7)
        self.assertEqual(
            approach,
            'Simple case - direct algorithms may be sufficient',
        )

    def test_complex_case_complexity(self) -> None:
        """Test complex case with high complexity."""
        complexity, approach = compute_cubie_complexity(4, 3, 5, 4)
        self.assertEqual(complexity, 16)
        self.assertEqual(
            approach,
            'Complex case - multi-stage solving approach recommended',
        )

    def test_boundary_case_seven(self) -> None:
        """Test boundary at complexity 7."""
        complexity, approach = compute_cubie_complexity(1, 2, 2, 2)
        self.assertEqual(complexity, 7)
        self.assertEqual(
            approach,
            'Simple case - direct algorithms may be sufficient',
        )

    def test_boundary_case_eight(self) -> None:
        """Test boundary at complexity 8."""
        complexity, approach = compute_cubie_complexity(2, 2, 2, 2)
        self.assertEqual(complexity, 8)
        self.assertEqual(
            approach,
            'Complex case - multi-stage solving approach recommended',
        )

    def test_all_corners_complexity(self) -> None:
        """Test all corners moved and twisted."""
        complexity, approach = compute_cubie_complexity(8, 8, 0, 0)
        self.assertEqual(complexity, 16)
        self.assertEqual(
            approach,
            'Complex case - multi-stage solving approach recommended',
        )

    def test_all_edges_complexity(self) -> None:
        """Test all edges moved and flipped."""
        complexity, approach = compute_cubie_complexity(0, 0, 12, 12)
        self.assertEqual(complexity, 24)
        self.assertEqual(
            approach,
            'Complex case - multi-stage solving approach recommended',
        )


class TestOrientationInvariance(unittest.TestCase):
    """
    Test that distance metrics are invariant under cube orientation.

    When applying the same scramble to differently oriented cubes,
    the distances statistics (sum, mean, max) should be identical
    because the physical movement of pieces is the same regardless of
    how we label the faces.
    """

    SCRAMBLE = "R U R' U' L' B L B' R2 D F2 D' R' U2 L U L' B2 R F"
    ORIENTATIONS = ('', 'z2', 'x', 'x y')

    def check_orientation_invariance(
            self,
            metric_type: str,
            *, pre_orientation: bool,
    ) -> None:
        """
        Check that distance metrics are invariant under orientation.
        """
        algorithm = Algorithm.parse_moves(self.SCRAMBLE)
        metric_name = metric_type.title()
        results = []

        for orientation in self.ORIENTATIONS:
            if pre_orientation:
                oriented_algo = orientation + algorithm
            else:
                oriented_algo = algorithm + orientation

            impacts = compute_impacts(oriented_algo)
            distance_metrics = (
                impacts.facelets_manhattan_distance
                if metric_type == 'manhattan'
                else impacts.facelets_qtm_distance
            )

            results.append({
                'orientation': orientation,
                'sum': distance_metrics.sum,
                'mean': distance_metrics.mean,
                'max': distance_metrics.max,
            })

        # Assert all orientations have identical metrics
        base_result = results[0]
        for result in results[1:]:
            self.assertEqual(
                result['sum'],
                base_result['sum'],
                f'{ metric_name } sum differs between '
                f"{ base_result['orientation'] } and { result['orientation'] }",
            )

            self.assertEqual(
                result['mean'],
                base_result['mean'],
                f'{ metric_name } mean differs between '
                f"{ base_result['orientation'] } "
                f"and { result['orientation'] }",
            )

            self.assertEqual(
                result['max'],
                base_result['max'],
                f'{ metric_name } max differs between '
                f"{ base_result['orientation'] } and { result['orientation'] }",
            )

    def test_manhattan_distance_invariant_under_pre_orientation(self) -> None:
        """
        Test Manhattan distance metrics are same across pre orientations.
        """
        self.check_orientation_invariance('manhattan', pre_orientation=True)

    def test_manhattan_distance_invariant_under_post_orientation(self) -> None:
        """
        Test Manhattan distance metrics are same across post orientations.
        """
        self.check_orientation_invariance('manhattan', pre_orientation=False)

    def test_qtm_distance_invariant_under_pre_orientation(self) -> None:
        """
        Test that QTM distance metrics remain the same across pre orientations.
        """
        self.check_orientation_invariance('qtm', pre_orientation=True)

    def test_qtm_distance_invariant_under_post_orientation(self) -> None:
        """
        Test that QTM distance metrics remain the same across post orientations.
        """
        self.check_orientation_invariance('qtm', pre_orientation=False)
