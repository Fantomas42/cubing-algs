"""Tests for the Algorithm class."""
import unittest
from contextlib import redirect_stdout
from io import StringIO

from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import ErgonomicsData
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves
from cubing_algs.vcube import VCube


class AlgorithmTestCase(unittest.TestCase):  # noqa: PLR0904
    """Tests for the Algorithm class core functionality."""

    def check_contains_moves(self, algo: Algorithm) -> None:
        """Check algo contains Move only."""
        for m in algo:
            self.assertIsInstance(m, Move)

    def test_init_empty(self) -> None:
        """Test init empty."""
        algo = Algorithm()
        self.assertEqual(str(algo), '')

        algo.extend('R2 U')

        self.assertEqual(str(algo), 'R2 U')

    def test_init_value(self) -> None:
        """Test init value."""
        algo = Algorithm([Move('F'), Move('R'), Move('U2')])
        self.assertEqual(str(algo), 'F R U2')

    def test_parse_moves(self) -> None:
        """Test parse moves."""
        algo = Algorithm.parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo = Algorithm.parse_moves(['R2', 'U'])
        self.assertEqual(str(algo), 'R2 U')

        algo = Algorithm.parse_moves([Move('R2'), Move('U')])
        self.assertEqual(str(algo), 'R2 U')

        algo = Algorithm.parse_moves(Move('R2'))
        self.assertEqual(str(algo), 'R2')

        algo = Algorithm.parse_moves(Algorithm.parse_moves(['R2', 'U']))
        self.assertEqual(str(algo), 'R2 U')

    def test_parse_move(self) -> None:
        """Test parse move."""
        move = Algorithm.parse_move('R2')
        self.assertEqual(move, 'R2')

        move = Algorithm.parse_move(Move('R2'))
        self.assertEqual(move, 'R2')

        with self.assertRaises(InvalidMoveError):
            Algorithm.parse_move('R2 U')

    def test_append(self) -> None:
        """Test append."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo.append('F2')
        self.assertEqual(str(algo), 'R2 U F2')

        self.check_contains_moves(algo)

        algo.append(Move('D'))
        self.assertEqual(str(algo), 'R2 U F2 D')

        self.check_contains_moves(algo)

        with self.assertRaises(InvalidMoveError):
            algo.append('G')

        with self.assertRaises(InvalidMoveError):
            algo.append('F R')

        with self.assertRaises(InvalidMoveError):
            algo.append(Move('G'))

        with self.assertRaises(InvalidMoveError):
            algo.append(['F', 'R'])  # type: ignore[arg-type]

        with self.assertRaises(InvalidMoveError):
            algo.append([])  # type: ignore[arg-type]

    def test_extend(self) -> None:
        """Test extend."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo.extend(['F2', 'B'])
        self.assertEqual(str(algo), 'R2 U F2 B')

        self.check_contains_moves(algo)

        algo.extend([])
        self.assertEqual(str(algo), 'R2 U F2 B')

        self.check_contains_moves(algo)

        algo.extend('F R')
        self.assertEqual(str(algo), 'R2 U F2 B F R')

        self.check_contains_moves(algo)

        algo.extend('D2')
        self.assertEqual(str(algo), 'R2 U F2 B F R D2')

        self.check_contains_moves(algo)

        algo.extend([Move('L'), Move('B')])
        self.assertEqual(str(algo), 'R2 U F2 B F R D2 L B')

        self.check_contains_moves(algo)

        algo.extend(Move('U'))
        self.assertEqual(str(algo), 'R2 U F2 B F R D2 L B U')

        self.check_contains_moves(algo)

        with self.assertRaises(InvalidMoveError):
            algo.extend(['F2', 'G'])

    def test_extend_with_algorithm(self) -> None:
        """Test extend with algorithm."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo.extend(parse_moves('F2 B'))
        self.assertEqual(str(algo), 'R2 U F2 B')

        self.check_contains_moves(algo)

    def test_add_operator(self) -> None:
        """Test add operator."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo = algo + ['F2', 'B']  # noqa: RUF005, PLR6104
        self.assertEqual(str(algo), 'R2 U F2 B')

        self.check_contains_moves(algo)

        algo = algo + 'F R'  # noqa: PLR6104
        self.assertEqual(str(algo), 'R2 U F2 B F R')

        self.check_contains_moves(algo)

        with self.assertRaises(InvalidMoveError):
            algo += 'F2 G'

    def test_iadd_operator(self) -> None:
        """Test iadd operator."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo += ['F2', 'B']
        self.assertEqual(str(algo), 'R2 U F2 B')

        self.check_contains_moves(algo)

        algo += 'F R'
        self.assertEqual(str(algo), 'R2 U F2 B F R')

        self.check_contains_moves(algo)

        algo += [Move('L2'), Move('D')]
        self.assertEqual(str(algo), 'R2 U F2 B F R L2 D')

        self.check_contains_moves(algo)

        algo += Move('U')
        self.assertEqual(str(algo), 'R2 U F2 B F R L2 D U')

        self.check_contains_moves(algo)

        with self.assertRaises(InvalidMoveError):
            algo + 'F2 G'

    def test_radd_operator(self) -> None:
        """Test radd operator."""
        algo = 'F2R2' + parse_moves('D2 U')
        self.assertEqual(str(algo), 'F2 R2 D2 U')

        self.check_contains_moves(algo)

        algo = ['R2', 'L'] + algo  # noqa: RUF005
        self.assertEqual(str(algo), 'R2 L F2 R2 D2 U')

        self.check_contains_moves(algo)

        algo = [Move('D'), Move('U')] + algo  # noqa: RUF005
        self.assertEqual(str(algo), 'D U R2 L F2 R2 D2 U')

        self.check_contains_moves(algo)

        with self.assertRaises(InvalidMoveError):
            'F2 G' + algo

    def test_radd_operator_z(self) -> None:
        """Test radd operator z."""
        algo = 'z' + parse_moves('R2 U')
        self.assertEqual(str(algo), 'z R2 U')

    def test_radd_operator_zprime(self) -> None:
        """Test radd operator zprime."""
        algo = "z'" + parse_moves('R2 U')
        self.assertEqual(str(algo), "z' R2 U")

    def test_radd_operator_z2(self) -> None:
        """Test radd operator z2."""
        algo = 'z2' + parse_moves('R2 U')
        self.assertEqual(str(algo), 'z2 R2 U')

    def test_add(self) -> None:
        """Test add."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo += ['F2', 'B']
        self.assertEqual(str(algo), 'R2 U F2 B')

        self.check_contains_moves(algo)

        algo += [Move('D2'), Move('B2')]
        self.assertEqual(str(algo), 'R2 U F2 B D2 B2')

        self.check_contains_moves(algo)

        algo += 'z y'
        self.assertEqual(str(algo), 'R2 U F2 B D2 B2 z y')

        self.check_contains_moves(algo)

        algo += Move('B')
        self.assertEqual(str(algo), 'R2 U F2 B D2 B2 z y B')

        self.check_contains_moves(algo)

        with self.assertRaises(InvalidMoveError):
            algo += 'F G'

    def test_add_exploded(self) -> None:
        """Test add exploded."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo += [*algo, 'F2', 'B']
        self.assertEqual(str(algo), 'R2 U R2 U F2 B')

        self.check_contains_moves(algo)

    def test_add_operator_with_algorithm(self) -> None:
        """Test add operator with algorithm."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo = algo + parse_moves('F2 B')  # noqa: PLR6104
        self.assertEqual(str(algo), 'R2 U F2 B')

        self.check_contains_moves(algo)

    def test_insert(self) -> None:
        """Test insert."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo.insert(0, 'F2')
        self.assertEqual(str(algo), 'F2 R2 U')

        self.check_contains_moves(algo)

        algo.insert(0, Move('L'))
        self.assertEqual(str(algo), 'L F2 R2 U')

        self.check_contains_moves(algo)

        with self.assertRaises(InvalidMoveError):
            algo.insert(0, 'G')

    def test_remove(self) -> None:
        """Test remove."""
        algo = parse_moves('R2 U R2')
        self.assertEqual(str(algo), 'R2 U R2')

        algo.remove(Move('R2'))
        self.assertEqual(str(algo), 'U R2')

        self.check_contains_moves(algo)

    def test_remove_type_str(self) -> None:
        """Test remove type str."""
        algo = parse_moves('R2 U R2')
        self.assertEqual(str(algo), 'R2 U R2')

        algo.remove('R2')  # type: ignore[arg-type]
        self.assertEqual(str(algo), 'U R2')

        self.check_contains_moves(algo)

    def test_pop(self) -> None:
        """Test pop."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        popped = algo.pop()
        self.assertEqual(str(algo), 'R2')
        self.assertEqual(popped, 'U')

        self.check_contains_moves(algo)

    def test_copy(self) -> None:
        """Test copy."""
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        copy = algo.copy()
        self.assertIsInstance(copy, Algorithm)
        self.assertEqual(str(copy), 'R2 U')

        self.check_contains_moves(algo)
        self.check_contains_moves(copy)

        algo.pop()
        self.assertEqual(str(algo), 'R2')
        self.assertEqual(str(copy), 'R2 U')

        self.check_contains_moves(algo)
        self.check_contains_moves(copy)

    def test_iter(self) -> None:
        """Test iter."""
        algo = parse_moves('R2 U')
        for m, n in zip(algo, ['R2', 'U'], strict=True):
            self.assertEqual(m, n)

    def test_getitem(self) -> None:
        """Test getitem."""
        algo = parse_moves('R2 U')
        self.assertEqual(algo[1], 'U')
        self.assertIsInstance(algo[1], Move)

        algo = parse_moves('R2 U F D B L')[1:4]
        self.assertEqual(str(algo), 'U F D')
        self.assertIsInstance(algo, Algorithm)
        self.assertIsInstance(algo[1], Move)

    def test_setitem_slice(self) -> None:
        """Test setitem slice."""
        algo = parse_moves('R2 U F')
        algo[2:] = []
        self.assertEqual(str(algo), 'R2 U')

        self.check_contains_moves(algo)

        algo = parse_moves('R2 U F')
        algo[1:] = []
        self.assertEqual(str(algo), 'R2')

        self.check_contains_moves(algo)

        algo = parse_moves('R2 U F')
        new_algo = parse_moves('B2 D')
        algo[2:] = new_algo
        self.assertEqual(str(algo), 'R2 U B2 D')

        self.check_contains_moves(algo)

        algo = parse_moves('R2 U F')
        new_algo = parse_moves('B2 D')
        algo[1:] = new_algo
        self.assertEqual(str(algo), 'R2 B2 D')

        self.check_contains_moves(algo)

        algo = parse_moves('R2 U F L D')
        new_algo = parse_moves('B2 D')
        algo[1:3] = new_algo
        self.assertEqual(str(algo), 'R2 B2 D L D')

        self.check_contains_moves(algo)

    def test_setitem(self) -> None:
        """Test setitem."""
        algo = parse_moves('R2 U')
        algo[1] = Move('B')
        self.assertEqual(str(algo), 'R2 B')

        self.check_contains_moves(algo)

    def test_delitem(self) -> None:
        """Test delitem."""
        algo = parse_moves('R2 U')
        del algo[1]
        self.assertEqual(str(algo), 'R2')

        self.check_contains_moves(algo)

    def test_contains(self) -> None:
        """Test contains."""
        algo = parse_moves('R2 U')
        self.assertIn(Move('U'), algo)
        self.assertIn(Move('R2'), algo)
        self.assertNotIn(Move('R'), algo)

    def test_contains_type_str(self) -> None:
        """Test contains type str."""
        algo = parse_moves('R2 U')
        self.assertIn('U', algo)
        self.assertIn('R2', algo)
        self.assertNotIn('R', algo)
        self.assertNotIn('2', algo)

    def test_count(self) -> None:
        """Test count."""
        algo = parse_moves('R2 U F R R2')
        self.assertEqual(algo.count(Move('R')), 1)
        self.assertEqual(algo.count(Move('R2')), 2)
        self.assertEqual(algo.count(Move('L')), 0)

    def test_count_type_str(self) -> None:
        """Test count type str."""
        algo = parse_moves('R2 U F R R2')
        self.assertEqual(algo.count('R'), 1)   # type: ignore[arg-type]
        self.assertEqual(algo.count('R2'), 2)  # type: ignore[arg-type]
        self.assertEqual(algo.count('L'), 0)   # type: ignore[arg-type]
        self.assertEqual(algo.count('2'), 0)   # type: ignore[arg-type]

    def test_index(self) -> None:
        """Test index."""
        algo = parse_moves('R2 U F R R2')
        self.assertEqual(algo.index(Move('R')), 3)
        self.assertEqual(algo.index(Move('R2')), 0)

        with self.assertRaises(ValueError):
            algo.index(Move('L'))

    def test_index_type_str(self) -> None:
        """Test index type str."""
        algo = parse_moves('R2 U F R R2')
        self.assertEqual(algo.index('R'), 3)   # type: ignore[arg-type]
        self.assertEqual(algo.index('R2'), 0)  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            algo.index('L')  # type: ignore[arg-type]

        with self.assertRaises(ValueError):
            algo.index('2')  # type: ignore[arg-type]

    def test_length(self) -> None:
        """Test length."""
        algo = parse_moves('R2 U')

        self.assertEqual(len(algo), 2)

    def test_str(self) -> None:
        """Test str."""
        algo = parse_moves('R2 U')

        self.assertEqual(str(algo), 'R2 U')

    def test_repr(self) -> None:
        """Test repr."""
        algo = parse_moves('R2 U')

        self.assertEqual(repr(algo), 'Algorithm("R2U")')

    def test_eq(self) -> None:
        """Test eq."""
        algo = parse_moves('R2 U')
        algo_bis = parse_moves('R2 U')

        self.assertEqual(algo, algo_bis)

    def test_eq_copy(self) -> None:
        """Test eq copy."""
        algo = parse_moves('R2 U')
        algo_copy = algo.copy()

        self.assertEqual(algo, algo_copy)

    def test_eq_list(self) -> None:
        """Test eq list."""
        algo = parse_moves('R2 U')
        algo_list = [Move('R2'), Move('U')]

        self.assertEqual(algo, algo_list)

    def test_transform(self) -> None:
        """Test transform."""
        algo = parse_moves('R R U F2 F2')
        expected = parse_moves('R2 U')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
            ),
            expected,
        )

        algo = parse_moves('R U F2')
        expected = parse_moves('R U F2')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
            ),
            expected,
        )

    def test_transform_to_fixpoint(self) -> None:
        """Test transform to fixpoint."""
        algo = parse_moves("R R F F' R2 U F2")
        expected = parse_moves('R2 R2 U F2')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
            ),
            expected,
        )

        algo = parse_moves("R R F F' R2 U F2")
        expected = parse_moves('U F2')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
                to_fixpoint=True,
            ),
            expected,
        )

    def test_min_cube_size(self) -> None:
        """Test min cube size."""
        algo = parse_moves("B' R2 U F2")

        self.assertEqual(
            algo.min_cube_size,
            2,
        )

        algo = parse_moves("B' R2 M U F2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' r2 U F2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' R2 U Fw2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' R2 U 2Fw2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' R2 U 3Fw2")

        self.assertEqual(
            algo.min_cube_size,
            6,
        )

        algo = parse_moves("B' R2 U 2-3Fw2")

        self.assertEqual(
            algo.min_cube_size,
            6,
        )

        algo = parse_moves("B' R2 U 4Fw2")

        self.assertEqual(
            algo.min_cube_size,
            8,
        )

        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertEqual(
            algo.min_cube_size,
            8,
        )

    def test_is_standard(self) -> None:
        """Test is standard."""
        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertTrue(algo.is_standard)
        self.assertFalse(algo.is_sign)

    def test_is_sign(self) -> None:
        """Test is sign."""
        algo = parse_moves("B' R2 U 2-4f2")

        self.assertTrue(algo.is_sign)
        self.assertFalse(algo.is_standard)

    def test_has_rotations(self) -> None:
        """Test has rotations."""
        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertTrue(algo.has_rotations)

        algo = parse_moves("B' R2 U 2-4f2")

        self.assertTrue(algo.has_rotations)

        algo = parse_moves("B' R2 U x")

        self.assertTrue(algo.has_rotations)

        algo = parse_moves('R2 E U')

        self.assertTrue(algo.has_rotations)

        algo = parse_moves('R2 F U D2 L B')

        self.assertFalse(algo.has_rotations)

    def test_has_internal_rotations(self) -> None:
        """Test has internal rotations."""
        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertTrue(algo.has_internal_rotations)

        algo = parse_moves("B' R2 U 2-4f2")

        self.assertTrue(algo.has_internal_rotations)

        algo = parse_moves('R2 E U')

        self.assertTrue(algo.has_internal_rotations)

        algo = parse_moves("B' R2 U x")

        self.assertFalse(algo.has_internal_rotations)


class AlgorithmCyclesPropertyTestCase(unittest.TestCase):
    """Test cases for the Algorithm.cycles property."""

    def test_empty_algorithm_cycles(self) -> None:
        """Test cycles property for empty algorithm."""
        algo = Algorithm()
        result = algo.cycles
        self.assertEqual(result, 0)

    def test_single_move_cycles(self) -> None:
        """Test cycles property for single move."""
        algo = Algorithm.parse_moves('R')
        result = algo.cycles
        self.assertEqual(result, 4)  # R has order 4

    def test_sexy_move_cycles(self) -> None:
        """Test cycles property for sexy move."""
        algo = Algorithm.parse_moves("R U R' U'")
        result = algo.cycles
        self.assertEqual(result, 6)  # Known order of sexy move

    def test_half_turn_cycles(self) -> None:
        """Test cycles property for half turn."""
        algo = Algorithm.parse_moves('R2')
        result = algo.cycles
        self.assertEqual(result, 2)  # R2 has order 2

    def test_identity_cycles(self) -> None:
        """Test cycles property for identity algorithm."""
        algo = Algorithm.parse_moves("R R'")
        result = algo.cycles
        self.assertEqual(result, 1)

    def test_complex_algorithm_cycles(self) -> None:
        """Test cycles property for complex algorithm."""
        algo = Algorithm.parse_moves("R U2 R' D' R U' R' D")
        result = algo.cycles
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLess(result, 100)

    def test_cycles_return_int_non_negative(self) -> None:
        """Test that cycles property returns integer."""
        test_cases = ['R', "R U R' U'", 'F2', 'x', 'M', '']

        for moves_str in test_cases:
            with self.subTest(moves=moves_str):
                if not moves_str:
                    algo = Algorithm()
                else:
                    algo = Algorithm.parse_moves(moves_str)
                result = algo.cycles
                self.assertIsInstance(result, int)
                self.assertGreaterEqual(result, 0)

    def test_cycles_with_rotations(self) -> None:
        """Test cycles property with cube rotations."""
        algo = Algorithm.parse_moves('x y z')
        result = algo.cycles
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)

    def test_cycles_with_slice_moves(self) -> None:
        """Test cycles property with slice moves."""
        algo = Algorithm.parse_moves('M E S')
        result = algo.cycles
        self.assertIsInstance(result, int)
        self.assertEqual(result, 4)

    def test_cycles_with_wide_moves(self) -> None:
        """Test cycles property with wide moves."""
        algo = Algorithm.parse_moves('r u f')
        result = algo.cycles
        self.assertIsInstance(result, int)
        self.assertEqual(result, 70)

    def test_cycles_with_pauses(self) -> None:
        """Test cycles property with pauses."""
        algo = Algorithm.parse_moves('R U . F')
        result = algo.cycles
        self.assertIsInstance(result, int)
        self.assertEqual(result, 80)

    def test_cycles_with_timed_moves(self) -> None:
        """Test cycles property with timed moves."""
        algo = Algorithm.parse_moves('R@50 U@75 F@100')
        result = algo.cycles
        self.assertIsInstance(result, int)
        self.assertEqual(result, 80)


class AlgorithmShowTestCase(unittest.TestCase):
    """Test cases for the Algorithm.show method."""

    def test_show_method_basic(self) -> None:
        """Test show method returns VCube instance."""
        algo = Algorithm.parse_moves("R U R'")

        with redirect_stdout(StringIO()):
            result = algo.show()

        self.assertIsInstance(result, VCube)

    def test_show_method_with_parameters(self) -> None:
        """Test show method with mode and orientation parameters."""
        algo = Algorithm.parse_moves("R U R'")

        with redirect_stdout(StringIO()):
            result = algo.show(mode='oll', orientation='FU')

        self.assertIsInstance(result, VCube)

    def test_show_method_empty_algorithm(self) -> None:
        """Test show method with empty algorithm."""
        algo = Algorithm()

        with redirect_stdout(StringIO()):
            result = algo.show()

        self.assertIsInstance(result, VCube)


class AlgorithmErgonomicsTestCase(unittest.TestCase):
    """Test cases for the Algorithm.ergonomics property."""

    def test_ergonomics_property_returns_ergonomics_data(self) -> None:
        """Test ergonomics property returns ErgonomicsData."""
        algo = Algorithm.parse_moves("R U R' U'")
        ergo = algo.ergonomics

        self.assertIsInstance(ergo, ErgonomicsData)

    def test_ergonomics_property_has_expected_fields(self) -> None:
        """Test ergonomics property returns data with expected fields."""
        algo = Algorithm.parse_moves("R U R' U'")
        ergo = algo.ergonomics

        # Check that all expected fields are present
        self.assertIsNotNone(ergo.comfort_score)
        self.assertIsNotNone(ergo.ergonomic_rating)
        self.assertIsNotNone(ergo.hand_balance_ratio)

    def test_ergonomics_property_empty_algorithm(self) -> None:
        """Test ergonomics property with empty algorithm."""
        algo = Algorithm()
        ergo = algo.ergonomics

        self.assertIsInstance(ergo, ErgonomicsData)
