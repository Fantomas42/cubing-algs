"""Tests for visual cube URL generation."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.vcube import VCube
from cubing_algs.visual_cube import VISUAL_URL
from cubing_algs.visual_cube import visual_cube_algorithm
from cubing_algs.visual_cube import visual_cube_cube


class VisualCubeTestCase(unittest.TestCase):
    """Tests for visual cube URL generation functions."""

    def test_visual_cube_algorithm_default_size(self) -> None:
        """Test visual_cube_algorithm with default size."""
        algo = Algorithm.parse_moves("R U R' U'")
        url = visual_cube_algorithm(algo)

        expected = f"{VISUAL_URL}&pzl=3&alg=RUR'U'"
        self.assertEqual(url, expected)

    def test_visual_cube_algorithm_custom_size(self) -> None:
        """Test visual_cube_algorithm with custom size."""
        algo = Algorithm.parse_moves("R U2 D'")
        url = visual_cube_algorithm(algo, size=4)

        expected = f"{VISUAL_URL}&pzl=4&alg=RU2D'"
        self.assertEqual(url, expected)

    def test_visual_cube_algorithm_empty(self) -> None:
        """Test visual_cube_algorithm with empty algorithm."""
        algo = Algorithm()
        url = visual_cube_algorithm(algo)

        expected = f'{VISUAL_URL}&pzl=3&alg='
        self.assertEqual(url, expected)

    def test_visual_cube_algorithm_complex(self) -> None:
        """Test visual_cube_algorithm with complex moves."""
        algo = Algorithm.parse_moves("Rw U2 x R' U R U' R'")
        url = visual_cube_algorithm(algo)

        expected = f"{VISUAL_URL}&pzl=3&alg=RwU2xR'URU'R'"
        self.assertEqual(url, expected)

    def test_visual_cube_cube(self) -> None:
        """Test visual_cube_cube with VCube instance."""
        cube = VCube()
        url = visual_cube_cube(cube)

        # VCube state is uppercase, but visual_cube_cube converts to lowercase
        expected_state = cube.state.lower()
        expected = f'{VISUAL_URL}&pzl=3&fd={expected_state}'
        self.assertEqual(url, expected)

    def test_visual_cube_cube_scrambled(self) -> None:
        """Test visual_cube_cube with scrambled cube."""
        cube = VCube()
        cube.rotate("R U R' U'")
        url = visual_cube_cube(cube)

        expected_state = cube.state.lower()
        expected = f'{VISUAL_URL}&pzl=3&fd={expected_state}'
        self.assertEqual(url, expected)
        # Verify the state contains expected characters
        self.assertTrue(all(c in 'urfdlb' for c in expected_state))


class AlgorithmVisualCubePropertyTestCase(unittest.TestCase):
    """Tests for Algorithm.visual_cube_url property."""

    def test_algorithm_visual_cube_url(self) -> None:
        """Test Algorithm.visual_cube_url property."""
        algo = Algorithm.parse_moves("R U R' U'")
        url = algo.visual_cube_url

        expected = f"{VISUAL_URL}&pzl=3&alg=RUR'U'"
        self.assertEqual(url, expected)

    def test_algorithm_visual_cube_url_empty(self) -> None:
        """Test Algorithm.visual_cube_url property with empty algorithm."""
        algo = Algorithm()
        url = algo.visual_cube_url

        expected = f'{VISUAL_URL}&pzl=3&alg='
        self.assertEqual(url, expected)


class VCubeVisualCubePropertyTestCase(unittest.TestCase):
    """Tests for VCube.visual_cube_url property."""

    def test_vcube_visual_cube_url(self) -> None:
        """Test VCube.visual_cube_url property."""
        cube = VCube()
        url = cube.visual_cube_url

        expected_state = cube.state.lower()
        expected = f'{VISUAL_URL}&pzl=3&fd={expected_state}'
        self.assertEqual(url, expected)

    def test_vcube_visual_cube_url_scrambled(self) -> None:
        """Test VCube.visual_cube_url property with scrambled cube."""
        cube = VCube()
        cube.rotate("F R U' R' U' R U R' F' R U R' U' R' F R F'")
        url = cube.visual_cube_url

        expected_state = cube.state.lower()
        expected = f'{VISUAL_URL}&pzl=3&fd={expected_state}'
        self.assertEqual(url, expected)
