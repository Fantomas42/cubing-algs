"""Tests for algorithm translation transformation functions."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.offset import PARSED_OFFSET_TABLES
from cubing_algs.transform.offset import compose_offset_tables
from cubing_algs.transform.offset import offset_x2_moves
from cubing_algs.transform.offset import rotate_move
from cubing_algs.transform.translate import translate_moves
from cubing_algs.transform.translate import translate_pov_moves


class ComposeOffsetTablesTestCase(unittest.TestCase):
    """Tests for compose_offset_tables."""

    def test_compose_with_empty(self) -> None:
        """Composing with an empty table returns the other table."""
        table = PARSED_OFFSET_TABLES["x'"]

        self.assertEqual(compose_offset_tables({}, table), table)
        self.assertEqual(compose_offset_tables(table, {}), table)

    def test_compose_identity(self) -> None:
        """Composing two empty tables returns empty."""
        self.assertEqual(compose_offset_tables({}, {}), {})

    def test_compose_chained_equals_double(self) -> None:
        """Composing x with x equals x2 (applied twice)."""
        x_table = PARSED_OFFSET_TABLES['x']
        composed = compose_offset_tables(x_table, x_table)

        alg = parse_moves('R U F D L B M S E')
        expected = offset_x2_moves(alg)

        result = Algorithm([rotate_move(m, composed) for m in alg])

        self.assertEqual(result, expected)

    def test_compose_preserves_flip(self) -> None:
        """Direction flips compose via XOR."""
        t1: dict[str, tuple[str, bool]] = {'S': ('E', True)}
        t2: dict[str, tuple[str, bool]] = {'E': ('S', True)}

        composed = compose_offset_tables(t1, t2)

        self.assertEqual(composed['S'], ('S', False))

    def test_compose_disjoint_tables(self) -> None:
        """Disjoint tables merge all entries."""
        t1: dict[str, tuple[str, bool]] = {'U': ('D', False)}
        t2: dict[str, tuple[str, bool]] = {'R': ('L', False)}

        composed = compose_offset_tables(t1, t2)

        self.assertEqual(composed['U'], ('D', False))
        self.assertEqual(composed['R'], ('L', False))


class RotateMoveTestCase(unittest.TestCase):
    """Tests for rotate_move."""

    def test_unmapped_move_unchanged(self) -> None:
        """Move not in table passes through unchanged."""
        move = Move('R')
        table: dict[str, tuple[str, bool]] = {'U': ('D', False)}

        self.assertEqual(rotate_move(move, table), move)

    def test_clockwise_no_flip(self) -> None:
        """Clockwise move remapped without flip stays clockwise."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', False)}

        result = rotate_move(Move('R'), table)

        self.assertEqual(str(result), 'F')

    def test_clockwise_with_flip(self) -> None:
        """Clockwise move remapped with flip becomes counter-clockwise."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', True)}

        result = rotate_move(Move('R'), table)

        self.assertEqual(str(result), "F'")

    def test_counter_clockwise_with_flip(self) -> None:
        """Counter-clockwise move with flip becomes clockwise."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', True)}

        result = rotate_move(Move("R'"), table)

        self.assertEqual(str(result), 'F')

    def test_counter_clockwise_no_flip(self) -> None:
        """Counter-clockwise move without flip stays counter-clockwise."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', False)}

        result = rotate_move(Move("R'"), table)

        self.assertEqual(str(result), "F'")

    def test_double_move_ignores_flip(self) -> None:
        """Double move is unaffected by flip."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', True)}

        result = rotate_move(Move('R2'), table)

        self.assertEqual(str(result), 'F2')

    def test_wide_move(self) -> None:
        """Wide move notation is preserved."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', False)}

        result = rotate_move(Move('Rw'), table)

        self.assertEqual(str(result), 'Fw')

    def test_timed_move(self) -> None:
        """Timing is preserved on remapped move."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', False)}

        result = rotate_move(Move('R@100'), table)

        self.assertEqual(str(result), 'F@100')

    def test_sign_move(self) -> None:
        """SiGN notation is preserved on remapped move."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', False)}

        result = rotate_move(Move('r'), table)

        self.assertEqual(str(result), 'f')

    def test_empty_table(self) -> None:
        """Empty table returns move unchanged."""
        result = rotate_move(Move('R'), {})

        self.assertEqual(str(result), 'R')

    def test_pause_move(self) -> None:
        """Pause move passes through unchanged."""
        table: dict[str, tuple[str, bool]] = {'R': ('F', False)}

        result = rotate_move(Move('.'), table)

        self.assertEqual(str(result), '.')


class TransformTranslateTestCase(unittest.TestCase):
    """Tests for algorithm translation across orientations."""

    def test_translate_z2(self) -> None:
        """Test translate z2."""
        # z2 (DR) is symmetric: should be easy
        orientation = parse_moves('z2')
        provide = parse_moves("L D L' D'")
        expect = parse_moves("R U R' U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_y_z2(self) -> None:
        """Test translate y z2."""
        # y z2 (DR)
        orientation = parse_moves('y z2')
        provide = parse_moves("F D F' D'")
        expect = parse_moves("R U R' U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_z_y(self) -> None:
        """Test translate z y."""
        # z y (LU)
        orientation = parse_moves('z y')
        provide = parse_moves("L B2 L' U' F U' L'")
        expect = parse_moves("U R2 U' F' L F' U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_x_y(self) -> None:
        """Test translate x y."""
        # x y (FR)
        orientation = parse_moves('x y')
        provide = parse_moves("R U R'")
        expect = parse_moves("F R F'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(result, expect)

    def test_translate_z2_with_pause(self) -> None:
        """Test translate z2 with pause."""
        orientation = parse_moves('z2')
        provide = parse_moves("L . D L' . D'")
        expect = parse_moves("R . U R' . U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_z2_timed(self) -> None:
        """Test translate z2 timed."""
        orientation = parse_moves('z2')
        provide = parse_moves("L@10 .@20 D@30 L'@40 .@50 D'@60")
        expect = parse_moves("R@10 .@20 U@30 R'@40 .@50 U'@60")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_invalid_orientation(self) -> None:
        """Test translate invalid orientation."""
        orientation = parse_moves('x F')
        provide = parse_moves("L D L' D'")

        with self.assertRaises(InvalidMoveError):
            translate_moves(orientation)(provide)

    def test_translate_no_orientation(self) -> None:
        """Test translate no orientation."""
        orientation = parse_moves('')
        provide = parse_moves("L D L' D'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_empty_algorithm(self) -> None:
        """Translating an empty algorithm returns it unchanged."""
        orientation = parse_moves('z2')

        result = translate_moves(orientation)(Algorithm())

        self.assertEqual(result, Algorithm())

    def test_translate_reusable_closure(self) -> None:
        """Closure from translate_moves can be reused on multiple algs."""
        translate = translate_moves(parse_moves('z2'))

        result1 = translate(parse_moves("L D L' D'"))
        result2 = translate(parse_moves("R U R' U'"))

        self.assertEqual(result1, parse_moves("R U R' U'"))
        self.assertEqual(result2, parse_moves("L D L' D'"))


class TransformTranslatePOVTestCase(unittest.TestCase):
    """Tests for POV-based algorithm translation."""

    def test_translate_pov_z2(self) -> None:
        """Test translate pov z2."""
        provide = parse_moves("z2 L D L' D'")
        expect = parse_moves("z2 R U R' U'")

        result = translate_pov_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_y_middle(self) -> None:
        """Test translate pov y middle."""
        provide = parse_moves("R U R' U' y B U B' U'")
        expect = parse_moves("R U R' U' y R U R' U'")

        result = translate_pov_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_z2_timed(self) -> None:
        """Test translate pov z2 timed."""
        provide = parse_moves("z2@0 L@10 D@20 L'@30 D'@40")
        expect = parse_moves("z2@0 R@10 U@20 R'@30 U'@40")

        result = translate_pov_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_consecutive_rotations(self) -> None:
        """Test translate pov with multiple consecutive rotations."""
        provide = parse_moves('R x y U')
        expect = parse_moves('R x y R')

        result = translate_pov_moves(provide)

        self.assertEqual(result, expect)

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_interspersed_rotations(self) -> None:
        """Test translate pov with rotations interspersed among moves."""
        provide = parse_moves('R x U y F')
        expect = parse_moves('R x B y U')

        result = translate_pov_moves(provide)

        self.assertEqual(result, expect)

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_trailing_rotation(self) -> None:
        """Test translate pov with trailing rotation."""
        provide = parse_moves('R U y')
        expect = parse_moves('R U y')

        result = translate_pov_moves(provide)

        self.assertEqual(result, expect)

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_no_rotations(self) -> None:
        """Algorithm without rotations is returned unchanged."""
        provide = parse_moves("R U R' U'")

        result = translate_pov_moves(provide)

        self.assertEqual(result, provide)

    def test_translate_pov_only_rotations(self) -> None:
        """Algorithm of only rotations is returned unchanged."""
        provide = parse_moves('x y z')

        result = translate_pov_moves(provide)

        self.assertEqual(result, provide)

    def test_translate_pov_empty(self) -> None:
        """Empty algorithm is returned unchanged."""
        result = translate_pov_moves(Algorithm())

        self.assertEqual(result, Algorithm())

    def test_translate_pov_double_rotation(self) -> None:
        """Double rotation (x2) is handled correctly."""
        provide = parse_moves("x2 B U B' U'")
        expect = parse_moves("x2 F D F' D'")

        result = translate_pov_moves(provide)

        self.assertEqual(result, expect)
