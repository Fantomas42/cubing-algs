"""Tests for binary mask operations."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.masks import compute_algorithm_mask
from cubing_algs.masks import intersection_masks
from cubing_algs.masks import negate_mask
from cubing_algs.masks import union_masks
from cubing_algs.solved_state import get_unique_facelets


class TestBinaryMasks(unittest.TestCase):
    """Tests for binary mask operations on cube states."""

    def test_union(self) -> None:
        """Test union."""
        self.assertEqual(union_masks('1010', '0110'), '1110')
        self.assertEqual(union_masks('1111', '0000'), '1111')
        self.assertEqual(union_masks('0000', '0000'), '0000')

    def test_union_multiple(self) -> None:
        """Test union multiple."""
        self.assertEqual(union_masks('1000', '0100', '0010', '0001'), '1111')
        self.assertEqual(union_masks('1010', '0101', '1100'), '1111')

    def test_union_single(self) -> None:
        """Test union single."""
        self.assertEqual(union_masks('1010'), '1010')

    def test_union_empty(self) -> None:
        """Test union empty."""
        self.assertEqual(union_masks(), '')

    def test_union_length_mismatch(self) -> None:
        """Test union raises ValueError on different length masks."""
        with self.assertRaises(ValueError):
            union_masks('1010', '101')

    def test_intersection(self) -> None:
        """Test intersection."""
        self.assertEqual(intersection_masks('1010', '1100'), '1000')
        self.assertEqual(intersection_masks('1111', '0000'), '0000')
        self.assertEqual(intersection_masks('1111', '1111'), '1111')

    def test_intersection_multiple(self) -> None:
        """Test intersection multiple."""
        self.assertEqual(intersection_masks('1111', '1110', '1100'), '1100')
        self.assertEqual(intersection_masks('1010', '0110', '1100'), '0000')

    def test_intersection_single(self) -> None:
        """Test intersection single."""
        self.assertEqual(intersection_masks('1010'), '1010')

    def test_intersection_empty(self) -> None:
        """Test intersection empty."""
        self.assertEqual(intersection_masks(), '')

    def test_intersection_length_mismatch(self) -> None:
        """Test intersection raises ValueError on different length masks."""
        with self.assertRaises(ValueError):
            intersection_masks('1010', '10100')

    def test_negate(self) -> None:
        """Test negate."""
        self.assertEqual(negate_mask('1010'), '0101')
        self.assertEqual(negate_mask('0000'), '1111')
        self.assertEqual(negate_mask('1111'), '0000')

    def test_negate_single_bit(self) -> None:
        """Test negate single bit."""
        self.assertEqual(negate_mask('1'), '0')
        self.assertEqual(negate_mask('0'), '1')

    def test_negate_empty(self) -> None:
        """Test negate empty."""
        self.assertEqual(negate_mask(''), '')


class TestComputeAlgorithmMask(unittest.TestCase):
    """Tests for compute_algorithm_mask."""

    def test_identity_algorithm(self) -> None:
        """Empty algorithm should produce all-zeros mask."""
        algo = Algorithm.parse_moves('')
        mask, state = compute_algorithm_mask(algo)

        self.assertEqual(mask, '0' * 54)
        self.assertEqual(state, get_unique_facelets(3))

    def test_single_move(self) -> None:
        """R move affects exactly 20 facelets."""
        algo = Algorithm.parse_moves('R')
        mask, _ = compute_algorithm_mask(algo)

        self.assertEqual(len(mask), 54)
        self.assertEqual(mask.count('1'), 20)

    def test_inverse_same_mask(self) -> None:
        """An algorithm and its inverse affect the same facelets."""
        algo = Algorithm.parse_moves("R U R' U'")
        algo_inv = Algorithm.parse_moves("U R U' R'")
        mask, _ = compute_algorithm_mask(algo)
        mask_inv, _ = compute_algorithm_mask(algo_inv)

        self.assertEqual(mask, mask_inv)

    def test_rotation_only(self) -> None:
        """Pure rotation should produce all-zeros mask."""
        algo = Algorithm.parse_moves('y')
        mask, _ = compute_algorithm_mask(algo)

        self.assertEqual(mask, '0' * 54)

    def test_rotation_with_move(self) -> None:
        """Rotation + move should only mark the move's facelets."""
        algo_bare = Algorithm.parse_moves('B')
        algo_rotated = Algorithm.parse_moves('y R')

        mask_bare, _ = compute_algorithm_mask(algo_bare)
        mask_rotated, _ = compute_algorithm_mask(algo_rotated)

        # y R is equivalent to B in solved-state coordinates
        self.assertEqual(mask_bare, mask_rotated)

    def test_mask_length_matches_cube_size(self) -> None:
        """Mask length equals 6 * size * size."""
        for size in (2, 3, 4):
            algo = Algorithm.parse_moves('R')
            mask, state = compute_algorithm_mask(algo, size=size)
            expected_length = 6 * size * size

            self.assertEqual(len(mask), expected_length)
            self.assertEqual(len(state), expected_length)

    def test_solved_algorithm_cycle(self) -> None:
        """Applying R4 returns to solved, mask should be all zeros."""
        algo = Algorithm.parse_moves('R R R R')
        mask, _ = compute_algorithm_mask(algo)

        self.assertEqual(mask, '0' * 54)

    def test_transformed_state_enables_permutation(self) -> None:
        """Transformed state can be used to compute permutations."""
        algo = Algorithm.parse_moves('R')
        mask, transformed_state = compute_algorithm_mask(algo)
        unique_facelets = get_unique_facelets(3)

        permutations: dict[int, int] = {}
        for pos in range(len(unique_facelets)):
            final = transformed_state.find(unique_facelets[pos])
            if final != pos:
                permutations[pos] = final

        # Every '1' in mask should have a permutation entry
        for i, bit in enumerate(mask):
            if bit == '1':
                self.assertIn(i, permutations)
            else:
                self.assertNotIn(i, permutations)

    def test_2x2x2_cube(self) -> None:
        """Mask works on 2x2x2 cubes."""
        algo = Algorithm.parse_moves('R')
        mask, _ = compute_algorithm_mask(algo, size=2)

        self.assertEqual(len(mask), 24)
        self.assertEqual(mask.count('1'), 12)

    def test_4x4x4_cube(self) -> None:
        """Mask works on 4x4x4 cubes."""
        algo = Algorithm.parse_moves('R')
        mask, _ = compute_algorithm_mask(algo, size=4)

        self.assertEqual(len(mask), 96)
        self.assertEqual(mask.count('1'), 32)

    def test_5x5x5_cube(self) -> None:
        """Mask works on 5x5x5 cubes."""
        algo = Algorithm.parse_moves('R')
        mask, _ = compute_algorithm_mask(algo, size=5)

        self.assertEqual(len(mask), 150)
        self.assertEqual(mask.count('1'), 44)

    def test_sexy_move(self) -> None:
        """Sexy move (R U R' U') affects a known number of facelets."""
        algo = Algorithm.parse_moves("R U R' U'")
        mask, _ = compute_algorithm_mask(algo)

        mobilized = mask.count('1')
        self.assertEqual(mobilized, 18)
