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
from cubing_algs.scrambler.pieces import derange_pieces
from cubing_algs.scrambler.pieces import disorient_corners
from cubing_algs.scrambler.pieces import disorient_edges
from cubing_algs.scrambler.pieces import orient_corners
from cubing_algs.scrambler.pieces import orient_edges
from cubing_algs.scrambler.pieces import random_corner_orientation
from cubing_algs.scrambler.pieces import random_edge_orientation


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
