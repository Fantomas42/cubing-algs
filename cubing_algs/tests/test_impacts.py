import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.impacts import ImpactData
from cubing_algs.impacts import compute_distance
from cubing_algs.impacts import compute_face_impact
from cubing_algs.impacts import compute_impacts
from cubing_algs.vcube import VCube


class TestImpactData(unittest.TestCase):
    """Test the ImpactData NamedTuple structure and properties."""

    def test_impact_data_structure(self) -> None:
        """Test ImpactData can be created with all required fields."""
        cube = VCube()
        impact_data = ImpactData(
            cube=cube,
            transformation_mask='0' * 54,
            fixed_count=54,
            mobilized_count=0,
            scrambled_percent=0.0,
            permutations={},
            distances={},
            distance_mean=0.0,
            distance_max=0,
            distance_sum=0,
            face_mobility={
                'U': 0, 'R': 0, 'F': 0,
                'D': 0, 'L': 0, 'B': 0,
            },
        )

        self.assertIsInstance(impact_data.cube, VCube)
        self.assertEqual(impact_data.transformation_mask, '0' * 54)
        self.assertEqual(impact_data.fixed_count, 54)
        self.assertEqual(impact_data.mobilized_count, 0)
        self.assertEqual(impact_data.scrambled_percent, 0.0)
        self.assertEqual(impact_data.permutations, {})
        self.assertEqual(impact_data.distances, {})
        self.assertEqual(impact_data.distance_mean, 0.0)
        self.assertEqual(impact_data.distance_max, 0)
        self.assertEqual(impact_data.distance_sum, 0)
        self.assertIsInstance(impact_data.face_mobility, dict)

    def test_impact_data_field_access(self) -> None:
        """Test individual field access on ImpactData."""
        cube = VCube()
        face_mobility = {'U': 1, 'R': 2, 'F': 3, 'D': 4, 'L': 5, 'B': 6}

        impact_data = ImpactData(
            cube=cube,
            transformation_mask='1' * 20 + '0' * 34,
            fixed_count=34,
            mobilized_count=20,
            scrambled_percent=20.0 / 54.0,
            permutations={0: 10, 1: 11},
            distances={0: 2, 1: 3},
            distance_mean=2.5,
            distance_max=3,
            distance_sum=5,
            face_mobility=face_mobility,
        )

        # Test all fields are accessible
        self.assertEqual(len(impact_data.transformation_mask), 54)
        self.assertEqual(impact_data.fixed_count, 34)
        self.assertEqual(impact_data.mobilized_count, 20)
        self.assertAlmostEqual(impact_data.scrambled_percent, 20.0 / 54.0)
        self.assertEqual(impact_data.permutations[0], 10)
        self.assertEqual(impact_data.distances[1], 3)
        self.assertEqual(impact_data.distance_mean, 2.5)
        self.assertEqual(impact_data.distance_max, 3)
        self.assertEqual(impact_data.distance_sum, 5)
        self.assertEqual(impact_data.face_mobility['U'], 1)


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


class TestComputeDistance(unittest.TestCase):
    """Test the compute_distance function."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_same_position_distance(self) -> None:
        """Test distance between same position is zero."""
        distance = compute_distance(0, 0, self.cube)
        self.assertEqual(distance, 0)

        distance = compute_distance(26, 26, self.cube)
        self.assertEqual(distance, 0)

        distance = compute_distance(53, 53, self.cube)
        self.assertEqual(distance, 0)

    def test_same_face_manhattan_distance(self) -> None:
        """Test Manhattan distance within the same face."""
        # U face positions (0-8): positions are laid out as:
        # 0 1 2
        # 3 4 5
        # 6 7 8

        # Adjacent positions (row or column neighbors)
        distance = compute_distance(0, 1, self.cube)  # Same row
        self.assertEqual(distance, 1)

        distance = compute_distance(1, 4, self.cube)  # Same column
        self.assertEqual(distance, 1)

        distance = compute_distance(4, 5, self.cube)  # Adjacent
        self.assertEqual(distance, 1)

        # Diagonal positions
        distance = compute_distance(0, 4, self.cube)  # Center diagonal
        self.assertEqual(distance, 2)

        distance = compute_distance(0, 8, self.cube)  # Opposite corners
        self.assertEqual(distance, 4)

    def test_different_face_distance(self) -> None:
        """Test distance between different faces."""
        cube_size = self.cube.size

        # From U face (position 0) to R face (position 9)
        # Should be cube_size + manhattan distance
        distance = compute_distance(0, 9, self.cube)
        self.assertEqual(distance, cube_size + 0)  # Same relative position

        # From U face corner to R face corner
        # U top-right to R top-right
        distance = compute_distance(2, 11, self.cube)
        self.assertEqual(distance, cube_size + 0)

    def test_opposite_face_distance(self) -> None:
        """Test distance between opposite faces."""
        cube_size = self.cube.size

        # U and D are opposite faces
        u_center = 4  # U face center
        d_center = 31  # D face center (27 + 4)

        distance = compute_distance(u_center, d_center, self.cube)
        # Should be cube_size * 2 (opposite factor) + manhattan distance
        self.assertEqual(distance, cube_size * 2 + 0)

    def test_face_boundaries(self) -> None:
        """Test distance calculations at face boundaries."""
        # Test first position of each face
        for i in range(6):
            face_start = i * 9
            distance = compute_distance(face_start, face_start, self.cube)
            self.assertEqual(distance, 0)

        # Test last position of each face
        for i in range(6):
            face_end = i * 9 + 8
            distance = compute_distance(face_end, face_end, self.cube)
            self.assertEqual(distance, 0)

    def test_edge_cases_positions(self) -> None:
        """Test edge cases with extreme positions."""
        # First position to last position
        distance = compute_distance(0, 53, self.cube)
        self.assertEqual(distance, 7)

        # Cross face movement
        distance = compute_distance(8, 9, self.cube)  # U to R face
        self.assertEqual(distance, 7)

    def test_distance_symmetry_property(self) -> None:
        """Test distance calculation handles position ordering correctly."""
        # Distance should be based on relative positions, not order
        distance1 = compute_distance(0, 10, self.cube)
        distance2 = compute_distance(10, 0, self.cube)

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

        self.assertEqual(result.fixed_count, 54)
        self.assertEqual(result.mobilized_count, 0)
        self.assertEqual(result.scrambled_percent, 0.0)
        self.assertEqual(result.permutations, {})
        self.assertEqual(result.distances, {})
        self.assertEqual(result.distance_mean, 0.0)
        self.assertEqual(result.distance_max, 0)
        self.assertEqual(result.distance_sum, 0)
        self.assertEqual(result.transformation_mask, '0' * 54)

        # All faces should have zero mobility
        for face_mobility in result.face_mobility.values():
            self.assertEqual(face_mobility, 0)

    def test_single_move_impact(self) -> None:
        """Test impact of a single move."""
        algorithm = Algorithm.parse_moves('R')
        result = compute_impacts(algorithm)

        # A single R move should affect some facelets
        self.assertGreater(result.mobilized_count, 0)
        self.assertLess(result.mobilized_count, 54)
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)
        expected_percent = result.mobilized_count / 54
        self.assertAlmostEqual(result.scrambled_percent, expected_percent)

        # Should have some permutations
        self.assertGreater(len(result.permutations), 0)

        # Should have distance metrics
        if result.distances:
            self.assertGreater(result.distance_mean, 0)
            self.assertGreater(result.distance_max, 0)
            self.assertGreater(result.distance_sum, 0)

    def test_double_move_impact(self) -> None:
        """Test impact of a double move."""
        algorithm = Algorithm.parse_moves('R2')
        result = compute_impacts(algorithm)

        self.assertGreater(result.mobilized_count, 0)
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)

        # Should have permutations
        self.assertGreater(len(result.permutations), 0)

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

        self.assertGreater(result_r2.distance_sum, result_r.distance_sum)
        self.assertEqual(result_r.distance_sum, result_rp.distance_sum)

    def test_inverse_moves_cancel(self) -> None:
        """Test that inverse moves cancel each other out."""
        algorithm = Algorithm.parse_moves("R R'")
        result = compute_impacts(algorithm)

        # Should have no impact (moves cancel out)
        self.assertEqual(result.mobilized_count, 0)
        self.assertEqual(result.fixed_count, 54)
        self.assertEqual(result.scrambled_percent, 0.0)
        self.assertEqual(result.permutations, {})
        self.assertEqual(result.distances, {})
        self.assertEqual(result.distance_mean, 0.0)
        self.assertEqual(result.distance_max, 0)
        self.assertEqual(result.distance_sum, 0)

    def test_four_moves_cancel(self) -> None:
        """Test that four identical moves cancel out."""
        algorithm = Algorithm.parse_moves('R R R R')
        result = compute_impacts(algorithm)

        # Four R moves should return to original state
        self.assertEqual(result.mobilized_count, 0)
        self.assertEqual(result.fixed_count, 54)
        self.assertEqual(result.scrambled_percent, 0.0)

    def test_complex_algorithm_impact(self) -> None:
        """Test impact of a complex algorithm."""
        algorithm = Algorithm.parse_moves("R U R' U'")
        result = compute_impacts(algorithm)

        # This is a common algorithm that should affect multiple faces
        self.assertGreater(result.mobilized_count, 0)
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)

        # Should have distance metrics
        if result.distances:
            self.assertGreaterEqual(result.distance_mean, 0)
            self.assertGreaterEqual(result.distance_max, 0)
            self.assertGreaterEqual(result.distance_sum, 0)

    def test_algorithm_with_rotations(self) -> None:
        """Test impact of algorithm with cube rotations."""
        algorithm = Algorithm.parse_moves("x R U R' U' x'")
        result = compute_impacts(algorithm)

        # Should have some impact
        self.assertGreater(result.mobilized_count, 0)
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)

    def test_algorithm_with_single_rotation(self) -> None:
        """Test impact of algorithm with cube rotations."""
        algorithm = Algorithm.parse_moves('x')
        result = compute_impacts(algorithm)

        # Actually all should be moved except L R centers
        self.assertEqual(result.mobilized_count, 52)

    def test_permutation_consistency(self) -> None:
        """Test that permutations are consistent with movement mask."""
        algorithm = Algorithm.parse_moves('R')
        result = compute_impacts(algorithm)

        # Number of permutations should equal mobilized count
        self.assertEqual(len(result.permutations), result.mobilized_count)

        # Permutation positions should correspond to '1's in mask
        moved_positions = [
            i for i, char in enumerate(result.transformation_mask)
            if char == '1'
        ]
        self.assertEqual(set(result.permutations.keys()), set(moved_positions))

    def test_distance_calculation_consistency(self) -> None:
        """Test that distance calculations are consistent."""
        algorithm = Algorithm.parse_moves('R U')
        result = compute_impacts(algorithm)

        if result.distances:
            # Distance mean should match manual calculation
            values = list(result.distances.values())
            calculated_mean = sum(values) / len(values)
            self.assertAlmostEqual(result.distance_mean, calculated_mean)

            # Distance sum should match
            distance_sum = sum(result.distances.values())
            self.assertEqual(result.distance_sum, distance_sum)

            # Distance max should match
            distance_max = max(result.distances.values())
            self.assertEqual(result.distance_max, distance_max)

    def test_face_mobility_consistency(self) -> None:
        """Test that face mobility sums correctly."""
        algorithm = Algorithm.parse_moves('R U F')
        result = compute_impacts(algorithm)

        # Sum of face mobility should equal mobilized count
        total_face_mobility = sum(result.face_mobility.values())
        self.assertEqual(total_face_mobility, result.mobilized_count)

        # Face mobility should have all faces
        self.assertEqual(set(result.face_mobility.keys()), set(FACE_ORDER))

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
            self.assertGreaterEqual(result.scrambled_percent, 0.0)
            self.assertLessEqual(result.scrambled_percent, 1.0)

            # Should match calculation
            expected_percent = result.mobilized_count / 54
            self.assertAlmostEqual(result.scrambled_percent, expected_percent)

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
            self.assertEqual(len(result.transformation_mask), 54)

            # Should only contain '0' and '1'
            valid_chars = all(
                char in '01' for char in result.transformation_mask
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
        self.assertGreater(result.mobilized_count, 0)
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)

    def test_edge_case_slice_moves(self) -> None:
        """Test impact calculation with slice moves."""
        algorithm = Algorithm.parse_moves('M')
        result = compute_impacts(algorithm)

        # Slice moves should affect some facelets
        self.assertGreater(result.mobilized_count, 0)
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)

    def test_distance_values_non_negative(self) -> None:
        """Test that all distance values are non-negative."""
        algorithm = Algorithm.parse_moves('R U F D L B')
        result = compute_impacts(algorithm)

        for distance in result.distances.values():
            self.assertGreaterEqual(distance, 0)

        self.assertGreaterEqual(result.distance_mean, 0)
        self.assertGreaterEqual(result.distance_max, 0)
        self.assertGreaterEqual(result.distance_sum, 0)

    def test_empty_permutations_empty_distances(self) -> None:
        """Test when no moves occur, permutations and distances are empty."""
        algorithm = Algorithm.parse_moves("R R'")  # Cancel out
        result = compute_impacts(algorithm)

        self.assertEqual(result.permutations, {})
        self.assertEqual(result.distances, {})
        self.assertEqual(result.distance_mean, 0.0)
        self.assertEqual(result.distance_max, 0)
        self.assertEqual(result.distance_sum, 0)


class TestComputeImpactsEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for the impacts module."""

    def test_very_long_algorithm(self) -> None:
        """Test impact calculation with very long algorithm."""
        # Create a long algorithm with many moves
        moves = ['R', 'U', "R'", "U'"] * 25  # 100 moves
        algorithm = Algorithm.parse_moves(' '.join(moves))
        result = compute_impacts(algorithm)

        # Should still work correctly
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)
        self.assertGreaterEqual(result.scrambled_percent, 0.0)
        self.assertLessEqual(result.scrambled_percent, 1.0)

    def test_algorithm_with_all_move_types(self) -> None:
        """Test algorithm containing all types of moves."""
        algorithm = Algorithm.parse_moves('R U F D L B M E S x y z Rw Uw Fw')
        result = compute_impacts(algorithm)

        # Should handle all move types
        self.assertEqual(result.fixed_count + result.mobilized_count, 54)
        self.assertIsInstance(result.face_mobility, dict)
        self.assertEqual(len(result.face_mobility), 6)

    def test_identical_algorithms_identical_results(self) -> None:
        """Test that identical algorithms produce identical results."""
        algorithm1 = Algorithm.parse_moves("R U R' U'")
        algorithm2 = Algorithm.parse_moves("R U R' U'")

        result1 = compute_impacts(algorithm1)
        result2 = compute_impacts(algorithm2)

        self.assertEqual(
            result1.transformation_mask, result2.transformation_mask,
        )
        self.assertEqual(result1.fixed_count, result2.fixed_count)
        self.assertEqual(result1.mobilized_count, result2.mobilized_count)
        self.assertEqual(result1.permutations, result2.permutations)
        self.assertEqual(result1.distances, result2.distances)
        self.assertEqual(result1.face_mobility, result2.face_mobility)

    def test_numeric_precision(self) -> None:
        """Test numeric precision in distance calculations."""
        # Complex algorithm for testing precision
        algorithm = Algorithm.parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F'",
        )
        result = compute_impacts(algorithm)

        if result.distances:
            # Mean should be precise
            manual_mean = sum(result.distances.values()) / len(result.distances)
            self.assertAlmostEqual(result.distance_mean, manual_mean, places=10)

            # Sum should be exact
            distance_sum = sum(result.distances.values())
            self.assertEqual(result.distance_sum, distance_sum)

    def test_face_mobility_edge_cases(self) -> None:
        """Test face mobility calculation edge cases."""
        # Test with algorithm that might affect only certain faces
        algorithm = Algorithm.parse_moves('R R R R')  # Should cancel out
        result = compute_impacts(algorithm)

        # All face mobility should be 0
        for _face, mobility in result.face_mobility.items():
            self.assertEqual(mobility, 0)

    def test_algorithm_commutativity_check(self) -> None:
        """Test different algorithm orders can produce different impacts."""
        algorithm1 = Algorithm.parse_moves('R U')
        algorithm2 = Algorithm.parse_moves('U R')

        result1 = compute_impacts(algorithm1)
        result2 = compute_impacts(algorithm2)

        # Results may be different (cube operations are not commutative)
        # But both should be valid
        self.assertEqual(result1.fixed_count + result1.mobilized_count, 54)
        self.assertEqual(result2.fixed_count + result2.mobilized_count, 54)
