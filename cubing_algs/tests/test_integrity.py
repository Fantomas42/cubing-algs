"""Tests for integrity module."""
import unittest

from cubing_algs.constants import CORNER_NUMBER
from cubing_algs.constants import CORNER_VALID_ORIENTATIONS
from cubing_algs.constants import EDGE_NUMBER
from cubing_algs.constants import EDGE_VALID_ORIENTATIONS
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EP
from cubing_algs.integrity import compute_parity
from cubing_algs.integrity import find_permutation_cycles
from cubing_algs.integrity import is_valid_orientation
from cubing_algs.integrity import is_valid_permutation


class TestComputeParity(unittest.TestCase):
    """Tests for compute_parity function."""

    def test_identity_permutation_even(self) -> None:
        """Test that identity permutation has even parity (0)."""
        self.assertEqual(compute_parity([0, 1, 2, 3]), 0)

    def test_solved_corner_permutation_even(self) -> None:
        """Test that solved corner permutation has even parity."""
        self.assertEqual(compute_parity(list(SOLVED_CP)), 0)

    def test_solved_edge_permutation_even(self) -> None:
        """Test that solved edge permutation has even parity."""
        self.assertEqual(compute_parity(list(SOLVED_EP)), 0)

    def test_single_transposition_odd(self) -> None:
        """Test that a single transposition (swap) has odd parity (1)."""
        # Swap positions 0 and 1
        perm = [1, 0, 2, 3, 4, 5, 6, 7]
        self.assertEqual(compute_parity(perm), 1)

    def test_two_transpositions_even(self) -> None:
        """Test that two transpositions have even parity."""
        perm = [1, 0, 3, 2, 4, 5, 6, 7]
        self.assertEqual(compute_parity(perm), 0)

    def test_three_transpositions_odd(self) -> None:
        """Test that three transpositions have odd parity."""
        # Swap (0,1), (2,3), and (4,5)
        perm = [1, 0, 3, 2, 5, 4, 6, 7]
        self.assertEqual(compute_parity(perm), 1)

    def test_3_cycle_even(self) -> None:
        """Test that a 3-cycle has even parity (requires 2 transpositions)."""
        # (0 1 2): 0→1, 1→2, 2→0
        perm = [1, 2, 0, 3, 4, 5, 6, 7]
        self.assertEqual(compute_parity(perm), 0)

    def test_4_cycle_odd(self) -> None:
        """Test that a 4-cycle has odd parity (requires 3 transpositions)."""
        # (0 1 2 3): 0→1, 1→2, 2→3, 3→0
        perm = [1, 2, 3, 0, 4, 5, 6, 7]
        self.assertEqual(compute_parity(perm), 1)

    def test_5_cycle_even(self) -> None:
        """Test that a 5-cycle has even parity (requires 4 transpositions)."""
        # (0 1 2 3 4): 0→1, 1→2, 2→3, 3→4, 4→0
        perm = [1, 2, 3, 4, 0, 5, 6, 7]
        self.assertEqual(compute_parity(perm), 0)

    def test_two_disjoint_3_cycles_even(self) -> None:
        """Test two disjoint 3-cycles have even parity (4 transpositions)."""
        perm = [1, 2, 0, 4, 5, 3, 6, 7]
        self.assertEqual(compute_parity(perm), 0)

    def test_3_cycle_and_transposition_odd(self) -> None:
        """Test 3-cycle plus transposition has odd parity (2+1=3)."""
        # (0 1 2)(3 4)
        perm = [1, 2, 0, 4, 3, 5, 6, 7]
        self.assertEqual(compute_parity(perm), 1)

    def test_empty_permutation(self) -> None:
        """Test that empty permutation has even parity."""
        self.assertEqual(compute_parity([]), 0)

    def test_single_element_permutation(self) -> None:
        """Test that single-element permutation has even parity."""
        self.assertEqual(compute_parity([0]), 0)

    def test_fixed_points_ignored(self) -> None:
        """Test that fixed points don't affect parity calculation."""
        # Only positions 0,1 are swapped, rest are fixed
        perm = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        self.assertEqual(compute_parity(perm), 1)


class TestFindPermutationCycles(unittest.TestCase):
    """Tests for find_permutation_cycles function."""

    def test_identity_no_cycles(self) -> None:
        """Test that identity permutation has no cycles."""
        self.assertEqual(find_permutation_cycles([0, 1, 2, 3]), [])

    def test_single_transposition(self) -> None:
        """Test that a single transposition forms one 2-cycle."""
        cycles = find_permutation_cycles([1, 0, 2, 3])
        self.assertEqual(len(cycles), 1)
        self.assertEqual(set(cycles[0]), {0, 1})

    def test_3_cycle(self) -> None:
        """Test that a 3-cycle is found correctly."""
        cycles = find_permutation_cycles([1, 2, 0, 3, 4])
        self.assertEqual(len(cycles), 1)
        self.assertEqual(set(cycles[0]), {0, 1, 2})

    def test_two_disjoint_cycles(self) -> None:
        """Test finding two disjoint cycles."""
        # (0 1)(2 3 4)
        cycles = find_permutation_cycles([1, 0, 3, 4, 2, 5])
        self.assertEqual(len(cycles), 2)
        cycle_sets = [set(c) for c in cycles]
        self.assertIn({0, 1}, cycle_sets)
        self.assertIn({2, 3, 4}, cycle_sets)

    def test_empty_permutation(self) -> None:
        """Test that empty permutation has no cycles."""
        self.assertEqual(find_permutation_cycles([]), [])

    def test_fixed_points_excluded(self) -> None:
        """Test that fixed points are not included in cycles."""
        # Only 0,1 swap, 2,3,4 are fixed
        cycles = find_permutation_cycles([1, 0, 2, 3, 4])
        self.assertEqual(len(cycles), 1)
        self.assertEqual(set(cycles[0]), {0, 1})

    def test_identity_permutation(self) -> None:
        """Test permutation where nothing moves."""
        permutation = SOLVED_CP
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

    def test_single_element(self) -> None:
        """Test single element permutation."""
        permutation = [0]
        cycles = find_permutation_cycles(permutation)
        self.assertEqual(cycles, [])


class TestIsValidPermutation(unittest.TestCase):
    """Tests for is_valid_permutation function."""

    def test_valid_corner_permutation(self) -> None:
        """Test that solved corner permutation is valid."""
        self.assertTrue(is_valid_permutation(list(SOLVED_CP), CORNER_NUMBER))

    def test_valid_edge_permutation(self) -> None:
        """Test that solved edge permutation is valid."""
        self.assertTrue(is_valid_permutation(list(SOLVED_EP), EDGE_NUMBER))

    def test_valid_shuffled_permutation(self) -> None:
        """Test that a shuffled permutation is valid."""
        self.assertTrue(is_valid_permutation([3, 1, 0, 2], 4))

    def test_invalid_wrong_size(self) -> None:
        """Test that wrong size permutation is invalid."""
        self.assertFalse(is_valid_permutation([0, 1, 2], 4))

    def test_invalid_duplicate_value(self) -> None:
        """Test that permutation with duplicate is invalid."""
        self.assertFalse(is_valid_permutation([0, 1, 1, 3], 4))

    def test_invalid_out_of_range(self) -> None:
        """Test that permutation with out-of-range value is invalid."""
        self.assertFalse(is_valid_permutation([0, 1, 2, 5], 4))

    def test_empty_permutation(self) -> None:
        """Test that empty permutation is valid for size 0."""
        self.assertTrue(is_valid_permutation([], 0))


class TestIsValidOrientation(unittest.TestCase):
    """Tests for is_valid_orientation function."""

    def test_valid_corner_orientation(self) -> None:
        """Test that valid corner orientation passes."""
        co = [0, 1, 2, 0, 1, 2, 0, 1]
        self.assertTrue(
            is_valid_orientation(co, CORNER_NUMBER, CORNER_VALID_ORIENTATIONS),
        )

    def test_valid_edge_orientation(self) -> None:
        """Test that valid edge orientation passes."""
        eo = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        self.assertTrue(
            is_valid_orientation(eo, EDGE_NUMBER, EDGE_VALID_ORIENTATIONS),
        )

    def test_invalid_corner_orientation_value(self) -> None:
        """Test that invalid corner orientation value fails."""
        co = [0, 1, 3, 0, 1, 2, 0, 1]  # 3 is invalid for corners
        self.assertFalse(
            is_valid_orientation(co, CORNER_NUMBER, CORNER_VALID_ORIENTATIONS),
        )

    def test_invalid_edge_orientation_value(self) -> None:
        """Test that invalid edge orientation value fails."""
        eo = [0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1]  # 2 is invalid for edges
        self.assertFalse(
            is_valid_orientation(eo, EDGE_NUMBER, EDGE_VALID_ORIENTATIONS),
        )

    def test_invalid_wrong_size(self) -> None:
        """Test that wrong size orientation fails."""
        co = [0, 1, 2, 0, 1]  # Only 5 elements, need 8
        self.assertFalse(
            is_valid_orientation(co, CORNER_NUMBER, CORNER_VALID_ORIENTATIONS),
        )

    def test_empty_orientation(self) -> None:
        """Test that empty orientation is valid for size 0."""
        self.assertTrue(is_valid_orientation([], 0, set()))
