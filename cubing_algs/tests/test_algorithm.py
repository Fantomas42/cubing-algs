"""Tests for the Algorithm class."""
import re
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import ErgonomicsData
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
    def show_output(algo: Algorithm,
                    mode: str = '', *,
                    impact_mask: bool = True) -> str:
        """
        Run algo.show() and capture stdout.

        Returns:
            Raw stdout output including ANSI escape codes.

        """
        buf = StringIO()
        with redirect_stdout(buf):
            algo.show(mode=mode, impact_mask=impact_mask)
        return buf.getvalue()

    def show_stripped(self, algo: Algorithm,
                      mode: str = '', *,
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
                mode=mode,
                impact_mask=impact_mask,
            ),
        )

    def show_grid(self, algo: Algorithm,
                  mode: str = '', *,
                  impact_mask: bool = True) -> str:
        """
        Run algo.show() and return a readable grid.

        Same layout as stripped output, but with case encoding:
        Uppercase = bright (affected), lowercase = dimmed (masked).

        Returns:
            Grid string with case-encoded mask information.

        """
        raw = self.show_output(
            algo,
            mode=mode,
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
                result.append(raw[i].lower() if is_masked else raw[i].upper())
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
        output = self.show_stripped(
            Algorithm.parse_moves("R U R'"),
            mode='oll',
        )

        expected = (
            '          B  B  B \n'
            '       R  D  D  D  L \n'
            '       R  D  D  D  L \n'
            '       U  R  D  D  L \n'
            '          F  F  F \n'
        )
        self.assertEqual(output, expected)

    def test_show_oll_mode_single_r(self) -> None:
        """Test show renders OLL mode for single R move."""
        output = self.show_stripped(
            Algorithm.parse_moves('R'),
            mode='oll',
        )

        expected = (
            '          U  B  B \n'
            '       R  B  D  D  L \n'
            '       R  B  D  D  L \n'
            '       R  B  D  D  L \n'
            '          D  F  F \n'
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

    Grid notation: Uppercase = bright (affected),
    lowercase = dimmed (masked).
    """

    def test_show_with_mask_r_u_r_prime(self) -> None:
        """Test impact mask highlights affected facelets for R U R'."""
        grid = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            impact_mask=True,
        )

        expected = (
            '          U  U  u \n'
            '          U  u  u \n'
            '          F  F  L \n'
            ' F  F  D  R  R  U  B  r  r  b  L  L \n'
            ' l  l  l  f  f  U  B  r  r  b  b  b \n'
            ' l  l  l  f  f  F  U  r  r  b  b  b \n'
            '          d  d  R \n'
            '          d  d  d \n'
            '          d  d  d '
        )
        self.assertEqual(grid, expected)

    def test_show_without_mask_all_bright(self) -> None:
        """Test impact_mask=False renders all facelets bright."""
        grid = self.show_grid(
            Algorithm.parse_moves("R U R'"),
            impact_mask=False,
        )

        self.assertTrue(
            all(c.isupper() or not c.isalpha() for c in grid),
            f'Expected all bright facelets without mask, got:\n{grid}',
        )

    def test_show_with_mask_empty(self) -> None:
        """Test empty algorithm dims all facelets."""
        grid = self.show_grid(
            Algorithm(),
            impact_mask=True,
        )

        expected = (
            '          u  u  u \n'
            '          u  u  u \n'
            '          u  u  u \n'
            ' l  l  l  f  f  f  r  r  r  b  b  b \n'
            ' l  l  l  f  f  f  r  r  r  b  b  b \n'
            ' l  l  l  f  f  f  r  r  r  b  b  b \n'
            '          d  d  d \n'
            '          d  d  d \n'
            '          d  d  d '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_r_move(self) -> None:
        """Test impact mask highlights R-layer facelets only."""
        grid = self.show_grid(
            Algorithm.parse_moves('R'),
            impact_mask=True,
        )

        expected = (
            '          u  u  F \n'
            '          u  u  F \n'
            '          u  u  F \n'
            ' l  l  l  f  f  D  R  R  R  U  b  b \n'
            ' l  l  l  f  f  D  R  r  R  U  b  b \n'
            ' l  l  l  f  f  D  R  R  R  U  b  b \n'
            '          d  d  B \n'
            '          d  d  B \n'
            '          d  d  B '
        )
        self.assertEqual(grid, expected)

    def test_show_with_mask_mse_moves(self) -> None:
        """Test impact mask highlights slice moves only."""
        grid = self.show_grid(
            Algorithm.parse_moves('M2 S2 E2'),
            impact_mask=True,
        )

        expected = (
            '          u  D  u \n'
            '          D  u  D \n'
            '          u  D  u \n'
            ' l  R  l  f  B  f  r  L  r  b  F  b \n'
            ' R  l  R  B  f  B  L  r  L  F  b  F \n'
            ' l  R  l  f  B  f  r  L  r  b  F  b \n'
            '          d  U  d \n'
            '          U  d  U \n'
            '          d  U  d '
        )
        self.assertEqual(grid, expected)


class AlgorithmImpactsTestCase(unittest.TestCase):
    """Test cases for the Algorithm.impacts property."""

    def test_impacts_property_returns_impact_data(self) -> None:
        """Test impacts property returns ImpactData."""
        algo = Algorithm.parse_moves("R U R' U'")
        impacts = algo.impacts

        self.assertIsInstance(impacts, ImpactData)


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

    def test_matches_render_cube(self) -> None:
        """Test that image() matches render_cube() output."""
        from cubing_algs.display.image import render_cube  # noqa: PLC0415

        algo = Algorithm.parse_moves("R U R' U'")
        self.assertEqual(algo.image(), render_cube(algo))

    def test_matches_vcube_image(self) -> None:
        """Test that Algorithm.image() matches VCube.image()."""
        algo = Algorithm.parse_moves("R U R' U'")
        cube = VCube()
        cube.rotate(algo)
        self.assertEqual(algo.image(), cube.image())

    def test_empty_algorithm(self) -> None:
        """Test rendering an empty algorithm."""
        algo = Algorithm()
        result = algo.image()
        self.assertTrue(result.startswith('<svg'))

    def test_3d_view(self) -> None:
        """Test 3d view rendering."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(view='3d')
        self.assertTrue(result.startswith('<svg'))

    def test_top_view(self) -> None:
        """Test top view rendering."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(view='top')
        self.assertTrue(result.startswith('<svg'))
        self.assertIn('class="face-U"', result)

    def test_custom_size(self) -> None:
        """Test custom image size."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(size=300)
        self.assertIn('width="300"', result)
        self.assertIn('height="300"', result)

    def test_cube_size_parameter(self) -> None:
        """Test explicit cube_size parameter."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(cube_size=2)
        self.assertTrue(result.startswith('<svg'))

    def test_custom_rotation(self) -> None:
        """Test custom rotation produces different SVG."""
        algo = Algorithm.parse_moves('R')
        default = algo.image()
        rotated = algo.image(rotation='y90')
        self.assertNotEqual(default, rotated)

    def test_custom_cube_color(self) -> None:
        """Test custom cube color."""
        algo = Algorithm.parse_moves('R')
        result = algo.image(cube_color='#ff0000')
        self.assertIn('#ff0000', result)

    def test_custom_distance(self) -> None:
        """Test custom camera distance."""
        algo = Algorithm.parse_moves('R')
        default = algo.image()
        closer = algo.image(distance=5.0)
        self.assertNotEqual(default, closer)
