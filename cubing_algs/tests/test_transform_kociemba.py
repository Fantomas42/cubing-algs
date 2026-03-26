"""Tests for Kociemba transformation functions."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.kociemba import kociemba_moves
from cubing_algs.vcube import VCube


class TransformKociembaTestCase(unittest.TestCase):  # noqa: PLR0904
    """
    Tests for Kociemba transformation
    that returns solver-generated algorithms.
    """

    def test_empty_algorithm(self) -> None:
        """Test empty algorithm returns empty algorithm."""
        provide = Algorithm()
        result = kociemba_moves(provide)

        self.assertEqual(result, Algorithm())
        self.assertEqual(len(result), 0)
        self.assertEqual(str(result), '')

    def test_solved_cube_returns_empty(self) -> None:
        """Test solved cube state returns empty algorithm."""
        provide = parse_moves("R U R' U'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)

    def test_single_move(self) -> None:
        """Test single basic move produces equivalent state."""
        provide = parse_moves('R')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'R')

    def test_single_move_prime(self) -> None:
        """Test single prime move produces equivalent state."""
        provide = parse_moves("R'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "R'")

    def test_single_move_double(self) -> None:
        """Test single double move produces equivalent state."""
        provide = parse_moves('R2')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'R2')

    def test_multiple_basic_moves(self) -> None:
        """Test multiple basic moves produce equivalent state."""
        provide = parse_moves('R U F')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'R U F')

    def test_result_contains_only_move_instances(self) -> None:
        """Test that result contains only Move instances."""
        provide = parse_moves('R U F L D B')
        result = kociemba_moves(provide)

        self.assertEqual(str(result), 'R U F L D B')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_sune_algorithm(self) -> None:
        """Test Sune algorithm produces equivalent state."""
        provide = parse_moves("R U R' U R U2 R'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(
            str(result),
            "R U R2 U' R2 U R U2 F2 R2 F2 U2 F2 R2 F2 U",
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_t_perm_algorithm(self) -> None:
        """Test T-perm algorithm produces equivalent state."""
        provide = parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "U F2 U' F2 D R2 B2 U B2 D' R2")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_sexy_move_algorithm(self) -> None:
        """Test sexy move algorithm produces equivalent state."""
        provide = parse_moves("R U R' U'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "R U R' U'")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_wide_move_conversion(self) -> None:
        """Test wide move raises error due to orientation change."""
        provide = parse_moves('Rw')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'L x')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_wide_moves_algorithm(self) -> None:
        """Test algorithm with paired wide moves produces equivalent state."""
        provide = parse_moves("Rw U Rw' U'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "L F L' U'")

        for m in result:
            self.assertTrue(isinstance(m, Move))
            self.assertFalse(m.is_wide_move)

    def test_rotation_x(self) -> None:
        """Test x rotation raises error due to orientation change."""
        provide = parse_moves('x')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'x')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rotation_y(self) -> None:
        """Test y rotation raises error due to orientation change."""
        provide = parse_moves('y')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'y')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rotation_z(self) -> None:
        """Test z rotation raises error due to orientation change."""
        provide = parse_moves('z')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'z')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_multiple_rotations(self) -> None:
        """Test multiple rotations raise error due to orientation change."""
        provide = parse_moves('x y z')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'y z2')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_slice_move_m(self) -> None:
        """Test M slice move raises error due to orientation change."""
        provide = parse_moves('M')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "R L' x'")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_slice_move_e(self) -> None:
        """Test E slice move raises error due to orientation change."""
        provide = parse_moves('E')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "U D' y'")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_slice_move_s(self) -> None:
        """Test S slice move raises error due to orientation change."""
        provide = parse_moves('S')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "F' B z")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_complex_algorithm_with_orientation_changing_moves(self) -> None:
        """Test algorithm with orientation-changing moves raises error."""
        provide = parse_moves("x R U R' U'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "R F R' F' x")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_inverse_algorithm(self) -> None:
        """Test inverse of algorithm produces equivalent state."""
        provide = parse_moves("R U R' U' R' F R F'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "F R F U F' R' F U' F2")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_j_perm_algorithm(self) -> None:
        """Test J-perm algorithm produces equivalent state."""
        provide = parse_moves("R U R' F' R U R' U' R' F R2 U' R'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "U2 F2 R2 U R2 U' R2 D R2 D' F2")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_result_uses_only_basic_faces(self) -> None:
        """Test result uses only R, U, F, L, D, B faces."""
        provide = parse_moves('R U F L D B')
        result = kociemba_moves(provide)

        self.assertEqual(str(result), 'R U F L D B')

        valid_faces = {'R', 'U', 'F', 'L', 'D', 'B'}

        for m in result:
            self.assertIn(m.base_move, valid_faces)

    def test_result_has_no_wide_moves(self) -> None:
        """Test result contains no wide moves."""
        provide = parse_moves('R U F L D B')
        result = kociemba_moves(provide)

        self.assertEqual(str(result), 'R U F L D B')
        self.assertNotIn('w', str(result))

        for m in result:
            self.assertFalse(m.is_wide_move)

    def test_result_has_no_rotations(self) -> None:
        """Test result contains no rotations."""
        provide = parse_moves('R U F L D B')
        result = kociemba_moves(provide)

        self.assertEqual(str(result), 'R U F L D B')
        self.assertNotIn('x', str(result))
        self.assertNotIn('y', str(result))
        self.assertNotIn('z', str(result))

        for m in result:
            self.assertFalse(m.is_rotational_move)

    def test_result_has_no_slice_moves(self) -> None:
        """Test result contains no slice moves."""
        provide = parse_moves('R U F L D B')
        result = kociemba_moves(provide)

        self.assertEqual(str(result), 'R U F L D B')
        self.assertNotIn('M', str(result))
        self.assertNotIn('E', str(result))
        self.assertNotIn('S', str(result))

        for m in result:
            self.assertFalse(m.is_inner_move)

    def test_long_algorithm(self) -> None:
        """Test long algorithm produces equivalent state."""
        provide = parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F' "
            "R U R' U R U2 R' U' R U2 R' U' R U' R'",
        )
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(
            str(result),
            "R' F2 R' B2 R F2 R' U B2 U' B2 R2 F2 D' L2 D F2",
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_canceling_moves(self) -> None:
        """Test algorithm with canceling moves produces equivalent state."""
        provide = parse_moves("R R' U U' F F'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), '')

    def test_redundant_algorithm(self) -> None:
        """Test redundant algorithm produces equivalent state."""
        provide = parse_moves('R R R R')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), '')

    def test_double_moves_only(self) -> None:
        """Test algorithm with only double moves."""
        provide = parse_moves('R2 U2 F2 D2')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'R2 U2 F2 D2')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_prime_moves_only(self) -> None:
        """Test algorithm with only prime moves."""
        provide = parse_moves("R' U' F' D' L' B'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "R' U' F' D' L' B'")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_all_basic_faces(self) -> None:
        """Test algorithm using all six basic faces."""
        provide = parse_moves('R U F L D B')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'R U F L D B')

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_result_modifiers_are_valid(self) -> None:
        """Test result contains only valid modifiers."""
        provide = parse_moves("R U2 F' D L2 B'")
        result = kociemba_moves(provide)

        self.assertEqual(str(result), "R U2 F' D L2 B'")

        valid_modifiers = {'', "'", '2'}

        for m in result:
            self.assertIn(m.modifier, valid_modifiers)

    def test_commutator_pattern(self) -> None:
        """Test commutator pattern produces equivalent state."""
        provide = parse_moves("R U R' U' R' F R F'")
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(provide)

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), "F R F U F' R' F U' F2")

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_timed_moves_stripped(self) -> None:
        """Test timed moves are stripped and produce equivalent state."""
        provide = parse_moves('R@100 U@200')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(parse_moves('R U'))

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'R U')

        for m in result:
            self.assertFalse(m.is_timed)

    def test_pause_moves_stripped(self) -> None:
        """Test pause moves are removed before solving."""
        provide = parse_moves('R . U')
        result = kociemba_moves(provide)

        cube1 = VCube()
        cube1.rotate(parse_moves('R U'))

        cube2 = VCube()
        cube2.rotate(result)

        self.assertEqual(cube1.state, cube2.state)
        self.assertEqual(str(result), 'R U')

        for m in result:
            self.assertFalse(m.is_pause)

    def test_only_pauses(self) -> None:
        """Test algorithm with only pauses returns empty."""
        provide = parse_moves('. .')
        result = kociemba_moves(provide)

        self.assertEqual(str(result), '')
