"""Tests for integrity module."""
import unittest

from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EP
from cubing_algs.integrity import compute_parity


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


if __name__ == '__main__':
    unittest.main()
