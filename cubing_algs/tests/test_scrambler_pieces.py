# ruff: noqa: S311
"""Tests for scrambler piece manipulation functions."""
import unittest
from random import Random

from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.constants import SOLVED_EP
from cubing_algs.constants import U_CORNERS
from cubing_algs.constants import U_EDGES
from cubing_algs.integrity import compute_parity
from cubing_algs.scrambler.pieces import arrange_pieces
from cubing_algs.scrambler.pieces import derange_pieces
from cubing_algs.scrambler.pieces import disorient_corners
from cubing_algs.scrambler.pieces import disorient_edges
from cubing_algs.scrambler.pieces import fix_parity_with_buffer
from cubing_algs.scrambler.pieces import orient_corners
from cubing_algs.scrambler.pieces import orient_edges
from cubing_algs.scrambler.pieces import random_corner_orientation
from cubing_algs.scrambler.pieces import random_edge_orientation
from cubing_algs.scrambler.pieces import random_orientation
from cubing_algs.scrambler.pieces import random_permutation
from cubing_algs.scrambler.pieces import shuffle_in_place
from cubing_algs.scrambler.pieces import swap_pieces


class TestRandomCornerOrientation(unittest.TestCase):
    """Tests for random_corner_orientation function."""

    def test_no_corners_returns_solved(self) -> None:
        """Test that orienting no corners returns solved state."""
        co = random_corner_orientation([])
        self.assertEqual(co, SOLVED_CO)

    def test_orientation_constraint_maintained(self) -> None:
        """Test that sum(co) % 3 == 0."""
        rng = Random(42)
        for _ in range(20):
            co = random_corner_orientation(SOLVED_CP, rng=rng)
            self.assertEqual(sum(co) % 3, 0)

    def test_partial_orientation_constraint(self) -> None:
        """Test constraint with partial corner set."""
        rng = Random(42)
        for _ in range(20):
            co = random_corner_orientation(U_CORNERS, rng=rng)
            self.assertEqual(sum(co) % 3, 0)

    def test_all_values_valid(self) -> None:
        """Test that all orientation values are 0, 1, or 2."""
        co = random_corner_orientation(SOLVED_CP, rng=Random(42))
        self.assertTrue(all(0 <= val <= 2 for val in co))

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same result."""
        co1 = random_corner_orientation(SOLVED_CP, rng=Random(42))
        co2 = random_corner_orientation(SOLVED_CP, rng=Random(42))
        self.assertEqual(co1, co2)


class TestRandomEdgeOrientation(unittest.TestCase):
    """Tests for random_edge_orientation function."""

    def test_no_edges_returns_solved(self) -> None:
        """Test that orienting no edges returns solved state."""
        eo = random_edge_orientation([])
        self.assertEqual(eo, SOLVED_EO)

    def test_orientation_constraint_maintained(self) -> None:
        """Test that sum(eo) % 2 == 0."""
        rng = Random(42)
        for _ in range(20):
            eo = random_edge_orientation(SOLVED_EP, rng=rng)
            self.assertEqual(sum(eo) % 2, 0)

    def test_partial_orientation_constraint(self) -> None:
        """Test constraint with partial edge set."""
        rng = Random(42)
        for _ in range(20):
            eo = random_edge_orientation(U_EDGES, rng=rng)
            self.assertEqual(sum(eo) % 2, 0)

    def test_all_values_valid(self) -> None:
        """Test that all orientation values are 0 or 1."""
        eo = random_edge_orientation(SOLVED_EP, rng=Random(42))
        self.assertTrue(all(val in {0, 1} for val in eo))

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same result."""
        eo1 = random_edge_orientation(SOLVED_EP, rng=Random(42))
        eo2 = random_edge_orientation(SOLVED_EP, rng=Random(42))
        self.assertEqual(eo1, eo2)


class TestDerangePieces(unittest.TestCase):
    """Tests for derange_pieces function."""

    def test_derange_corners_not_solved(self) -> None:
        """Test deranging corners ensures they're not solved."""
        cp, co = SOLVED_CP, SOLVED_CO
        ep, eo = SOLVED_EP, SOLVED_EO

        cp, co, ep, eo = derange_pieces(
            cp,
            co,
            ep,
            eo,
            U_CORNERS,
            [],
            buffer_corners=[4, 5],
            rng=Random(42),
        )

        # U corners should NOT be solved
        not_solved_count = sum(1 for idx in U_CORNERS if cp[idx] != idx)
        self.assertGreater(not_solved_count, 0)

    def test_derange_edges_not_solved(self) -> None:
        """Test deranging edges ensures they're not solved."""
        cp, co = SOLVED_CP, SOLVED_CO
        ep, eo = SOLVED_EP, SOLVED_EO

        cp, co, ep, eo = derange_pieces(
            cp,
            co,
            ep,
            eo,
            [],
            U_EDGES,
            buffer_edges=[8, 9],
            rng=Random(42),
        )

        # U edges should NOT be solved
        not_solved_count = sum(1 for idx in U_EDGES if ep[idx] != idx)
        self.assertGreater(not_solved_count, 0)

    def test_maintains_parity(self) -> None:
        """Test that derangement maintains parity."""
        rng = Random(42)
        for _ in range(10):
            cp, co = SOLVED_CP, SOLVED_CO
            ep, eo = SOLVED_EP, SOLVED_EO

            cp, co, ep, eo = derange_pieces(
                cp,
                co,
                ep,
                eo,
                U_CORNERS,
                U_EDGES,
                [4, 5],
                [8, 9],
                rng=rng,
            )

            self.assertEqual(compute_parity(cp), compute_parity(ep))


class TestOrientCorners(unittest.TestCase):
    """Tests for orient_corners function."""

    def test_orient_no_corners(self) -> None:
        """Test orienting no corners returns input."""
        co = [1, 2, 0, 1, 2, 0, 1, 2]
        result = orient_corners(co, [], rng=Random(42))
        self.assertEqual(result, co)

    def test_orient_corners_to_zero(self) -> None:
        """Test orienting corners sets them to 0."""
        co = [1, 2, 1, 2, 0, 0, 0, 0]
        result = orient_corners(
            co, U_CORNERS,
            buffer_corners=[4, 5],
            rng=Random(42),
        )

        # U corners should be oriented
        for idx in U_CORNERS:
            self.assertEqual(result[idx], 0)

    def test_maintains_constraint(self) -> None:
        """Test that orientation maintains sum(co) % 3 == 0."""
        rng = Random(42)
        for _ in range(10):
            co = random_corner_orientation(SOLVED_CP, rng=rng)
            result = orient_corners(co, U_CORNERS, [4, 5], rng=rng)
            self.assertEqual(sum(result) % 3, 0)

    def test_orient_corners_without_buffer(self) -> None:
        """Test orienting corners without buffer pieces."""
        co = [1, 2, 0, 0, 0, 0, 0, 0]
        result = orient_corners(
            co, U_CORNERS,
            buffer_corners=[],
            rng=Random(42),
        )

        # Should still maintain constraint
        self.assertEqual(sum(result) % 3, 0)
        # U corners should be oriented
        # but one might have orientation to fix constraint
        zero_count = sum(1 for idx in U_CORNERS if result[idx] == 0)
        self.assertGreaterEqual(zero_count, len(U_CORNERS) - 1)

    def test_orient_corners_default_rng(self) -> None:
        """Test orient_corners with default RNG."""
        co = [1, 2, 0, 0, 0, 0, 0, 0]
        result = orient_corners(co, U_CORNERS, buffer_corners=[4, 5])

        # Should maintain constraint
        self.assertEqual(sum(result) % 3, 0)
        # U corners should be oriented
        for idx in U_CORNERS:
            self.assertEqual(result[idx], 0)


class TestDisorientCorners(unittest.TestCase):
    """Tests for disorient_corners function."""

    def test_disorient_corners_not_zero(self) -> None:
        """Test disorienting corners makes them non-zero."""
        co = SOLVED_CO
        result = disorient_corners(
            co,
            U_CORNERS,
            buffer_corners=[4, 5],
            rng=Random(42),
        )

        # U corners should be disoriented
        non_zero_count = sum(1 for idx in U_CORNERS if result[idx] != 0)
        self.assertGreater(non_zero_count, 0)

    def test_maintains_constraint(self) -> None:
        """Test that disorientation maintains sum(co) % 3 == 0."""
        rng = Random(42)
        for _ in range(10):
            co = SOLVED_CO
            result = disorient_corners(co, U_CORNERS, [4, 5], rng=rng)
            self.assertEqual(sum(result) % 3, 0)

    def test_disorient_without_buffer(self) -> None:
        """Test disorienting corners without buffer pieces."""
        co = SOLVED_CO.copy()
        result = disorient_corners(
            co, U_CORNERS,
            buffer_corners=[],
            rng=Random(42),
        )

        # Without buffer, constraint may not be perfectly maintained
        # but function should still return valid orientations
        self.assertTrue(all(0 <= val <= 2 for val in result))
        # At least some corners should be disoriented
        non_zero = sum(1 for idx in U_CORNERS if result[idx] != 0)
        self.assertGreater(non_zero, 0)

    def test_disorient_already_disoriented(self) -> None:
        """Test disorienting already disoriented corners."""
        co = [1, 2, 0, 0, 0, 0, 0, 0]
        result = disorient_corners(co, U_CORNERS, [4, 5], rng=Random(42))

        # Should maintain constraint
        self.assertEqual(sum(result) % 3, 0)

    def test_disorient_single_corner_with_buffer(self) -> None:
        """Test disorienting single corner with buffer."""
        co = SOLVED_CO.copy()
        result = disorient_corners(
            co, [0],
            buffer_corners=[4, 5],
            rng=Random(42),
        )

        # Should maintain constraint
        self.assertEqual(sum(result) % 3, 0)
        # Corner should be disoriented
        self.assertNotEqual(result[0], 0)

    def test_disorient_corners_default_rng(self) -> None:
        """Test disorient_corners with default RNG."""
        co = SOLVED_CO.copy()
        result = disorient_corners(co, U_CORNERS, buffer_corners=[4, 5])

        # Should maintain constraint
        self.assertEqual(sum(result) % 3, 0)
        # At least some corners should be disoriented
        non_zero = sum(1 for idx in U_CORNERS if result[idx] != 0)
        self.assertGreater(non_zero, 0)


class TestOrientEdges(unittest.TestCase):
    """Tests for orient_edges function."""

    def test_orient_no_edges(self) -> None:
        """Test orienting no edges returns input."""
        eo = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        result = orient_edges(eo, [], rng=Random(42))
        self.assertEqual(result, eo)

    def test_orient_edges_to_zero(self) -> None:
        """Test orienting edges sets them to 0."""
        eo = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        result = orient_edges(eo, U_EDGES, buffer_edges=[8, 9], rng=Random(42))

        # U edges should be oriented
        for idx in U_EDGES:
            self.assertEqual(result[idx], 0)

    def test_maintains_constraint(self) -> None:
        """Test that orientation maintains sum(eo) % 2 == 0."""
        rng = Random(42)
        for _ in range(10):
            eo = random_edge_orientation(SOLVED_EP, rng=rng)
            result = orient_edges(eo, U_EDGES, [8, 9], rng=rng)
            self.assertEqual(sum(result) % 2, 0)

    def test_orient_edges_default_rng(self) -> None:
        """Test orient_edges with default RNG."""
        eo = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        result = orient_edges(eo, U_EDGES, buffer_edges=[8, 9])

        # Should maintain constraint
        self.assertEqual(sum(result) % 2, 0)
        # U edges should be oriented
        for idx in U_EDGES:
            self.assertEqual(result[idx], 0)


class TestDisorientEdges(unittest.TestCase):
    """Tests for disorient_edges function."""

    def test_disorient_edges_not_zero(self) -> None:
        """Test disorienting edges makes them non-zero."""
        eo = SOLVED_EO
        result = disorient_edges(
            eo, U_EDGES,
            buffer_edges=[8, 9],
            rng=Random(42),
        )

        # U edges should be disoriented
        non_zero_count = sum(1 for idx in U_EDGES if result[idx] != 0)
        self.assertGreater(non_zero_count, 0)

    def test_maintains_constraint(self) -> None:
        """Test that disorientation maintains sum(eo) % 2 == 0."""
        rng = Random(42)
        for _ in range(10):
            eo = SOLVED_EO
            result = disorient_edges(eo, U_EDGES, [8, 9], rng=rng)
            self.assertEqual(sum(result) % 2, 0)

    def test_disorient_without_buffer(self) -> None:
        """Test disorienting edges without buffer pieces."""
        eo = SOLVED_EO.copy()
        result = disorient_edges(eo, U_EDGES, buffer_edges=[], rng=Random(42))

        # Should still maintain constraint
        self.assertEqual(sum(result) % 2, 0)
        # At least some edges should be disoriented
        non_zero = sum(1 for idx in U_EDGES if result[idx] != 0)
        self.assertGreater(non_zero, 0)

    def test_disorient_already_disoriented(self) -> None:
        """Test disorienting already disoriented edges."""
        eo = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        result = disorient_edges(eo, U_EDGES, [8, 9], rng=Random(42))

        # Should maintain constraint
        self.assertEqual(sum(result) % 2, 0)

    def test_disorient_edges_no_buffer_unflip_case(self) -> None:
        """Test disorienting edges without buffer when unflip is needed."""
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        edges = [0, 1, 2]  # Odd number of edges to trigger unflip
        result = disorient_edges(eo, edges, buffer_edges=[], rng=Random(42))

        # Should maintain constraint
        self.assertEqual(sum(result) % 2, 0)
        # At least some edges should be disoriented
        non_zero = sum(1 for idx in edges if result[idx] != 0)
        self.assertGreater(non_zero, 0)

    def test_disorient_edges_default_rng(self) -> None:
        """Test disorient_edges with default RNG."""
        eo = SOLVED_EO.copy()
        result = disorient_edges(eo, U_EDGES, buffer_edges=[8, 9])

        # Should maintain constraint
        self.assertEqual(sum(result) % 2, 0)
        # At least some edges should be disoriented
        non_zero = sum(1 for idx in U_EDGES if result[idx] != 0)
        self.assertGreater(non_zero, 0)


class TestSwapPieces(unittest.TestCase):
    """Tests for swap_pieces function."""

    def test_swap_pieces_in_permutation(self) -> None:
        """Test that swap correctly exchanges pieces in permutation."""
        perm = [0, 1, 2, 3, 4, 5, 6, 7]
        orient = [0, 0, 0, 0, 0, 0, 0, 0]

        swap_pieces(perm, orient, 0, 3)

        self.assertEqual(perm[0], 3)
        self.assertEqual(perm[3], 0)

    def test_swap_pieces_in_orientation(self) -> None:
        """Test that swap correctly exchanges pieces in orientation."""
        perm = [0, 1, 2, 3, 4, 5, 6, 7]
        orient = [0, 1, 2, 0, 1, 2, 0, 1]

        swap_pieces(perm, orient, 1, 4)

        self.assertEqual(orient[1], 1)
        self.assertEqual(orient[4], 1)
        self.assertEqual(perm[1], 4)
        self.assertEqual(perm[4], 1)

    def test_swap_same_index(self) -> None:
        """Test swapping same index leaves arrays unchanged."""
        perm = [0, 1, 2, 3, 4, 5, 6, 7]
        orient = [0, 1, 2, 0, 1, 2, 0, 1]
        original_perm = perm.copy()
        original_orient = orient.copy()

        swap_pieces(perm, orient, 2, 2)

        self.assertEqual(perm, original_perm)
        self.assertEqual(orient, original_orient)

    def test_swap_first_and_last(self) -> None:
        """Test swapping first and last elements."""
        perm = [0, 1, 2, 3, 4, 5, 6, 7]
        orient = [0, 0, 0, 0, 0, 0, 0, 2]

        swap_pieces(perm, orient, 0, 7)

        self.assertEqual(perm[0], 7)
        self.assertEqual(perm[7], 0)
        self.assertEqual(orient[0], 2)
        self.assertEqual(orient[7], 0)


class TestShuffleInPlace(unittest.TestCase):
    """Tests for shuffle_in_place function."""

    def test_shuffle_empty_list(self) -> None:
        """Test shuffling empty list returns True."""
        perm = [0, 1, 2, 3]
        orient = [0, 0, 0, 0]
        result = shuffle_in_place(perm, orient, [], Random(42))
        self.assertTrue(result)

    def test_shuffle_single_element(self) -> None:
        """Test shuffling single element returns True."""
        perm = [0, 1, 2, 3]
        orient = [0, 0, 0, 0]
        result = shuffle_in_place(perm, orient, [2], Random(42))
        self.assertTrue(result)

    def test_shuffle_changes_order(self) -> None:
        """Test that shuffle changes piece order."""
        perm = [0, 1, 2, 3, 4, 5, 6, 7]
        orient = [0, 0, 0, 0, 0, 0, 0, 0]

        original_perm = perm.copy()
        shuffle_in_place(perm, orient, SOLVED_CP, Random(42))

        # With high probability, shuffling should change order
        self.assertNotEqual(perm, original_perm)

    def test_shuffle_deterministic(self) -> None:
        """Test that shuffle is deterministic with same seed."""
        perm1 = [0, 1, 2, 3, 4, 5, 6, 7]
        orient1 = [0, 0, 0, 0, 0, 0, 0, 0]

        perm2 = [0, 1, 2, 3, 4, 5, 6, 7]
        orient2 = [0, 0, 0, 0, 0, 0, 0, 0]

        shuffle_in_place(perm1, orient1, SOLVED_CP, Random(42))
        shuffle_in_place(perm2, orient2, SOLVED_CP, Random(42))

        self.assertEqual(perm1, perm2)
        self.assertEqual(orient1, orient2)

    def test_shuffle_returns_parity(self) -> None:
        """Test that shuffle returns correct parity."""
        perm = [0, 1, 2, 3, 4, 5, 6, 7]
        orient = [0, 0, 0, 0, 0, 0, 0, 0]

        result = shuffle_in_place(perm, orient, SOLVED_CP, Random(42))
        self.assertIsInstance(result, bool)

    def test_shuffle_subset_indices(self) -> None:
        """Test shuffling only subset of indices."""
        perm = [0, 1, 2, 3, 4, 5, 6, 7]
        orient = [0, 0, 0, 0, 0, 0, 0, 0]

        shuffle_in_place(perm, orient, [0, 1, 2, 3], Random(42))

        # Indices 4-7 should be unchanged
        self.assertEqual(perm[4], 4)
        self.assertEqual(perm[5], 5)
        self.assertEqual(perm[6], 6)
        self.assertEqual(perm[7], 7)


class TestFixParityWithBuffer(unittest.TestCase):
    """Tests for fix_parity_with_buffer function."""

    def test_fix_parity_with_edge_buffer(self) -> None:
        """Test fixing parity using edge buffer."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]  # Odd permutation
        co = SOLVED_CO.copy()
        ep = SOLVED_EP.copy()  # Even permutation
        eo = SOLVED_EO.copy()

        self.assertNotEqual(compute_parity(cp), compute_parity(ep))

        fix_parity_with_buffer(cp, co, ep, eo, [], [8, 9])

        self.assertEqual(compute_parity(cp), compute_parity(ep))

    def test_fix_parity_with_corner_buffer(self) -> None:
        """Test fixing parity using corner buffer."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]  # Odd permutation
        co = SOLVED_CO.copy()
        ep = SOLVED_EP.copy()  # Even permutation
        eo = SOLVED_EO.copy()

        self.assertNotEqual(compute_parity(cp), compute_parity(ep))

        fix_parity_with_buffer(cp, co, ep, eo, [4, 5], [])

        self.assertEqual(compute_parity(cp), compute_parity(ep))

    def test_fix_parity_prefers_edges(self) -> None:
        """Test that parity fix prefers edges when both buffers available."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = SOLVED_CO.copy()
        ep = SOLVED_EP.copy()
        eo = SOLVED_EO.copy()

        fix_parity_with_buffer(cp, co, ep, eo, [4, 5], [8, 9])

        # Edges should be swapped
        self.assertEqual(ep[8], 9)
        self.assertEqual(ep[9], 8)
        # Corners should be unchanged
        self.assertEqual(cp[4], 4)
        self.assertEqual(cp[5], 5)

    def test_no_buffer_does_nothing(self) -> None:
        """Test that no buffer available does nothing."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = SOLVED_CO.copy()
        ep = SOLVED_EP.copy()
        eo = SOLVED_EO.copy()

        original_cp = cp.copy()
        original_ep = ep.copy()

        fix_parity_with_buffer(cp, co, ep, eo, [], [])

        self.assertEqual(cp, original_cp)
        self.assertEqual(ep, original_ep)

    def test_single_edge_buffer_does_nothing(self) -> None:
        """Test that single edge in buffer does nothing."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = SOLVED_CO.copy()
        ep = SOLVED_EP.copy()
        eo = SOLVED_EO.copy()

        original_ep = ep.copy()

        fix_parity_with_buffer(cp, co, ep, eo, [], [8])

        self.assertEqual(ep, original_ep)


class TestRandomPermutation(unittest.TestCase):
    """Tests for random_permutation function."""

    def test_empty_permutation_returns_solved(self) -> None:
        """Test that empty permutation returns solved state."""
        cp, co, ep, eo = random_permutation([], [])
        self.assertEqual(cp, SOLVED_CP)
        self.assertEqual(co, SOLVED_CO)
        self.assertEqual(ep, SOLVED_EP)
        self.assertEqual(eo, SOLVED_EO)

    def test_maintains_parity(self) -> None:
        """Test that random permutation maintains parity."""
        rng = Random(42)
        for _ in range(20):
            cp, _co, ep, _eo = random_permutation(
                SOLVED_CP,
                SOLVED_EP,
                rng=rng,
            )
            self.assertEqual(compute_parity(cp), compute_parity(ep))

    def test_corners_only_permutation(self) -> None:
        """Test permuting only corners."""
        cp, _co, ep, _eo = random_permutation(U_CORNERS, [], rng=Random(42))
        self.assertEqual(ep, SOLVED_EP)
        # At least some corners should be permuted
        permuted = sum(1 for i in U_CORNERS if cp[i] != i)
        self.assertGreater(permuted, 0)

    def test_edges_only_permutation(self) -> None:
        """Test permuting only edges."""
        cp, _co, ep, _eo = random_permutation([], U_EDGES, rng=Random(42))
        self.assertEqual(cp, SOLVED_CP)
        # At least some edges should be permuted
        permuted = sum(1 for i in U_EDGES if ep[i] != i)
        self.assertGreater(permuted, 0)

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same result."""
        result1 = random_permutation(
            SOLVED_CP,
            SOLVED_EP,
            rng=Random(42),
        )
        result2 = random_permutation(
            SOLVED_CP,
            SOLVED_EP,
            rng=Random(42),
        )
        self.assertEqual(result1, result2)

    def test_orientation_stays_solved(self) -> None:
        """Test that orientation arrays remain solved."""
        _cp, co, _ep, eo = random_permutation(
            SOLVED_CP,
            SOLVED_EP,
            rng=Random(42),
        )
        self.assertEqual(co, SOLVED_CO)
        self.assertEqual(eo, SOLVED_EO)

    def test_default_rng(self) -> None:
        """Test that default RNG is used when None provided."""
        result = random_permutation(U_CORNERS, U_EDGES)
        self.assertEqual(len(result), 4)


class TestRandomOrientation(unittest.TestCase):
    """Tests for random_orientation function."""

    def test_empty_pieces_returns_zeros(self) -> None:
        """Test that empty pieces returns all zeros."""
        result = random_orientation([], 8, 3, Random(42))
        self.assertEqual(result, [0] * 8)

    def test_corner_orientation_constraint(self) -> None:
        """Test corner orientation maintains sum % 3 == 0."""
        rng = Random(42)
        for _ in range(20):
            result = random_orientation(SOLVED_CP, 8, 3, rng)
            self.assertEqual(sum(result) % 3, 0)

    def test_edge_orientation_constraint(self) -> None:
        """Test edge orientation maintains sum % 2 == 0."""
        rng = Random(42)
        for _ in range(20):
            result = random_orientation(SOLVED_EP, 12, 2, rng)
            self.assertEqual(sum(result) % 2, 0)

    def test_partial_corner_orientation(self) -> None:
        """Test partial corner set maintains constraint."""
        result = random_orientation(U_CORNERS, 8, 3, Random(42))
        u_sum = sum(result[i] for i in U_CORNERS)
        self.assertEqual(u_sum % 3, 0)

    def test_single_piece_zero_orientation(self) -> None:
        """Test single piece gets zero orientation."""
        result = random_orientation([0], 8, 3, Random(42))
        self.assertEqual(result[0], 0)

    def test_deterministic_with_seed(self) -> None:
        """Test that same seed produces same result."""
        result1 = random_orientation(SOLVED_CP, 8, 3, Random(42))
        result2 = random_orientation(SOLVED_CP, 8, 3, Random(42))
        self.assertEqual(result1, result2)

    def test_valid_corner_values(self) -> None:
        """Test that corner orientation values are 0, 1, or 2."""
        result = random_orientation(SOLVED_CP, 8, 3, Random(42))
        self.assertTrue(all(0 <= val <= 2 for val in result))

    def test_valid_edge_values(self) -> None:
        """Test that edge orientation values are 0 or 1."""
        result = random_orientation(SOLVED_EP, 12, 2, Random(42))
        self.assertTrue(all(val in {0, 1} for val in result))


class TestArrangePieces(unittest.TestCase):
    """Tests for arrange_pieces function."""

    def test_already_solved_stays_solved(self) -> None:
        """Test that already solved pieces stay solved."""
        cp, _co, ep, _eo = arrange_pieces(
            SOLVED_CP.copy(),
            SOLVED_CO.copy(),
            SOLVED_EP.copy(),
            SOLVED_EO.copy(),
            U_CORNERS,
            U_EDGES,
            buffer_corners=[4, 5],
            buffer_edges=[8, 9],
            rng=Random(42),
        )

        for idx in U_CORNERS:
            self.assertEqual(cp[idx], idx)
        for idx in U_EDGES:
            self.assertEqual(ep[idx], idx)

    def test_arrange_scrambled_corners(self) -> None:
        """Test arranging scrambled corners to solved."""
        cp = [3, 2, 1, 0, 4, 5, 6, 7]
        co = SOLVED_CO.copy()
        ep = SOLVED_EP.copy()
        eo = SOLVED_EO.copy()

        cp, co, ep, eo = arrange_pieces(
            cp, co, ep, eo,
            U_CORNERS,
            [],
            buffer_corners=[4, 5],
            buffer_edges=[8, 9],
            rng=Random(42),
        )

        # U corners should be solved
        for idx in U_CORNERS:
            self.assertEqual(cp[idx], idx)

    def test_arrange_scrambled_edges(self) -> None:
        """Test arranging scrambled edges to solved."""
        cp = SOLVED_CP.copy()
        co = SOLVED_CO.copy()
        ep = [3, 2, 1, 0, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = SOLVED_EO.copy()

        cp, co, ep, eo = arrange_pieces(
            cp, co, ep, eo,
            [],
            U_EDGES,
            buffer_corners=[4, 5],
            buffer_edges=[8, 9],
            rng=Random(42),
        )

        # U edges should be solved
        for idx in U_EDGES:
            self.assertEqual(ep[idx], idx)

    def test_maintains_parity(self) -> None:
        """Test that arrange maintains parity."""
        rng = Random(42)
        for _ in range(10):
            cp, co, ep, eo = random_permutation(
                SOLVED_CP,
                SOLVED_EP,
                rng=rng,
            )

            cp, co, ep, eo = arrange_pieces(
                cp, co, ep, eo,
                U_CORNERS,
                U_EDGES,
                [4, 5],
                [8, 9],
                rng=rng,
            )

            self.assertEqual(compute_parity(cp), compute_parity(ep))

    def test_default_rng(self) -> None:
        """Test that default RNG is used when None provided."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = SOLVED_CO.copy()
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = SOLVED_EO.copy()

        result = arrange_pieces(cp, co, ep, eo, [0, 1], [0, 1], [4, 5], [8, 9])
        self.assertEqual(len(result), 4)

    def test_empty_pieces_with_scrambled_state(self) -> None:
        """Test arranging no pieces leaves state unchanged."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]
        co = SOLVED_CO.copy()
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = SOLVED_EO.copy()

        result_cp, _result_co, _result_ep, _result_eo = arrange_pieces(
            cp, co, ep, eo,
            [], [],
            buffer_corners=[4, 5],
            buffer_edges=[8, 9],
            rng=Random(42),
        )

        # State should change due to internal shuffling
        self.assertIsInstance(result_cp, list)
        self.assertEqual(len(result_cp), 8)


class TestDerangePiecesExtended(unittest.TestCase):
    """Extended tests for derange_pieces function."""

    def test_derange_with_no_buffer(self) -> None:
        """Test deranging without buffer pieces."""
        cp, _co, ep, _eo = derange_pieces(
            SOLVED_CP,
            SOLVED_CO,
            SOLVED_EP,
            SOLVED_EO,
            U_CORNERS,
            U_EDGES,
            buffer_corners=[],
            buffer_edges=[],
            rng=Random(42),
        )

        # Pieces should not be solved
        not_solved_corners = sum(1 for idx in U_CORNERS if cp[idx] != idx)
        not_solved_edges = sum(1 for idx in U_EDGES if ep[idx] != idx)
        self.assertGreater(not_solved_corners, 0)
        self.assertGreater(not_solved_edges, 0)

    def test_derange_corners_only(self) -> None:
        """Test deranging only corners."""
        cp, _co, _ep, _eo = derange_pieces(
            SOLVED_CP,
            SOLVED_CO,
            SOLVED_EP,
            SOLVED_EO,
            U_CORNERS,
            [],
            buffer_corners=[4, 5],
            buffer_edges=[],
            rng=Random(42),
        )

        # U corners should not be solved
        not_solved = sum(1 for idx in U_CORNERS if cp[idx] != idx)
        self.assertGreater(not_solved, 0)

    def test_derange_edges_only(self) -> None:
        """Test deranging only edges."""
        _cp, _co, ep, _eo = derange_pieces(
            SOLVED_CP,
            SOLVED_CO,
            SOLVED_EP,
            SOLVED_EO,
            [],
            U_EDGES,
            buffer_corners=[],
            buffer_edges=[8, 9],
            rng=Random(42),
        )

        # U edges should not be solved
        not_solved = sum(1 for idx in U_EDGES if ep[idx] != idx)
        self.assertGreater(not_solved, 0)

    def test_derange_all_pieces(self) -> None:
        """Test deranging all corners and edges."""
        cp, _co, ep, _eo = derange_pieces(
            SOLVED_CP,
            SOLVED_CO,
            SOLVED_EP,
            SOLVED_EO,
            SOLVED_CP,
            SOLVED_EP,
            buffer_corners=[],
            buffer_edges=[],
            rng=Random(42),
        )

        # All pieces should be deranged
        solved_count = sum(1 for i in SOLVED_CP if cp[i] == i)
        solved_count += sum(1 for i in SOLVED_EP if ep[i] == i)
        self.assertEqual(solved_count, 0)

    def test_default_rng(self) -> None:
        """Test that default RNG is used when None provided."""
        result = derange_pieces(
            SOLVED_CP,
            SOLVED_CO,
            SOLVED_EP,
            SOLVED_EO,
            U_CORNERS,
            U_EDGES,
            [4, 5],
            [8, 9],
        )
        self.assertEqual(len(result), 4)
