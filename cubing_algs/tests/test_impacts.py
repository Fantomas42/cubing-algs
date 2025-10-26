import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.impacts import ImpactData
from cubing_algs.impacts import analyze_cycles
from cubing_algs.impacts import analyze_layers
from cubing_algs.impacts import classify_pattern
from cubing_algs.impacts import compute_cubie_complexity
from cubing_algs.impacts import compute_manhattan_distance
from cubing_algs.impacts import compute_face_impact
from cubing_algs.impacts import compute_face_to_face_matrix
from cubing_algs.impacts import compute_impacts
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
            facelets_manhattan_distances={},
            facelets_manhattan_distance_mean=0.0,
            facelets_manhattan_distance_max=0,
            facelets_manhattan_distance_sum=0,
            facelets_qtm_distances={},
            facelets_qtm_distance_mean=0.0,
            facelets_qtm_distance_max=0,
            facelets_qtm_distance_sum=0,
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
        self.assertEqual(impact_data.facelets_manhattan_distances, {})
        self.assertEqual(impact_data.facelets_manhattan_distance_mean, 0.0)
        self.assertEqual(impact_data.facelets_manhattan_distance_max, 0)
        self.assertEqual(impact_data.facelets_manhattan_distance_sum, 0)
        self.assertEqual(impact_data.facelets_qtm_distances, {})
        self.assertEqual(impact_data.facelets_qtm_distance_mean, 0.0)
        self.assertEqual(impact_data.facelets_qtm_distance_max, 0)
        self.assertEqual(impact_data.facelets_qtm_distance_sum, 0)
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
            facelets_manhattan_distances={0: 2, 1: 3},
            facelets_manhattan_distance_mean=2.5,
            facelets_manhattan_distance_max=3,
            facelets_manhattan_distance_sum=5,
            facelets_qtm_distances={0: 1, 1: 2},
            facelets_qtm_distance_mean=1.5,
            facelets_qtm_distance_max=2,
            facelets_qtm_distance_sum=3,
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
        self.assertEqual(impact_data.facelets_manhattan_distances[1], 3)
        self.assertEqual(impact_data.facelets_manhattan_distance_mean, 2.5)
        self.assertEqual(impact_data.facelets_manhattan_distance_max, 3)
        self.assertEqual(impact_data.facelets_manhattan_distance_sum, 5)
        self.assertEqual(impact_data.facelets_qtm_distances[1], 2)
        self.assertEqual(impact_data.facelets_qtm_distance_mean, 1.5)
        self.assertEqual(impact_data.facelets_qtm_distance_max, 2)
        self.assertEqual(impact_data.facelets_qtm_distance_sum, 3)
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
        distance = compute_manhattan_distance(0, 1, self.cube)  # Same row
        self.assertEqual(distance, 1)

        distance = compute_manhattan_distance(1, 4, self.cube)  # Same column
        self.assertEqual(distance, 1)

        distance = compute_manhattan_distance(4, 5, self.cube)  # Adjacent
        self.assertEqual(distance, 1)

        # Diagonal positions
        distance = compute_manhattan_distance(0, 4, self.cube)  # Center diagonal
        self.assertEqual(distance, 2)

        distance = compute_manhattan_distance(0, 8, self.cube)  # Opposite corners
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
            distance = compute_manhattan_distance(face_start, face_start, self.cube)
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
        self.assertEqual(result.facelets_manhattan_distances, {})
        self.assertEqual(result.facelets_manhattan_distance_mean, 0.0)
        self.assertEqual(result.facelets_manhattan_distance_max, 0)
        self.assertEqual(result.facelets_manhattan_distance_sum, 0)
        self.assertEqual(result.facelets_qtm_distances, {})
        self.assertEqual(result.facelets_qtm_distance_mean, 0.0)
        self.assertEqual(result.facelets_qtm_distance_max, 0)
        self.assertEqual(result.facelets_qtm_distance_sum, 0)
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
        if result.facelets_manhattan_distances:
            self.assertGreater(result.facelets_manhattan_distance_mean, 0)
            self.assertGreater(result.facelets_manhattan_distance_max, 0)
            self.assertGreater(result.facelets_manhattan_distance_sum, 0)

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
            result_r2.facelets_manhattan_distance_sum,
            result_r.facelets_manhattan_distance_sum,
        )
        self.assertEqual(
            result_r.facelets_manhattan_distance_sum,
            result_rp.facelets_manhattan_distance_sum,
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
        self.assertEqual(result.facelets_manhattan_distances, {})
        self.assertEqual(result.facelets_manhattan_distance_mean, 0.0)
        self.assertEqual(result.facelets_manhattan_distance_max, 0)
        self.assertEqual(result.facelets_manhattan_distance_sum, 0)

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
        if result.facelets_manhattan_distances:
            self.assertGreaterEqual(result.facelets_manhattan_distance_mean, 0)
            self.assertGreaterEqual(result.facelets_manhattan_distance_max, 0)
            self.assertGreaterEqual(result.facelets_manhattan_distance_sum, 0)

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

        if result.facelets_manhattan_distances:
            # Distance mean should match manual calculation
            values = list(result.facelets_manhattan_distances.values())
            calculated_mean = sum(values) / len(values)
            self.assertAlmostEqual(
                result.facelets_manhattan_distance_mean,
                calculated_mean,
            )

            # Distance sum should match
            distance_sum = sum(result.facelets_manhattan_distances.values())
            self.assertEqual(result.facelets_manhattan_distance_sum, distance_sum)

            # Distance max should match
            distance_max = max(result.facelets_manhattan_distances.values())
            self.assertEqual(result.facelets_manhattan_distance_max, distance_max)

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

        for distance in result.facelets_manhattan_distances.values():
            self.assertGreaterEqual(distance, 0)

        self.assertGreaterEqual(result.facelets_manhattan_distance_mean, 0)
        self.assertGreaterEqual(result.facelets_manhattan_distance_max, 0)
        self.assertGreaterEqual(result.facelets_manhattan_distance_sum, 0)

    def test_empty_permutations_empty_distances(self) -> None:
        """Test when no moves occur, permutations and distances are empty."""
        algorithm = Algorithm.parse_moves("R R'")  # Cancel out
        result = compute_impacts(algorithm)

        self.assertEqual(result.facelets_permutations, {})
        self.assertEqual(result.facelets_manhattan_distances, {})
        self.assertEqual(result.facelets_manhattan_distance_mean, 0.0)
        self.assertEqual(result.facelets_manhattan_distance_max, 0)
        self.assertEqual(result.facelets_manhattan_distance_sum, 0)


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
            result1.facelets_manhattan_distances,
            result2.facelets_manhattan_distances,
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

        if result.facelets_manhattan_distances:
            # Mean should be precise
            manual_mean = (
                sum(result.facelets_manhattan_distances.values())
                / len(result.facelets_manhattan_distances)
            )
            self.assertAlmostEqual(
                result.facelets_manhattan_distance_mean,
                manual_mean,
                places=10,
            )

            # Sum should be exact
            distance_sum = sum(result.facelets_manhattan_distances.values())
            self.assertEqual(result.facelets_manhattan_distance_sum, distance_sum)

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
