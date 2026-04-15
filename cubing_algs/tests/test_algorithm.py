"""Tests for the Algorithm class."""
import json
import re
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import ErgonomicsData
from cubing_algs.exceptions import InvalidCubeSizeError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.impacts import ImpactData
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.invert import invert_moves
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

    def test_setitem_slice_with_move(self) -> None:
        """Test setitem slice with a Move value replaces the slice correctly."""
        algo = parse_moves('R2 U F L D')
        algo[1:3] = Move('R2')
        self.assertEqual(str(algo), 'R2 R2 L D')

        self.check_contains_moves(algo)

    def test_setitem_int(self) -> None:
        """Test setitem."""
        algo = parse_moves('R2 U')
        algo[1] = Move('B')
        self.assertEqual(str(algo), 'R2 B')

        self.check_contains_moves(algo)

    def test_setitem_int_with_string(self) -> None:
        """Test setitem with a string stores a Move, not an Algorithm."""
        algo = parse_moves('R2 U F')
        algo[1] = 'B'
        self.assertEqual(str(algo), 'R2 B F')

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

        self.assertEqual(repr(algo), 'Algorithm("R2 U")')

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

    def test_transform_to_fixpoint_exhausted(self) -> None:
        """
        Test transform to fixpoint when MAX_ITERATIONS is exhausted
        without convergence.
        """
        algo = parse_moves("R U R' U'")

        # invert_moves alternates: original → inverted → original → ...
        # never converges; after 2 iterations mod_moves is back to the original
        with patch('cubing_algs.algorithm.MAX_ITERATIONS', 2):
            result = algo.transform(invert_moves, to_fixpoint=True)

        self.assertEqual(result, algo)

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

    def test_has_pauses(self) -> None:
        """Test has pauses."""
        algo = parse_moves("R U . R' U'")

        self.assertTrue(algo.has_pauses)

        algo = parse_moves("R U R' U'")

        self.assertFalse(algo.has_pauses)

    def test_has_times(self) -> None:
        """Test has timed moves."""
        algo = parse_moves("R@0.5 U R' U'")

        self.assertTrue(algo.has_times)

        algo = parse_moves("R U R' U'")

        self.assertFalse(algo.has_times)


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


class AlgorithmShowMixin:
    """Testing tools for Algorithm.show() output verification."""

    ANSI_RE = re.compile(r'\x1b\[[^m]*m')
    # Default palette masked background: '#444444' → rgb(68,68,68)
    MASKED_BG = '\x1b[48;2;68;68;68m'

    @staticmethod
    def show_output(algo: Algorithm,  # noqa: PLR0913
                    size: int = 3,
                    mode: str = '',
                    orientation: str = '',
                    layout: str = '', *,
                    impact_mask: bool = True) -> str:
        """
        Run algo.show() and capture stdout.

        Returns:
            Raw stdout output including ANSI escape codes.

        """
        buf = StringIO()
        with (
            patch('cubing_algs.display.vcube.USE_COLORS', new=True),
            redirect_stdout(buf),
        ):
            algo.show(
                size=size,
                mode=mode,
                orientation=orientation,
                layout=layout,
                impact_mask=impact_mask,
            )
        return buf.getvalue()

    def show_stripped(self, algo: Algorithm,  # noqa: PLR0913
                      size: int = 3,
                      mode: str = '',
                      orientation: str = '',
                      layout: str = '', *,
                      impact_mask: bool = True) -> str:
        """
        Run algo.show() and return output with ANSI codes stripped.

        Returns:
            Plain text output with face letters and spacing.

        """
        return self.ANSI_RE.sub(
            '',
            self.show_output(
                algo,
                size=size,
                mode=mode,
                orientation=orientation,
                layout=layout,
                impact_mask=impact_mask,
            ),
        )

    def show_grid(self, algo: Algorithm,  # noqa: PLR0913
                  size: int = 3,
                  mode: str = '',
                  orientation: str = '',
                  layout: str = '', *,
                  impact_mask: bool = True) -> str:
        """
        Run algo.show() and return a readable grid.

        Same layout as stripped output, but with case encoding:
        Uppercase = dimmed (masked), lowercase = bright (affected).

        Returns:
            Grid string with case-encoded mask information.

        """
        raw = self.show_output(
            algo,
            size=size,
            mode=mode,
            orientation=orientation,
            layout=layout,
            impact_mask=impact_mask,
        )

        i = 0
        result: list[str] = []
        is_masked = False

        while i < len(raw):
            if raw[i] == '\x1b':
                end = raw.index('m', i) + 1
                seq = raw[i:end]
                if seq.startswith('\x1b[48;2;'):
                    is_masked = seq == self.MASKED_BG
                i = end
            elif raw[i].isalpha():
                result.append(raw[i].upper() if is_masked else raw[i].lower())
                i += 1
            else:
                result.append(raw[i])
                i += 1
        return ''.join(result).rstrip('\n')


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class AlgorithmShowTestCase(AlgorithmShowMixin, unittest.TestCase):
    """Test cases for Algorithm.show without mask."""

    def test_show_returns_vcube(self) -> None:
        """Test show method returns VCube instance."""
        algo = Algorithm.parse_moves("R U R'")

        with redirect_stdout(StringIO()):
            result = algo.show()

        self.assertIsInstance(result, VCube)

    def test_show_renders_solved_cube(self) -> None:
        """Test show renders solved cube for empty algorithm."""
        output = self.show_stripped(Algorithm())

        expected = (
            '          U  U  U \n'
            '          U  U  U \n'
            '          U  U  U \n'
            ' L  L  L  F  F  F  R  R  R  B  B  B \n'
            ' L  L  L  F  F  F  R  R  R  B  B  B \n'
            ' L  L  L  F  F  F  R  R  R  B  B  B \n'
            '          D  D  D \n'
            '          D  D  D \n'
            '          D  D  D \n'
        )
        self.assertEqual(output, expected)

    def test_show_renders_r_move(self) -> None:
        """Test show renders single R move correctly."""
        output = self.show_stripped(
            Algorithm.parse_moves('R'),
        )

        expected = (
            '          U  U  F \n'
            '          U  U  F \n'
            '          U  U  F \n'
            ' L  L  L  F  F  D  R  R  R  U  B  B \n'
            ' L  L  L  F  F  D  R  R  R  U  B  B \n'
            ' L  L  L  F  F  D  R  R  R  U  B  B \n'
            '          D  D  B \n'
            '          D  D  B \n'
            '          D  D  B \n'
        )
        self.assertEqual(output, expected)

    def test_show_renders_r_u_r_prime(self) -> None:
        """Test show renders R U R' correctly."""
        output = self.show_stripped(
            Algorithm.parse_moves("R U R'"),
        )

        expected = (
            '          U  U  U \n'
            '          U  U  U \n'
            '          F  F  L \n'
            ' F  F  D  R  R  U  B  R  R  B  L  L \n'
            ' L  L  L  F  F  U  B  R  R  B  B  B \n'
            ' L  L  L  F  F  F  U  R  R  B  B  B \n'
            '          D  D  R \n'
            '          D  D  D \n'
            '          D  D  D \n'
        )
        self.assertEqual(output, expected)

    def test_show_oll_mode(self) -> None:
        """Test show renders OLL mode layout."""
        output = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            mode='oll',
        )

        expected = (
            '          l  l  B \n'
            '       f  u  u  U  R \n'
            '       f  u  U  U  R \n'
            '       d  f  f  l  b \n'
            '          r  r  u '
        )
        self.assertEqual(output, expected)

    def test_show_oll_mode_single_r(self) -> None:
        """Test show renders OLL mode for single R move."""
        output = self.show_grid(
            Algorithm.parse_moves('R'),
            mode='oll',
        )

        expected = (
            '          B  B  u \n'
            '       L  U  U  f  r \n'
            '       L  U  U  f  r \n'
            '       L  U  U  f  r \n'
            '          F  F  d '
        )
        self.assertEqual(output, expected)

    def test_show_strips_timing(self) -> None:
        """Test show strips timing from moves before applying."""
        output_timed = self.show_stripped(
            Algorithm.parse_moves('R@50 U@75'),
        )
        output_plain = self.show_stripped(
            Algorithm.parse_moves('R U'),
        )

        self.assertEqual(output_timed, output_plain)

    def test_show_orients_cube_to_uf(self) -> None:
        """Test show returns cube oriented to UF."""
        algo = Algorithm.parse_moves("R U R'")

        with redirect_stdout(StringIO()):
            result = algo.show()

        self.assertEqual(result.orientation, 'UF')


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class AlgorithmShowMaskTestCase(AlgorithmShowMixin, unittest.TestCase):
    """
    Test cases for Algorithm.show with impact mask.

    Grid notation: Uppercase = dimmed (masked),
    lowercase = bright (affected).
    """

    def test_show_with_mask_r_u_r_prime(self) -> None:
        """Test impact mask highlights affected facelets for R U R'."""
        grid = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            impact_mask=True,
        )

        expected = (
            '          u  u  U \n'
            '          u  U  U \n'
            '          f  f  l \n'
            ' f  f  d  r  r  u  b  R  R  B  l  l \n'
            ' L  L  L  F  F  u  b  R  R  B  B  B \n'
            ' L  L  L  F  F  f  u  R  R  B  B  B \n'
            '          D  D  r \n'
            '          D  D  D \n'
            '          D  D  D '
        )
        self.assertEqual(grid, expected)

    def test_show_without_mask_all_bright(self) -> None:
        """Test impact_mask=False renders all facelets bright."""
        grid = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            impact_mask=False,
        )

        self.assertTrue(
            all(c.islower() or not c.isalpha() for c in grid),
            f'Expected all bright facelets without mask, got:\n{grid}',
        )

    def test_show_with_mask_empty(self) -> None:
        """Test empty algorithm dims all facelets."""
        grid = self.show_grid(
            Algorithm(),
            impact_mask=True,
        )

        expected = (
            '          U  U  U \n'
            '          U  U  U \n'
            '          U  U  U \n'
            ' L  L  L  F  F  F  R  R  R  B  B  B \n'
            ' L  L  L  F  F  F  R  R  R  B  B  B \n'
            ' L  L  L  F  F  F  R  R  R  B  B  B \n'
            '          D  D  D \n'
            '          D  D  D \n'
            '          D  D  D '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_r_move(self) -> None:
        """Test impact mask highlights R-layer facelets only."""
        grid = self.show_grid(
            Algorithm.parse_moves('R'),
            impact_mask=True,
        )

        expected = (
            '          U  U  f \n'
            '          U  U  f \n'
            '          U  U  f \n'
            ' L  L  L  F  F  d  r  r  r  u  B  B \n'
            ' L  L  L  F  F  d  r  R  r  u  B  B \n'
            ' L  L  L  F  F  d  r  r  r  u  B  B \n'
            '          D  D  b \n'
            '          D  D  b \n'
            '          D  D  b '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_mse_moves(self) -> None:
        """Test impact mask highlights slice moves only."""
        grid = self.show_grid(
            Algorithm.parse_moves('M2 S2 E2'),
            impact_mask=True,
        )

        expected = (
            '          U  d  U \n'
            '          d  U  d \n'
            '          U  d  U \n'
            ' L  r  L  F  b  F  R  l  R  B  f  B \n'
            ' r  L  r  b  F  b  l  R  l  f  B  f \n'
            ' L  r  L  F  b  F  R  l  R  B  f  B \n'
            '          D  u  D \n'
            '          u  D  u \n'
            '          D  u  D '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r(self) -> None:
        """Test impact mask with y rotation prefix highlights R-layer only."""
        grid = self.show_grid(
            Algorithm.parse_moves('y R'),
            impact_mask=True,
        )

        expected = (
            '          U  U  r \n'
            '          U  U  r \n'
            '          U  U  r \n'
            ' F  F  F  R  R  d  b  b  b  u  L  L \n'
            ' F  F  F  R  R  d  b  B  b  u  L  L \n'
            ' F  F  F  R  R  d  b  b  b  u  L  L \n'
            '          D  D  l \n'
            '          D  D  l \n'
            '          D  D  l '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r_orientation_df(self) -> None:
        """
        Test impact mask with y rotation prefix highlights R-layer only,
        with custom DF orientation.
        """
        grid = self.show_grid(
            Algorithm.parse_moves('y R'),
            orientation='DF',
            impact_mask=True,
        )

        expected = (
            '          l  l  l \n'
            '          D  D  D \n'
            '          D  D  D \n'
            ' d  R  R  F  F  F  L  L  u  b  b  b \n'
            ' d  R  R  F  F  F  L  L  u  b  B  b \n'
            ' d  R  R  F  F  F  L  L  u  b  b  b \n'
            '          U  U  U \n'
            '          U  U  U \n'
            '          r  r  r '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r_orientation_uf(self) -> None:
        """
        Test impact mask with y rotation prefix highlights R-layer only,
        with custom UF orientation.
        """
        grid = self.show_grid(
            Algorithm.parse_moves('y R'),
            orientation='UF',
            impact_mask=True,
        )

        expected = (
            '          r  r  r \n'
            '          U  U  U \n'
            '          U  U  U \n'
            ' u  L  L  F  F  F  R  R  d  b  b  b \n'
            ' u  L  L  F  F  F  R  R  d  b  B  b \n'
            ' u  L  L  F  F  F  R  R  d  b  b  b \n'
            '          D  D  D \n'
            '          D  D  D \n'
            '          l  l  l '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r_u_r_prime(self) -> None:
        """Test impact mask with y rotation prefix for R U R'."""
        grid = self.show_grid(
            Algorithm.parse_moves("y R U R'"),
            impact_mask=True,
        )

        expected = (
            '          u  u  U \n'
            '          u  U  U \n'
            '          r  r  f \n'
            ' r  r  d  b  b  u  l  B  B  L  f  f \n'
            ' F  F  F  R  R  u  l  B  B  L  L  L \n'
            ' F  F  F  R  R  r  u  B  B  L  L  L \n'
            '          D  D  b \n'
            '          D  D  D \n'
            '          D  D  D '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r_u_r_prime_orientation_uf(self) -> None:
        """
        Test impact mask with y rotation prefix highlights R-layer only,
        with custom UF orientation.
        """
        grid = self.show_grid(
            Algorithm.parse_moves("y R U R'"),
            orientation='UF',
            impact_mask=True,
        )

        expected = (
            '          U  U  f \n'
            '          u  U  r \n'
            '          u  u  r \n'
            ' L  f  f  r  r  d  b  b  u  l  B  B \n'
            ' L  L  L  F  F  F  R  R  u  l  B  B \n'
            ' L  L  L  F  F  F  R  R  r  u  B  B \n'
            '          D  D  D \n'
            '          D  D  D \n'
            '          D  D  b '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_z2_pll_t(self) -> None:
        """Test impact mask with z2 rotation prefix for PLL T perm."""
        grid = self.show_grid(
            Algorithm.parse_moves("z2 R U R' U' R' F R2 U' R' U' R U R' F'"),
            impact_mask=True,
        )

        expected = (
            '          D  D  d \n'
            '          d  D  d \n'
            '          D  D  d \n'
            ' R  l  R  F  F  l  b  r  f  l  B  B \n'
            ' R  R  R  F  F  F  L  L  L  B  B  B \n'
            ' R  R  R  F  F  F  L  L  L  B  B  B \n'
            '          U  U  U \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_z2_oll_21_h(self) -> None:
        """Test impact mask with z2 rotation prefix for OLL 21 H."""
        grid = self.show_grid(
            Algorithm.parse_moves(
                "z2 F R U R' U' R U R' U' R U R' U' F'",
            ),
            impact_mask=True,
        )

        expected = (
            '          b  D  b \n'
            '          D  D  D \n'
            '          f  D  f \n'
            ' l  R  l  d  F  d  r  L  r  d  B  d \n'
            ' R  R  R  F  F  F  L  L  L  B  B  B \n'
            ' R  R  R  F  F  F  L  L  L  B  B  B \n'
            '          U  U  U \n'
            '          U  U  U \n'
            '          U  U  U '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_z2_oll_21_h_oll_mode(self) -> None:
        """Test impact mask with z2 OLL 21 H using OLL mode (top layout)."""
        grid = self.show_grid(
            Algorithm.parse_moves(
                "z2 F R U R' U' R U R' U' R U R' U' F'",
            ),
            mode='oll',
            impact_mask=True,
        )

        expected = (
            '          d  B  d \n'
            '       l  b  D  b  r \n'
            '       R  D  D  D  L \n'
            '       l  f  D  f  r \n'
            '          d  F  d '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_z2_oll_21_h_oll_linear(self) -> None:
        """Test impact mask with z2 OLL 21 H using OLL mode, linear layout."""
        grid = self.show_grid(
            Algorithm.parse_moves(
                "z2 F R U R' U' R U R' U' R U R' U' F'",
            ),
            mode='oll',
            layout='linear',
            impact_mask=True,
        )

        expected = (
            ' b  D  b   r  L  r   d  F  d   U  U  U   l  R  l   d  B  d \n'
            ' D  D  D   L  L  L   F  F  F   U  U  U   R  R  R   B  B  B \n'
            ' f  D  f   L  L  L   F  F  F   U  U  U   R  R  R   B  B  B '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_z2_oll_21_h_oll_extended(self) -> None:
        """Test impact mask with z2 OLL 21 H using OLL mode, extended layout."""
        grid = self.show_grid(
            Algorithm.parse_moves(
                "z2 F R U R' U' R U R' U' R U R' U' F'",
            ),
            mode='oll',
            layout='extended',
            impact_mask=True,
        )

        expected = (
            '                d  b  d \n'
            '             l  b  D  b  r \n'
            '             r  D  D  D  l \n'
            '             l  f  D  f  r \n'
            '    b  d  f                 f  d  b  b  d  b \n'
            ' d  l  R  l     d  F  d     r  L  r  d  B  d  l \n'
            ' b  R  R  R     F  F  F     L  L  L  B  B  B  r \n'
            ' b  R  R  R     F  F  F     L  L  L  B  B  B  r \n'
            '    u  u  u                 u  u  u  u  u  u \n'
            '             r  U  U  U  l \n'
            '             r  U  U  U  l \n'
            '             r  U  U  U  l \n'
            '                b  b  b '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class Algorithm2x2x2ShowMaskTestCase(AlgorithmShowMixin, unittest.TestCase):
    """
    Test cases for Algorithm.show with impact mask on 2x2x2.

    Grid notation: Uppercase = dimmed (masked),
    lowercase = bright (affected).
    """

    def test_show_with_mask_r_move(self) -> None:
        """Test impact mask highlights R-layer facelets only."""
        grid = self.show_grid(
            Algorithm.parse_moves('R'),
            size=2,
            impact_mask=True,
        )
        expected = (
            '       U  f \n'
            '       U  f \n'
            ' L  L  F  d  r  r  u  B \n'
            ' L  L  F  d  r  r  u  B \n'
            '       D  b \n'
            '       D  b '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_r_u_r_prime(self) -> None:
        """Test impact mask highlights affected facelets for R U R'."""
        grid = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            size=2,
            impact_mask=True,
        )
        expected = (
            '       u  U \n'
            '       f  l \n'
            ' f  d  r  u  b  R  B  l \n'
            ' L  L  F  f  u  R  B  B \n'
            '       D  r \n'
            '       D  D '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r(self) -> None:
        """Test impact mask with y rotation prefix on 2x2x2."""
        grid = self.show_grid(
            Algorithm.parse_moves('y R'),
            size=2,
            impact_mask=True,
        )
        expected = (
            '       U  r \n'
            '       U  r \n'
            ' F  F  R  d  b  b  u  L \n'
            ' F  F  R  d  b  b  u  L \n'
            '       D  l \n'
            '       D  l '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r_u_r_prime(self) -> None:
        """Test impact mask with y rotation prefix for R U R' on 2x2x2."""
        grid = self.show_grid(
            Algorithm.parse_moves("y R U R'"),
            size=2,
            impact_mask=True,
        )
        expected = (
            '       u  U \n'
            '       r  f \n'
            ' r  d  b  u  l  B  L  f \n'
            ' F  F  R  r  u  B  L  L \n'
            '       D  b \n'
            '       D  D '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class Algorithm4x4x4ShowMaskTestCase(AlgorithmShowMixin, unittest.TestCase):
    """
    Test cases for Algorithm.show with impact mask on 4x4x4.

    Grid notation: Uppercase = dimmed (masked),
    lowercase = bright (affected).
    """

    def test_show_with_mask_r_move(self) -> None:
        """Test impact mask highlights R-layer facelets only."""
        grid = self.show_grid(
            Algorithm.parse_moves('R'),
            size=4,
            impact_mask=True,
        )
        expected = (
            '             U  U  U  f \n'
            '             U  U  U  f \n'
            '             U  U  U  f \n'
            '             U  U  U  f \n'
            ' L  L  L  L  F  F  F  d  r  r  r  r  u  B  B  B \n'
            ' L  L  L  L  F  F  F  d  r  r  r  r  u  B  B  B \n'
            ' L  L  L  L  F  F  F  d  r  r  r  r  u  B  B  B \n'
            ' L  L  L  L  F  F  F  d  r  r  r  r  u  B  B  B \n'
            '             D  D  D  b \n'
            '             D  D  D  b \n'
            '             D  D  D  b \n'
            '             D  D  D  b '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_r_u_r_prime(self) -> None:
        """Test impact mask highlights affected facelets for R U R'."""
        grid = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            size=4,
            impact_mask=True,
        )
        expected = (
            '             u  u  u  U \n'
            '             u  u  u  U \n'
            '             u  u  u  U \n'
            '             f  f  f  l \n'
            ' f  f  f  d  r  r  r  u  b  R  R  R  B  l  l  l \n'
            ' L  L  L  L  F  F  F  u  b  R  R  R  B  B  B  B \n'
            ' L  L  L  L  F  F  F  u  b  R  R  R  B  B  B  B \n'
            ' L  L  L  L  F  F  F  f  u  R  R  R  B  B  B  B \n'
            '             D  D  D  r \n'
            '             D  D  D  D \n'
            '             D  D  D  D \n'
            '             D  D  D  D '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r(self) -> None:
        """Test impact mask with y rotation prefix on 4x4x4."""
        grid = self.show_grid(
            Algorithm.parse_moves('y R'),
            size=4,
            impact_mask=True,
        )
        expected = (
            '             U  U  U  r \n'
            '             U  U  U  r \n'
            '             U  U  U  r \n'
            '             U  U  U  r \n'
            ' F  F  F  F  R  R  R  d  b  b  b  b  u  L  L  L \n'
            ' F  F  F  F  R  R  R  d  b  b  b  b  u  L  L  L \n'
            ' F  F  F  F  R  R  R  d  b  b  b  b  u  L  L  L \n'
            ' F  F  F  F  R  R  R  d  b  b  b  b  u  L  L  L \n'
            '             D  D  D  l \n'
            '             D  D  D  l \n'
            '             D  D  D  l \n'
            '             D  D  D  l '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r_u_r_prime(self) -> None:
        """Test impact mask with y rotation prefix for R U R' on 4x4x4."""
        grid = self.show_grid(
            Algorithm.parse_moves("y R U R'"),
            size=4,
            impact_mask=True,
        )
        expected = (
            '             u  u  u  U \n'
            '             u  u  u  U \n'
            '             u  u  u  U \n'
            '             r  r  r  f \n'
            ' r  r  r  d  b  b  b  u  l  B  B  B  L  f  f  f \n'
            ' F  F  F  F  R  R  R  u  l  B  B  B  L  L  L  L \n'
            ' F  F  F  F  R  R  R  u  l  B  B  B  L  L  L  L \n'
            ' F  F  F  F  R  R  R  r  u  B  B  B  L  L  L  L \n'
            '             D  D  D  b \n'
            '             D  D  D  D \n'
            '             D  D  D  D \n'
            '             D  D  D  D '
        )
        self.assertEqual(grid, expected)


@patch('cubing_algs.display.vcube.DEFAULT_PALETTE', 'default')
class Algorithm5x5x5ShowMaskTestCase(AlgorithmShowMixin, unittest.TestCase):
    """
    Test cases for Algorithm.show with impact mask on 5x5x5.

    Grid notation: Uppercase = dimmed (masked),
    lowercase = bright (affected).
    """

    def test_show_with_mask_r_move(self) -> None:
        """Test impact mask highlights R-layer facelets only."""
        grid = self.show_grid(
            Algorithm.parse_moves('R'),
            size=5,
            impact_mask=True,
        )
        expected = (
            '                U  U  U  U  f \n'
            '                U  U  U  U  f \n'
            '                U  U  U  U  f \n'
            '                U  U  U  U  f \n'
            '                U  U  U  U  f \n'
            ' L  L  L  L  L  F  F  F  F  d  r  r  r  r  r  u  B  B  B  B \n'
            ' L  L  L  L  L  F  F  F  F  d  r  r  r  r  r  u  B  B  B  B \n'
            ' L  L  L  L  L  F  F  F  F  d  r  r  R  r  r  u  B  B  B  B \n'
            ' L  L  L  L  L  F  F  F  F  d  r  r  r  r  r  u  B  B  B  B \n'
            ' L  L  L  L  L  F  F  F  F  d  r  r  r  r  r  u  B  B  B  B \n'
            '                D  D  D  D  b \n'
            '                D  D  D  D  b \n'
            '                D  D  D  D  b \n'
            '                D  D  D  D  b \n'
            '                D  D  D  D  b '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_r_u_r_prime(self) -> None:
        """Test impact mask highlights affected facelets for R U R'."""
        grid = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            size=5,
            impact_mask=True,
        )
        expected = (
            '                u  u  u  u  U \n'
            '                u  u  u  u  U \n'
            '                u  u  U  u  U \n'
            '                u  u  u  u  U \n'
            '                f  f  f  f  l \n'
            ' f  f  f  f  d  r  r  r  r  u  b  R  R  R  R  B  l  l  l  l \n'
            ' L  L  L  L  L  F  F  F  F  u  b  R  R  R  R  B  B  B  B  B \n'
            ' L  L  L  L  L  F  F  F  F  u  b  R  R  R  R  B  B  B  B  B \n'
            ' L  L  L  L  L  F  F  F  F  u  b  R  R  R  R  B  B  B  B  B \n'
            ' L  L  L  L  L  F  F  F  F  f  u  R  R  R  R  B  B  B  B  B \n'
            '                D  D  D  D  r \n'
            '                D  D  D  D  D \n'
            '                D  D  D  D  D \n'
            '                D  D  D  D  D \n'
            '                D  D  D  D  D '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r(self) -> None:
        """Test impact mask with y rotation prefix on 5x5x5."""
        grid = self.show_grid(
            Algorithm.parse_moves('y R'),
            size=5,
            impact_mask=True,
        )
        expected = (
            '                U  U  U  U  r \n'
            '                U  U  U  U  r \n'
            '                U  U  U  U  r \n'
            '                U  U  U  U  r \n'
            '                U  U  U  U  r \n'
            ' F  F  F  F  F  R  R  R  R  d  b  b  b  b  b  u  L  L  L  L \n'
            ' F  F  F  F  F  R  R  R  R  d  b  b  b  b  b  u  L  L  L  L \n'
            ' F  F  F  F  F  R  R  R  R  d  b  b  B  b  b  u  L  L  L  L \n'
            ' F  F  F  F  F  R  R  R  R  d  b  b  b  b  b  u  L  L  L  L \n'
            ' F  F  F  F  F  R  R  R  R  d  b  b  b  b  b  u  L  L  L  L \n'
            '                D  D  D  D  l \n'
            '                D  D  D  D  l \n'
            '                D  D  D  D  l \n'
            '                D  D  D  D  l \n'
            '                D  D  D  D  l '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_y_r_u_r_prime(self) -> None:
        """Test impact mask with y rotation prefix for R U R' on 5x5x5."""
        grid = self.show_grid(
            Algorithm.parse_moves("y R U R'"),
            size=5,
            impact_mask=True,
        )
        expected = (
            '                u  u  u  u  U \n'
            '                u  u  u  u  U \n'
            '                u  u  U  u  U \n'
            '                u  u  u  u  U \n'
            '                r  r  r  r  f \n'
            ' r  r  r  r  d  b  b  b  b  u  l  B  B  B  B  L  f  f  f  f \n'
            ' F  F  F  F  F  R  R  R  R  u  l  B  B  B  B  L  L  L  L  L \n'
            ' F  F  F  F  F  R  R  R  R  u  l  B  B  B  B  L  L  L  L  L \n'
            ' F  F  F  F  F  R  R  R  R  u  l  B  B  B  B  L  L  L  L  L \n'
            ' F  F  F  F  F  R  R  R  R  r  u  B  B  B  B  L  L  L  L  L \n'
            '                D  D  D  D  b \n'
            '                D  D  D  D  D \n'
            '                D  D  D  D  D \n'
            '                D  D  D  D  D \n'
            '                D  D  D  D  D '
        )
        self.assertEqual(grid, expected)


class AlgorithmImpactsTestCase(unittest.TestCase):
    """Test cases for the Algorithm.impacts method."""

    def test_impacts_method_returns_impact_data(self) -> None:
        """Test impacts method returns ImpactData."""
        algo = Algorithm.parse_moves("R U R' U'")
        impacts = algo.impacts()

        self.assertIsInstance(impacts, ImpactData)

    def test_impacts_raises_on_too_small_cube_size(self) -> None:
        """Test impacts raises InvalidCubeSizeError for undersized cube."""
        algo = Algorithm.parse_moves('3Rw')

        with self.assertRaises(InvalidCubeSizeError):
            algo.impacts(size=3)

    def test_get_cube_and_impact_mask_raises_on_too_small_cube_size(
            self,
    ) -> None:
        """Test get_cube_and_impact_mask raises for undersized cube."""
        algo = Algorithm.parse_moves('3Rw')

        with self.assertRaises(InvalidCubeSizeError):
            algo.get_cube_and_impact_mask(size=3)

    def test_validate_cube_size_accepts_valid_size(self) -> None:
        """Test validate_cube_size does not raise for valid size."""
        algo = Algorithm.parse_moves("R U R' U'")

        try:
            algo.validate_cube_size(3)
        except InvalidCubeSizeError:
            self.fail('validate_cube_size raised unexpectedly')

    def test_validate_cube_size_raises_on_too_small(self) -> None:
        """Test validate_cube_size raises for undersized cube."""
        algo = Algorithm.parse_moves('3Rw')

        with self.assertRaises(InvalidCubeSizeError):
            algo.validate_cube_size(3)


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


class AlgorithmImageTestCase(unittest.TestCase):
    """Tests for Algorithm.image() method."""

    def test_returns_svg(self) -> None:
        """Test that image() returns an SVG string."""
        algo = Algorithm.parse_moves("R U R' U'")
        result = algo.image()
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith('<svg'))
        self.assertTrue(result.endswith('</svg>'))

    def test_matches_vcube_image(self) -> None:
        """Test that Algorithm.image() matches VCube.image()."""
        algo = Algorithm.parse_moves("R U R' U'")
        cube = VCube()
        cube.rotate(algo)
        self.assertEqual(
            algo.image(impact_mask=False),
            cube.image(),
        )

    def test_empty_algorithm(self) -> None:
        """Test rendering an empty algorithm."""
        algo = Algorithm()
        result = algo.image()
        self.assertTrue(result.startswith('<svg'))

    def test_3d_view(self) -> None:
        """Test 3d view rendering."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(layout='3d')
        self.assertTrue(result.startswith('<svg'))

    def test_top_view(self) -> None:
        """Test top view rendering."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(layout='top')
        self.assertTrue(result.startswith('<svg'))
        self.assertIn('class="face-U"', result)

    def test_custom_size(self) -> None:
        """Test custom image size."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(image_size=300)
        self.assertIn('width="300"', result)
        self.assertIn('height="300"', result)

    def test_size_parameter(self) -> None:
        """Test explicit cube size parameter."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(size=2)
        self.assertTrue(result.startswith('<svg'))

    def test_custom_rotation(self) -> None:
        """Test custom rotation produces different SVG."""
        algo = Algorithm.parse_moves('R')
        default = algo.image()
        rotated = algo.image(rotation='y90')
        self.assertNotEqual(default, rotated)

    def test_custom_distance(self) -> None:
        """Test custom camera distance."""
        algo = Algorithm.parse_moves('R')
        default = algo.image()
        closer = algo.image(distance=5.0)
        self.assertNotEqual(default, closer)


class AlgorithmToDictTestCase(unittest.TestCase):
    """Tests for the Algorithm.to_dict method."""

    def test_expected_keys(self) -> None:
        """to_dict returns every documented top-level key."""
        algo = Algorithm.parse_moves("R U R' U'")
        result = algo.to_dict()
        self.assertEqual(
            set(result),
            {
                'moves', 'cycles', 'min_cube_size',
                'is_standard', 'is_sign',
                'has_rotations', 'has_internal_rotations',
                'has_pauses', 'has_times',
                'metrics', 'ergonomics', 'structure',
                'memory', 'impacts',
            },
        )

    def test_moves_is_string(self) -> None:
        """Moves entry is the stringified algorithm."""
        algo = Algorithm.parse_moves("R U R' U'")
        self.assertEqual(algo.to_dict()['moves'], "R U R' U'")

    def test_nested_are_plain_dicts(self) -> None:
        """Data containers are flattened to plain dicts."""
        algo = Algorithm.parse_moves("R U R' U' F R U R' U' F'")
        result = algo.to_dict()
        for key in ('metrics', 'ergonomics', 'structure', 'memory', 'impacts'):
            self.assertIsInstance(result[key], dict)

    def test_json_serializable(self) -> None:
        """The full dict is JSON-serializable."""
        algo = Algorithm.parse_moves("R U R' U' F R U R' U' F'")
        payload = json.dumps(algo.to_dict())
        self.assertGreater(len(payload), 0)

    def test_impacts_cube_is_facelets_string(self) -> None:
        """VCube inside impacts is flattened to its facelets state string."""
        algo = Algorithm.parse_moves("R U R' U'")
        result = algo.to_dict()
        cube = result['impacts']['cube']
        self.assertIsInstance(cube, str)
        self.assertEqual(len(cube), 54)

    def test_size_parameter_validates(self) -> None:
        """to_dict propagates cube-size validation from impacts."""
        algo = Algorithm.parse_moves('3Rw')
        with self.assertRaises(InvalidCubeSizeError):
            algo.to_dict(size=2)

    def test_size_parameter_accepted(self) -> None:
        """to_dict accepts a custom cube size."""
        algo = Algorithm.parse_moves("R U R' U'")
        result = algo.to_dict(size=4)
        self.assertEqual(len(result['impacts']['cube']), 6 * 4 * 4)
