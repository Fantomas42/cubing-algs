"""Tests for scrambler utility functions."""
import unittest

from cubing_algs.constants import CORNER_NAMES
from cubing_algs.constants import D_CORNERS
from cubing_algs.constants import D_EDGES
from cubing_algs.constants import E_EDGES
from cubing_algs.constants import EDGE_NAMES
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EP
from cubing_algs.constants import U_CORNERS
from cubing_algs.constants import U_EDGES
from cubing_algs.scrambler.utils import solve_to_algorithm
from cubing_algs.scrambler.utils import vcube_to_kociemba_string
from cubing_algs.vcube import VCube


class TestVCubeToKociemba(unittest.TestCase):
    """Tests for VCube to Kociemba conversion."""

    def test_solved_cube_conversion(self) -> None:
        """Test converting solved cube to Kociemba format."""
        cube = VCube()
        kociemba_str = vcube_to_kociemba_string(cube)

        # Solved cube should have 9 of each face color
        self.assertEqual(len(kociemba_str), 54)
        self.assertEqual(kociemba_str.count('U'), 9)
        self.assertEqual(kociemba_str.count('R'), 9)
        self.assertEqual(kociemba_str.count('F'), 9)
        self.assertEqual(kociemba_str.count('D'), 9)
        self.assertEqual(kociemba_str.count('L'), 9)
        self.assertEqual(kociemba_str.count('B'), 9)

    def test_scrambled_cube_conversion(self) -> None:
        """Test converting scrambled cube to Kociemba format."""
        cube = VCube()
        cube.rotate("R U R' U'")
        kociemba_str = vcube_to_kociemba_string(cube)

        # Should still have 54 characters and 9 of each color
        self.assertEqual(len(kociemba_str), 54)
        self.assertEqual(kociemba_str.count('U'), 9)
        self.assertEqual(kociemba_str.count('R'), 9)
        self.assertEqual(kociemba_str.count('F'), 9)
        self.assertEqual(kociemba_str.count('D'), 9)
        self.assertEqual(kociemba_str.count('L'), 9)
        self.assertEqual(kociemba_str.count('B'), 9)

    def test_non_3x3x3_cube_raises_error(self) -> None:
        """Test that non-3x3x3 cubes raise ValueError."""
        cube = VCube(size=2)
        with self.assertRaises(ValueError):
            vcube_to_kociemba_string(cube)


class TestSolveToAlgorithm(unittest.TestCase):
    """Tests for solve_to_algorithm function."""

    def test_solve_solved_cube(self) -> None:
        """Test solving an already solved cube."""
        solved_state = 'U' * 9 + 'R' * 9 + 'F' * 9 + 'D' * 9 + 'L' * 9 + 'B' * 9
        solution = solve_to_algorithm(solved_state)

        # Solved cube should return empty or very short solution
        self.assertIsInstance(solution, str)
        self.assertFalse(solution.strip())

    def test_solve_scrambled_cube(self) -> None:
        """Test solving a scrambled cube returns valid algorithm."""
        cube = VCube()
        cube.rotate("R U R' U'")
        kociemba_str = vcube_to_kociemba_string(cube)
        solution = solve_to_algorithm(kociemba_str)

        # Should return a non-empty string with moves
        self.assertIsInstance(solution, str)
        self.assertGreater(len(solution), 0)


class TestConstants(unittest.TestCase):
    """Tests for constant definitions."""

    def test_corner_names_length(self) -> None:
        """Test CORNER_NAMES has 8 entries."""
        self.assertEqual(len(CORNER_NAMES), 8)

    def test_edge_names_length(self) -> None:
        """Test EDGE_NAMES has 12 entries."""
        self.assertEqual(len(EDGE_NAMES), 12)

    def test_corner_names_unique(self) -> None:
        """Test CORNER_NAMES has no duplicates."""
        self.assertEqual(len(CORNER_NAMES), len(set(CORNER_NAMES)))

    def test_edge_names_unique(self) -> None:
        """Test EDGE_NAMES has no duplicates."""
        self.assertEqual(len(EDGE_NAMES), len(set(EDGE_NAMES)))

    def test_layer_groups_no_overlap_corners(self) -> None:
        """Test U and D corner groups don't overlap."""
        self.assertTrue(set(U_CORNERS).isdisjoint(set(D_CORNERS)))

    def test_layer_groups_cover_all_corners(self) -> None:
        """Test U and D groups cover all corners."""
        self.assertEqual(set(U_CORNERS) | set(D_CORNERS), set(SOLVED_CP))

    def test_layer_groups_no_overlap_edges(self) -> None:
        """Test U, D, and E edge groups don't overlap."""
        self.assertTrue(set(U_EDGES).isdisjoint(set(D_EDGES)))
        self.assertTrue(set(U_EDGES).isdisjoint(set(E_EDGES)))
        self.assertTrue(set(D_EDGES).isdisjoint(set(E_EDGES)))

    def test_layer_groups_cover_all_edges(self) -> None:
        """Test U, D, and E groups cover all edges."""
        self.assertEqual(
            set(U_EDGES) | set(D_EDGES) | set(E_EDGES),
            set(SOLVED_EP),
        )
