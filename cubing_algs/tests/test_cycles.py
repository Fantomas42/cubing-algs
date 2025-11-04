"""Tests for cycle order calculation."""

import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.cycles import compute_cycles


class ComputeCyclesTestCase(unittest.TestCase):
    """Test cases for the compute_cycles function."""

    def test_empty_algorithm(self) -> None:
        """Test cycles computation for empty algorithm."""
        algorithm = Algorithm()
        result = compute_cycles(algorithm)
        self.assertEqual(result, 0)

    def test_single_quarter_turn(self) -> None:
        """Test cycles computation for a single quarter turn."""
        algorithm = Algorithm.parse_moves('R')
        result = compute_cycles(algorithm)
        self.assertEqual(result, 4)  # R4 = identity, so R has order 4

    def test_single_half_turn(self) -> None:
        """Test cycles computation for a single half turn."""
        algorithm = Algorithm.parse_moves('R2')
        result = compute_cycles(algorithm)
        self.assertEqual(result, 2)  # R2 * R2 = identity, so R2 has order 2

    def test_sexy_move(self) -> None:
        """Test cycles computation for R U R' U' (sexy move)."""
        algorithm = Algorithm.parse_moves("R U R' U'")
        result = compute_cycles(algorithm)
        self.assertEqual(result, 6)  # Known order of this algorithm

    def test_t_perm(self) -> None:
        """Test cycles computation for T-perm algorithm."""
        algorithm = Algorithm.parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F'",
        )
        result = compute_cycles(algorithm)
        # T-perm returns to solved in 2 applications
        self.assertEqual(result, 2)

    def test_4_move_commutator(self) -> None:
        """Test cycles computation for simple 4-move commutator."""
        algorithm = Algorithm.parse_moves("R U R' U'")
        result = compute_cycles(algorithm)
        # This is the sexy move, known to have order 6
        self.assertEqual(result, 6)

    def test_rotation_moves(self) -> None:
        """Test cycles computation with cube rotations."""
        algorithm = Algorithm.parse_moves('x')
        result = compute_cycles(algorithm)
        self.assertEqual(result, 1)  # x rotation doesn't change solved state

    def test_slice_moves(self) -> None:
        """Test cycles computation with slice moves."""
        algorithm = Algorithm.parse_moves('M')
        result = compute_cycles(algorithm)
        self.assertEqual(result, 4)  # M move has order 4

    def test_double_slice_move(self) -> None:
        """Test cycles computation for double slice move."""
        algorithm = Algorithm.parse_moves('M2')
        result = compute_cycles(algorithm)
        self.assertEqual(result, 2)  # M2 has order 2

    def test_wide_moves(self) -> None:
        """Test cycles computation with wide moves."""
        algorithm = Algorithm.parse_moves('r')
        result = compute_cycles(algorithm)
        self.assertEqual(result, 4)  # r (wide R) has order 4

    def test_complex_algorithm(self) -> None:
        """Test cycles computation for more complex algorithm."""
        algorithm = Algorithm.parse_moves("R U2 R' D' R U' R' D")
        result = compute_cycles(algorithm)
        # This should have a finite order
        self.assertEqual(result, 12)

    def test_algorithm_that_scrambles_extensively(self) -> None:
        """Test cycles computation for algorithm that takes many iterations."""
        # This is a known algorithm with high order
        algorithm = Algorithm.parse_moves("R U R' U R U2 R'")
        result = compute_cycles(algorithm)
        # Should have a specific order but not hit the 100 limit
        self.assertEqual(result, 6)

    def test_safety_limit_not_reached(self) -> None:
        """Test that normal algorithms don't hit the safety limit."""
        test_cases = [
            'R',
            'R2',
            "R U R' U'",
            "F R U' R' U' R U R' F'",  # OLL algorithm
            "R U R' U R U2 R'",  # Right trigger
        ]

        for moves_str in test_cases:
            with self.subTest(moves=moves_str):
                algorithm = Algorithm.parse_moves(moves_str)
                result = compute_cycles(algorithm)
                self.assertLess(
                    result, 100,
                    f"Algorithm '{moves_str}' hit safety limit",
                )

    def test_identity_algorithm(self) -> None:
        """Test cycles computation for algorithms that cancel out."""
        algorithm = Algorithm.parse_moves("R R'")
        result = compute_cycles(algorithm)
        self.assertEqual(result, 1)  # Identity has order 1

    def test_double_identity(self) -> None:
        """Test cycles computation for double identity."""
        algorithm = Algorithm.parse_moves('R2 R2')
        result = compute_cycles(algorithm)
        self.assertEqual(result, 1)  # Identity has order 1

    def test_commutator_identity(self) -> None:
        """Test cycles computation for commutator that equals identity."""
        # [R, U] [U, R]^-1 = identity
        algorithm = Algorithm.parse_moves("R U R' U' U R U' R'")
        result = compute_cycles(algorithm)
        self.assertEqual(result, 1)  # Identity has order 1

    def test_edge_case_single_move_variations(self) -> None:
        """Test cycles computation for various single move types."""
        test_cases = [
            ('F', 4),    # F has order 4
            ("F'", 4),   # F' has order 4
            ('F2', 2),   # F2 has order 2
            ('B', 4),    # B has order 4
            ('U', 4),    # U has order 4
            ('D', 4),    # D has order 4
            ('L', 4),    # L has order 4
        ]

        for moves_str, expected_cycles in test_cases:
            with self.subTest(moves=moves_str):
                algorithm = Algorithm.parse_moves(moves_str)
                result = compute_cycles(algorithm)
                self.assertEqual(result, expected_cycles)

    def test_input_type_algorithm_objects(self) -> None:
        """Test that compute_cycles accepts Algorithm objects."""
        algorithm = Algorithm.parse_moves("R U R' U'")
        result = compute_cycles(algorithm)
        self.assertEqual(result, 6)
