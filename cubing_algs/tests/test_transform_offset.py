"""Tests for offset transformation functions."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.offset import PARSED_OFFSET_TABLES
from cubing_algs.transform.offset import compose_offset_tables
from cubing_algs.transform.offset import offset_moves
from cubing_algs.transform.offset import offset_x2_moves
from cubing_algs.transform.offset import offset_x_moves
from cubing_algs.transform.offset import offset_xprime_moves
from cubing_algs.transform.offset import offset_y2_moves
from cubing_algs.transform.offset import offset_y_moves
from cubing_algs.transform.offset import offset_yprime_moves
from cubing_algs.transform.offset import offset_z2_moves
from cubing_algs.transform.offset import offset_z_moves
from cubing_algs.transform.offset import offset_zprime_moves
from cubing_algs.transform.offset import rotate
from cubing_algs.transform.offset import rotate_move


class TransformOffsetTestCase(unittest.TestCase):
    """Tests for offset transformations that apply cube rotations."""

    def test_offset_x_moves(self) -> None:
        """Test offset x moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R B R' B'")

        result = offset_x_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_offset_x_moves_wide_standard(self) -> None:
        """Test offset x moves wide standard."""
        provide = parse_moves("R U Rw' Uw'")
        expect = parse_moves("R B Rw' Bw'")

        result = offset_x_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_offset_x_moves_wide_sign(self) -> None:
        """Test offset x moves wide sign."""
        provide = parse_moves("R U r' u'")
        expect = parse_moves("R B r' b'")

        result = offset_x_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_offset_x2_moves(self) -> None:
        """Test offset x2 moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R D R' D'")

        self.assertEqual(
            offset_x2_moves(provide),
            expect,
        )

    def test_offset_xprime_moves(self) -> None:
        """Test offset xprime moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R F R' F'")

        self.assertEqual(
            offset_xprime_moves(provide),
            expect,
        )

    def test_offset_y_moves(self) -> None:
        """Test offset y moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("F U F' U'")

        self.assertEqual(
            offset_y_moves(provide),
            expect,
        )

    def test_offset_y2_moves(self) -> None:
        """Test offset y2 moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("L U L' U'")

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

    def test_offset_yprime_moves(self) -> None:
        """Test offset yprime moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("B U B' U'")

        self.assertEqual(
            offset_yprime_moves(provide),
            expect,
        )

    def test_offset_z_moves(self) -> None:
        """Test offset z moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("D R D' R'")

        self.assertEqual(
            offset_z_moves(provide),
            expect,
        )

    def test_offset_z2_moves(self) -> None:
        """Test offset z2 moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("L D L' D'")

        self.assertEqual(
            offset_z2_moves(provide),
            expect,
        )

    def test_offset_zprime_moves(self) -> None:
        """Test offset zprime moves."""
        provide = parse_moves("R U R' U'")
        expect = parse_moves("U L U' L'")

        self.assertEqual(
            offset_zprime_moves(provide),
            expect,
        )

    def test_offset_big_moves(self) -> None:
        """Test offset big moves."""
        provide = parse_moves('3R')
        expect = parse_moves('3L')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves('3R2')
        expect = parse_moves('3L2')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves("3R'")
        expect = parse_moves("3L'")

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

    def test_offset_big_moves_timed(self) -> None:
        """Test offset big moves timed."""
        provide = parse_moves('3R@100')
        expect = parse_moves('3L@100')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves('3R2@100')
        expect = parse_moves('3L2@100')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves("3R'@100")
        expect = parse_moves("3L'@100")

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

    def test_offset_big_moves_timed_with_pauses(self) -> None:
        """Test offset big moves timed with pauses."""
        provide = parse_moves('.@50 3R@100 .@150')
        expect = parse_moves('.@50 3L@100 .@150')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )


class RotateMoveTestCase(unittest.TestCase):
    """Tests for rotate_move with parsed offset tables."""

    def test_rotate_move_basic(self) -> None:
        """Test basic move rotation through x' table."""
        table = PARSED_OFFSET_TABLES['x']
        move = Move('U')
        result = rotate_move(move, table)
        self.assertEqual(str(result), 'F')

    def test_rotate_move_inverted(self) -> None:
        """Test inverted move rotation."""
        table = PARSED_OFFSET_TABLES['x']
        move = Move("U'")
        result = rotate_move(move, table)
        self.assertEqual(str(result), "F'")

    def test_rotate_move_double(self) -> None:
        """Test double move rotation."""
        table = PARSED_OFFSET_TABLES['x']
        move = Move('U2')
        result = rotate_move(move, table)
        self.assertEqual(str(result), 'F2')

    def test_rotate_move_wide(self) -> None:
        """Test wide move rotation."""
        table = PARSED_OFFSET_TABLES['x']
        move = Move('Uw')
        result = rotate_move(move, table)
        self.assertEqual(str(result), 'Fw')

    def test_rotate_move_not_in_table(self) -> None:
        """Test move not in table is returned unchanged."""
        move = Move('R')
        result = rotate_move(move, {})
        self.assertEqual(str(result), 'R')

    def test_rotate_move_timed(self) -> None:
        """Test timed move rotation preserves timing."""
        table = PARSED_OFFSET_TABLES['x']
        move = Move('U@100')
        result = rotate_move(move, table)
        self.assertEqual(str(result), 'F@100')

    def test_rotate_move_sign(self) -> None:
        """Test sign move rotation preserves sign notation."""
        table = PARSED_OFFSET_TABLES['x']
        move = Move('u')
        result = rotate_move(move, table)
        self.assertEqual(str(result), 'f')


class ComposeOffsetTablesInOffsetTestCase(unittest.TestCase):
    """Tests for compose_offset_tables used within offset module."""

    def test_compose_x_twice_equals_x2(self) -> None:
        """Test composing x with x gives same result as x2 offset."""
        x_table = PARSED_OFFSET_TABLES['x']
        composed = compose_offset_tables(x_table, x_table)

        algo = parse_moves("R U R' U'")
        from_composed = Algorithm(rotate_move(m, composed) for m in algo)
        from_offset = offset_x2_moves(algo)

        self.assertEqual(from_composed, from_offset)

    def test_compose_passthrough_unmapped_key(self) -> None:
        """Test keys in t1 whose mapped value is not in t2 pass through."""
        t1: dict[str, tuple[str, bool]] = {'U': ('X', False)}
        t2: dict[str, tuple[str, bool]] = {'R': ('L', False)}

        composed = compose_offset_tables(t1, t2)

        self.assertEqual(composed['U'], ('X', False))
        self.assertEqual(composed['R'], ('L', False))

    def test_compose_disjoint_tables(self) -> None:
        """Test keys only in t2 are added to the result."""
        t1: dict[str, tuple[str, bool]] = {'U': ('D', True)}
        t2: dict[str, tuple[str, bool]] = {'R': ('L', False)}

        composed = compose_offset_tables(t1, t2)

        self.assertEqual(composed['U'], ('D', True))
        self.assertEqual(composed['R'], ('L', False))


class RotateTestCase(unittest.TestCase):
    """Tests for the rotate function."""

    def test_rotate_single_rotation(self) -> None:
        """Test rotate applies a single rotation to an algorithm."""
        algo = parse_moves("R U R' U'")
        result = rotate(algo, "x'")
        self.assertEqual(result, parse_moves("R B R' B'"))


class OffsetMovesEdgeCasesTestCase(unittest.TestCase):
    """Tests for offset_moves edge cases."""

    def test_offset_moves_count_zero(self) -> None:
        """Test offset_moves with count=0 returns the algorithm unchanged."""
        algo = parse_moves("R U R' U'")
        result = offset_moves(algo, 'x', count=0)
        self.assertIs(result, algo)

    def test_offset_moves_empty_algorithm(self) -> None:
        """Test offset_moves with empty algorithm returns it unchanged."""
        algo = Algorithm()
        result = offset_moves(algo, 'x', count=2)
        self.assertIs(result, algo)
