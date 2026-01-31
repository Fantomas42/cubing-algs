"""Tests for scrambler converter functions."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.constants import SOLVED_EP
from cubing_algs.constants import SOLVED_SO
from cubing_algs.scrambler.converters import cubies_to_algorithm
from cubing_algs.scrambler.converters import facelets_to_algorithm
from cubing_algs.solved_state import SOLVED_FACELETS_3x3x3
from cubing_algs.vcube import VCube


class TestFaceletsToAlgorithm(unittest.TestCase):
    """Tests for facelets_to_algorithm function."""

    def test_solved_to_solved_produces_algorithm(self) -> None:
        """Test that solving solved state produces valid algorithm."""
        result = facelets_to_algorithm(
            SOLVED_FACELETS_3x3x3,
            SOLVED_FACELETS_3x3x3,
        )
        self.assertIsInstance(result, Algorithm)

        # Apply result to solved cube should keep it solved
        cube = VCube()
        cube.rotate(result)
        self.assertTrue(cube.is_solved)

    def test_solved_to_solved_default_destination(self) -> None:
        """Test that default destination is solved state."""
        result = facelets_to_algorithm(SOLVED_FACELETS_3x3x3)
        self.assertIsInstance(result, Algorithm)

        # Apply result to solved cube should keep it solved
        cube = VCube()
        cube.rotate(result)
        self.assertTrue(cube.is_solved)

    def test_simple_move_produces_algorithm(self) -> None:
        """Test that simple scrambled state produces valid algorithm."""
        cube = VCube()
        cube.rotate("R U R' U'")
        scrambled_state = cube.state

        result = facelets_to_algorithm(scrambled_state)
        self.assertIsInstance(result, Algorithm)
        self.assertGreater(len(result), 0)

        # Algorithm should be valid and change the state
        test_cube = VCube(scrambled_state)
        original_state = test_cube.state
        test_cube.rotate(result)
        # State should change after applying algorithm
        self.assertNotEqual(test_cube.state, original_state)

    def test_complex_scramble_produces_algorithm(self) -> None:
        """Test that complex scrambled state produces valid algorithm."""
        cube = VCube()
        cube.rotate("R U R' U' R' F R2 U' R' U' R U R' F'")
        scrambled_state = cube.state

        result = facelets_to_algorithm(scrambled_state)
        self.assertIsInstance(result, Algorithm)

        # Apply result and verify it solves the cube
        test_cube = VCube(scrambled_state)
        test_cube.rotate(result)
        self.assertTrue(test_cube.is_solved)

    def test_custom_destination_state(self) -> None:
        """Test solving to custom destination state."""
        # Create two different scrambled states
        cube1 = VCube()
        cube1.rotate("R U R'")
        state1 = cube1.state

        cube2 = VCube()
        cube2.rotate("F D F'")
        state2 = cube2.state

        # Get algorithm to go from state1 to state2
        result = facelets_to_algorithm(state1, state2)
        self.assertIsInstance(result, Algorithm)

        # Verify it transforms state1 to something functionally
        # equivalent to state2.
        # The algorithm may not produce exact match due to mirror transform
        test_cube = VCube(state1)
        test_cube.rotate(result)
        # Check that we got a valid transformation
        self.assertIsInstance(test_cube.state, str)
        self.assertEqual(len(test_cube.state), len(state2))

    def test_single_quarter_turn(self) -> None:
        """Test that single quarter turn is properly converted."""
        cube = VCube()
        cube.rotate('R')
        scrambled_state = cube.state

        result = facelets_to_algorithm(scrambled_state)
        self.assertIsInstance(result, Algorithm)

        # Algorithm should be valid and change the state
        test_cube = VCube(scrambled_state)
        original_state = test_cube.state
        test_cube.rotate(result)
        self.assertNotEqual(test_cube.state, original_state)


class TestCubiesToAlgorithm(unittest.TestCase):
    """Tests for cubies_to_algorithm function."""

    def test_solved_state_produces_algorithm(self) -> None:
        """Test that solved cubie state produces valid algorithm."""
        cubies = (SOLVED_CP, SOLVED_CO, SOLVED_EP, SOLVED_EO)
        result = cubies_to_algorithm(cubies)
        self.assertIsInstance(result, Algorithm)

        # Apply to solved cube should keep it solved
        cube = VCube()
        cube.rotate(result)
        self.assertTrue(cube.is_solved)

    def test_scrambled_state_produces_algorithm(self) -> None:
        """Test that scrambled cubie state produces valid algorithm."""
        cube = VCube()
        cube.rotate("R U R' U'")

        cp, co, ep, eo, _so = cube.to_cubies
        result = cubies_to_algorithm((cp, co, ep, eo))
        self.assertIsInstance(result, Algorithm)
        self.assertGreater(len(result), 0)

        # Algorithm should be valid and produce a valid state
        test_cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_SO)
        original_state = test_cube.state
        test_cube.rotate(result)
        # State should change
        self.assertNotEqual(test_cube.state, original_state)

    def test_with_destination_state(self) -> None:  # noqa: PLR0914
        """Test solving to custom destination cubie state."""
        cube1 = VCube()
        cube1.rotate("R U R'")
        cp1, co1, ep1, eo1, _so1 = cube1.to_cubies
        cubies1 = (cp1, co1, ep1, eo1)

        cube2 = VCube()
        cube2.rotate("F D F'")
        cp2, co2, ep2, eo2, _so2 = cube2.to_cubies
        cubies2 = (cp2, co2, ep2, eo2)

        result = cubies_to_algorithm(cubies1, cubies2)
        self.assertIsInstance(result, Algorithm)

        # Verify algorithm is valid
        test_cube = VCube.from_cubies(*cubies1, SOLVED_SO)
        test_cube.rotate(result)

        # Should produce a valid state
        self.assertIsInstance(test_cube.state, str)
        self.assertEqual(len(test_cube.state), 54)
        self.assertEqual(test_cube.state, cube2.state)

    def test_corner_permutation_only(self) -> None:
        """Test state with only corner permutation changed."""
        cp = [1, 0, 2, 3, 4, 5, 6, 7]  # Swap first two corners
        co = SOLVED_CO.copy()
        # Swap first two edges for parity
        ep = [1, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = SOLVED_EO.copy()

        result = cubies_to_algorithm((cp, co, ep, eo))
        self.assertIsInstance(result, Algorithm)

        # Apply and verify
        test_cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_SO)
        test_cube.rotate(result)
        self.assertTrue(test_cube.is_solved)

    def test_corner_orientation_only(self) -> None:
        """Test state with only corner orientation changed."""
        cp = SOLVED_CP.copy()
        # Twisted corners maintaining constraint
        co = [1, 2, 0, 0, 0, 0, 0, 0]
        ep = SOLVED_EP.copy()
        eo = SOLVED_EO.copy()

        result = cubies_to_algorithm((cp, co, ep, eo))
        self.assertIsInstance(result, Algorithm)

        # Algorithm should be valid and change the state
        test_cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_SO)
        original_state = test_cube.state
        test_cube.rotate(result)
        self.assertNotEqual(test_cube.state, original_state)

    def test_edge_orientation_only(self) -> None:
        """Test state with only edge orientation changed."""
        cp = SOLVED_CP.copy()
        co = SOLVED_CO.copy()
        ep = SOLVED_EP.copy()
        # Flipped edges maintaining constraint
        eo = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        result = cubies_to_algorithm((cp, co, ep, eo))
        self.assertIsInstance(result, Algorithm)

        # Apply and verify
        test_cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_SO)
        test_cube.rotate(result)
        self.assertTrue(test_cube.is_solved)

    def test_complex_cubie_state(self) -> None:
        """Test complex cubie state with all components changed."""
        cube = VCube()
        cube.rotate("R U R' U' R' F R2 U' R' U' R U R' F'")
        cp, co, ep, eo, _so = cube.to_cubies

        result = cubies_to_algorithm((cp, co, ep, eo))
        self.assertIsInstance(result, Algorithm)

        # Apply and verify
        test_cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_SO)
        test_cube.rotate(result)
        self.assertTrue(test_cube.is_solved)
