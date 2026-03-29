"""Tests for solver functions."""
import unittest

from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.constants import SOLVED_EP
from cubing_algs.exceptions import InvalidFaceletsSolveError
from cubing_algs.solved_state import SOLVED_FACELETS_3x3x3
from cubing_algs.solver import cubies_to_cubies_algorithm
from cubing_algs.solver import facelets_to_facelets_algorithm
from cubing_algs.vcube import VCube


class FaceletsToFaceletsAlgorithmTestCase(unittest.TestCase):
    """Tests for facelets_to_facelets_algorithm function."""

    def test_single_move_r(self) -> None:
        """Test solving single R move returns R'."""
        source = VCube()
        source.rotate('R')

        algorithm = facelets_to_facelets_algorithm(
            source.state,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), "R'")

    def test_single_move_u(self) -> None:
        """Test solving single U move returns U'."""
        source = VCube()
        source.rotate('U')

        algorithm = facelets_to_facelets_algorithm(
            source.state,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), "U'")

    def test_double_move_r2(self) -> None:
        """Test solving R2 returns R2."""
        source = VCube()
        source.rotate('R2')

        algorithm = facelets_to_facelets_algorithm(
            source.state,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), 'R2')

    def test_sexy_move(self) -> None:
        """Test solving sexy move R U R' U' returns U R U' R'."""
        source = VCube()
        source.rotate("R U R' U'")

        algorithm = facelets_to_facelets_algorithm(
            source.state,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), "U R U' R'")

    def test_sledgehammer(self) -> None:
        """Test solving sledgehammer R' F R F' returns F R' F' R."""
        source = VCube()
        source.rotate("R' F R F'")

        algorithm = facelets_to_facelets_algorithm(
            source.state,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), "F R' F' R")

    def test_sune(self) -> None:
        """Test solving sune R U R' U R U2 R'."""
        source = VCube()
        source.rotate("R U R' U R U2 R'")

        algorithm = facelets_to_facelets_algorithm(
            source.state,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), "R U2 R' U' R U' R'")

    def test_double_moves(self) -> None:
        """Test solving R2 U2 R U2 R2."""
        source = VCube()
        source.rotate('R2 U2 R U2 R2')

        algorithm = facelets_to_facelets_algorithm(
            source.state,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), "R2 U2 R' U2 R2")

    def test_kociemba_exception(self) -> None:
        """
        Test solved to solved, known to provide invalid results.

        https://github.com/muodov/kociemba/issues/56
        """
        algorithm = facelets_to_facelets_algorithm(
            SOLVED_FACELETS_3x3x3,
            SOLVED_FACELETS_3x3x3,
        )

        self.assertEqual(str(algorithm), '')

    def test_invalid_facelets_raises_error(self) -> None:
        """Test that invalid facelets raise InvalidFaceletsSolveError."""
        invalid_facelets = 'U' * 54

        with self.assertRaises(InvalidFaceletsSolveError) as context:
            facelets_to_facelets_algorithm(
                invalid_facelets,
                SOLVED_FACELETS_3x3x3,
            )

        error_msg = str(context.exception)
        self.assertIn('Solver encountered an error', error_msg)
        self.assertIn('probably the facelets are not UF oriented', error_msg)

    def test_invalid_destination_raises_error(self) -> None:
        """Test that invalid destination facelets raise error."""
        invalid_facelets = (
            'RRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBBRRRRRRRRR'
        )

        with self.assertRaises(InvalidFaceletsSolveError):
            facelets_to_facelets_algorithm(
                SOLVED_FACELETS_3x3x3,
                invalid_facelets,
            )

    def test_malformed_facelets_length(self) -> None:
        """Test that facelets with wrong length raise error."""
        short_facelets = 'UUU'

        with self.assertRaises(InvalidFaceletsSolveError):
            facelets_to_facelets_algorithm(
                short_facelets,
                SOLVED_FACELETS_3x3x3,
            )

    def test_empty_facelets(self) -> None:
        """Test that empty facelets raise error."""
        empty_facelets = ''

        with self.assertRaises(InvalidFaceletsSolveError):
            facelets_to_facelets_algorithm(
                empty_facelets,
                SOLVED_FACELETS_3x3x3,
            )


class CubiesToCubiesAlgorithmTestCase(unittest.TestCase):
    """Tests for cubies_to_cubies_algorithm function."""

    def test_single_move_r_cubies(self) -> None:
        """Test solving single R move from cubies returns R'."""
        source_cube = VCube()
        source_cube.rotate('R')

        cp, co, ep, eo, _ = source_cube.cubies
        source = (cp, co, ep, eo)
        destination = (list(SOLVED_CP), list(SOLVED_CO),
                       list(SOLVED_EP), list(SOLVED_EO))

        algorithm = cubies_to_cubies_algorithm(source, destination)

        self.assertEqual(str(algorithm), "R'")

    def test_double_move_r2_cubies(self) -> None:
        """Test solving R2 from cubies returns R2."""
        source_cube = VCube()
        source_cube.rotate('R2')

        cp, co, ep, eo, _ = source_cube.cubies
        source = (cp, co, ep, eo)
        destination = (list(SOLVED_CP), list(SOLVED_CO),
                       list(SOLVED_EP), list(SOLVED_EO))

        algorithm = cubies_to_cubies_algorithm(source, destination)

        self.assertEqual(str(algorithm), 'R2')

    def test_sexy_move_cubies(self) -> None:
        """Test solving sexy move from cubies returns U R U' R'."""
        source_cube = VCube()
        source_cube.rotate("R U R' U'")

        cp, co, ep, eo, _ = source_cube.cubies
        source = (cp, co, ep, eo)
        destination = (list(SOLVED_CP), list(SOLVED_CO),
                       list(SOLVED_EP), list(SOLVED_EO))

        algorithm = cubies_to_cubies_algorithm(source, destination)

        self.assertEqual(str(algorithm), "U R U' R'")

    def test_sune_cubies(self) -> None:
        """Test solving sune from cubies."""
        source_cube = VCube()
        source_cube.rotate("R U R' U R U2 R'")

        cp, co, ep, eo, _ = source_cube.cubies
        source = (cp, co, ep, eo)
        destination = (list(SOLVED_CP), list(SOLVED_CO),
                       list(SOLVED_EP), list(SOLVED_EO))

        algorithm = cubies_to_cubies_algorithm(source, destination)

        self.assertEqual(str(algorithm), "R U2 R' U' R U' R'")
