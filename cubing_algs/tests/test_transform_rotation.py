"""Tests for rotation transformation functions."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.rotation import compress_ending_rotations
from cubing_algs.transform.rotation import compress_rotations
from cubing_algs.transform.rotation import optimize_conjugate_rotations
from cubing_algs.transform.rotation import optimize_double_rotations
from cubing_algs.transform.rotation import optimize_triple_rotations
from cubing_algs.transform.rotation import remove_ending_rotations
from cubing_algs.transform.rotation import remove_rotations
from cubing_algs.transform.rotation import remove_starting_rotations
from cubing_algs.transform.rotation import split_moves_ending_rotations


class TransformRemoveEndingRotationsTestCase(unittest.TestCase):
    """Tests for removing ending rotations from algorithms."""

    def test_remove_ending_rotations(self) -> None:
        """Test remove ending rotations."""
        provide = parse_moves('R2 F U x y2')
        expect = parse_moves('R2 F U')

        result = remove_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_ending_rotations_timed(self) -> None:
        """Test remove ending rotations timed."""
        provide = parse_moves('R2@1 F@2 U@3 x@4 y2@5')
        expect = parse_moves('R2@1 F@2 U@3')

        result = remove_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_ending_rotations_timed_preserve_starting(self) -> None:
        """Test remove ending rotations timed preserve starting."""
        provide = parse_moves('x@0 R2@1 F@2 U@3 x@4 y2@5')
        expect = parse_moves('x@0 R2@1 F@2 U@3')

        result = remove_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_ending_rotations_timed_paused(self) -> None:
        """Test remove ending rotations timed paused."""
        provide = parse_moves('R2@1 F@2 U@3 x@4 .@5 y2@6')
        expect = parse_moves('R2@1 F@2 U@3')

        result = remove_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('R2@1 F@2 U@3 .@4 x@5 .@6 y2@7')
        expect = parse_moves('R2@1 F@2 U@3')

        result = remove_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformRemoveStartingRotationsTestCase(unittest.TestCase):
    """Tests for removing starting rotations from algorithms."""

    def test_remove_starting_rotations(self) -> None:
        """Test remove starting rotations."""
        provide = parse_moves('x y2 R2 F U')
        expect = parse_moves('R2 F U')

        result = remove_starting_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_starting_rotations_timed(self) -> None:
        """Test remove starting rotations timed."""
        provide = parse_moves('x@1 y2@2 R2@3 F@4 U@5')
        expect = parse_moves('R2@3 F@4 U@5')

        result = remove_starting_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_starting_rotations_timed_preserve_ending(self) -> None:
        """Test remove starting rotations timed preserve ending."""
        provide = parse_moves('x@1 y2@2 R2@3 F@4 U@5 x@6')
        expect = parse_moves('R2@3 F@4 U@5 x@6')

        result = remove_starting_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_starting_rotations_timed_paused(self) -> None:
        """Test remove starting rotations timed paused."""
        provide = parse_moves('z@0 . x2@1 R2@2 F@3 U@4')
        expect = parse_moves('R2@2 F@3 U@4')

        result = remove_starting_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('.@0 x@1 .@3 .@4 R2@5 F@6 U@7')
        expect = parse_moves('R2@5 F@6 U@7')

        result = remove_starting_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformRemoveRotationsTestCase(unittest.TestCase):
    """Tests for removing all rotations from algorithms."""

    def test_remove_rotations(self) -> None:
        """Test remove rotations."""
        provide = parse_moves('z R2 F U x y2')
        expect = parse_moves('R2 F U')

        result = remove_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_rotations_timed(self) -> None:
        """Test remove rotations timed."""
        provide = parse_moves('y@0 R2@1 F@2 U@3 x@4 y2@5')
        expect = parse_moves('R2@1 F@2 U@3')

        result = remove_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_rotations_timed_paused(self) -> None:
        """Test remove rotations timed paused."""
        provide = parse_moves('x@0 R2@1 F@2 U@3 x@4 .@5 y2@6')
        expect = parse_moves('R2@1 F@2 U@3 .@5')

        result = remove_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('R2@1 F@2 U@3 .@4 x@5 .@6 y2@7')
        expect = parse_moves('R2@1 F@2 U@3 .@4 .@6')

        result = remove_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class SplitMovesEndingRotationsTestCase(unittest.TestCase):
    """Tests for splitting moves and ending rotations."""

    def test_split_moves_ending_rotations(self) -> None:
        """Test split moves ending rotations."""
        provide = parse_moves("R2 F x x x'")
        expect = (parse_moves('R2 F'), parse_moves("x x x'"))

        result = split_moves_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result[1]:
            self.assertTrue(isinstance(m, Move))

    def test_split_moves_ending_rotations_empty(self) -> None:
        """Test split moves ending rotations empty."""
        provide = parse_moves('R2 F')
        expect = (parse_moves('R2 F'), Algorithm())

        result = split_moves_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_split_moves_ending_rotations_start(self) -> None:
        """Test split moves ending rotations start."""
        provide = parse_moves('x R2 F')
        expect = (parse_moves('x R2 F'), Algorithm())

        result = split_moves_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )


class TransformOptimizeTripleRotationsTestCase(unittest.TestCase):
    """Tests for optimizing triple rotation sequences."""

    def test_optimize_triple_rotations(self) -> None:
        """Test optimize triple rotations."""
        provide = parse_moves('x2 y2 z2')
        expect = Algorithm()

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        provide = parse_moves('y2 x2 z2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        provide = parse_moves('z2 x2 y2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_optimize_triple_rotations_timed(self) -> None:
        """Test optimize triple rotations timed."""
        provide = parse_moves('x2@0 y2@50 z2@100')
        expect = Algorithm()

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_optimize_triple_rotations_start(self) -> None:
        """Test optimize triple rotations start."""
        provide = parse_moves('x2 x2 y2 z2')
        expect = parse_moves('x2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_triple_rotations_end(self) -> None:
        """Test optimize triple rotations end."""
        provide = parse_moves('x2 y2 z2 x2')
        expect = parse_moves('x2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_triple_rotations_max(self) -> None:
        """Test optimize triple rotations max."""
        provide = parse_moves('x2 y2 z2')

        result = optimize_triple_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )


class TransformOptimizeDoubleRotationsTestCase(unittest.TestCase):
    """Tests for optimizing double rotation sequences."""

    def test_optimize_double_rotations(self) -> None:
        """Test optimize double rotations."""
        provide = parse_moves('x2 y2')
        expect = parse_moves('z2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('z2 x2')
        expect = parse_moves('y2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('z2 y2')
        expect = parse_moves('x2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_timed(self) -> None:
        """Test optimize double rotations timed."""
        provide = parse_moves('x2@50 y2@100')
        expect = parse_moves('z2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_start(self) -> None:
        """Test optimize double rotations start."""
        provide = parse_moves('x x2 y2')
        expect = parse_moves('x z2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_end(self) -> None:
        """Test optimize double rotations end."""
        provide = parse_moves('x2 y2 x')
        expect = parse_moves('z2 x')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_multiple(self) -> None:
        """Test optimize double rotations multiple."""
        provide = parse_moves('x2 y2 x2')
        expect = parse_moves('y2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_chained(self) -> None:
        """
        Test that a newly produced rotation is further
        combined with adjacent double rotations.
        """
        # x2 y2 z2 y2: first pair x2,y2 → z2,
        # then z2,z2 skipped (same), z2,y2 → x2
        # but the resulting z2,x2 pair must be further combined into y2
        provide = parse_moves('x2 y2 z2 y2')
        expect = parse_moves('y2')

        result = optimize_double_rotations(provide)

        self.assertEqual(result, expect)
        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_max(self) -> None:
        """Test optimize double rotations max."""
        provide = parse_moves('x2 y2')

        result = optimize_double_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )

    def test_optimize_double_rotations_ignores_face_moves(self) -> None:
        """Test that non-rotation double moves are left unchanged."""
        cases = [
            ('R2 U2', 'R2 U2'),
            ('R2 F2', 'R2 F2'),
            ('U2 D2', 'U2 D2'),
            ('R2 U2 F2', 'R2 U2 F2'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                provide = parse_moves(provided)
                expect = parse_moves(expected)

                result = optimize_double_rotations(provide)

                self.assertEqual(result, expect)

    def test_optimize_double_rotations_ignores_mixed_moves(self) -> None:
        """Test that mixed rotation and face double moves are left unchanged."""
        cases = [
            ('x2 R2', 'x2 R2'),
            ('R2 y2', 'R2 y2'),
            ('z2 U2', 'z2 U2'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                provide = parse_moves(provided)
                expect = parse_moves(expected)

                result = optimize_double_rotations(provide)

                self.assertEqual(result, expect)


class TransformOptimizeConjugateRotationsTestCase(unittest.TestCase):
    """Tests for optimizing conjugate rotation patterns."""

    def test_optimize_conjugate_rotations(self) -> None:
        """Test optimize conjugate rotations."""
        provide = parse_moves("y x2 y'")
        expect = parse_moves('z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y' x2 y")
        expect = parse_moves('z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("z x2 z'")
        expect = parse_moves('y2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("z' y2 z")
        expect = parse_moves('x2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_timed(self) -> None:
        """Test optimize conjugate rotations timed."""
        provide = parse_moves("y@0 x2@50 y'@100")
        expect = parse_moves('z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_start(self) -> None:
        """Test optimize conjugate rotations start."""
        provide = parse_moves("x x y2 x'")
        expect = parse_moves('x z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_end(self) -> None:
        """Test optimize conjugate rotations end."""
        provide = parse_moves("x y2 x' x")
        expect = parse_moves('z2 x')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_multiple(self) -> None:
        """Test optimize conjugate rotations multiple."""
        provide = parse_moves("x' z2 x y x2 y'")
        expect = parse_moves('y2 z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_chained_double(self) -> None:
        """
        Test that two conjugate patterns whose results
        form a double-rotation pair are fully combined.
        """
        # y x2 y' → z2, then y z2 y' → x2 —
        # the resulting z2 x2 must be further combined into y2
        provide = parse_moves("y x2 y' y z2 y'")
        expect = parse_moves('z2 x2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(result, expect)
        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_max(self) -> None:
        """Test optimize conjugate rotations max."""
        provide = parse_moves("y x2 y'")

        result = optimize_conjugate_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )

    def test_optimize_conjugate_rotations_ignores_face_moves(self) -> None:
        """Test that non-rotation conjugate patterns are left unchanged."""
        cases = [
            ("R U2 R'", "R U2 R'"),
            ("F D2 F'", "F D2 F'"),
            ("L R2 L'", "L R2 L'"),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                provide = parse_moves(provided)
                expect = parse_moves(expected)

                result = optimize_conjugate_rotations(provide)

                self.assertEqual(result, expect)

    def test_optimize_conjugate_rotations_ignores_mixed_moves(self) -> None:
        """Test mixed rotation and face conjugates are unchanged."""
        cases = [
            ("R y2 R'", "R y2 R'"),
            ("U x2 U'", "U x2 U'"),
            ("x R2 x'", "x R2 x'"),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                provide = parse_moves(provided)
                expect = parse_moves(expected)

                result = optimize_conjugate_rotations(provide)

                self.assertEqual(result, expect)


class TransformCompressRotationsTestCase(unittest.TestCase):
    """Tests for compressing rotation sequences."""

    def test_compress_rotations(self) -> None:
        """Test compress rotations."""
        provide = parse_moves("x' z2 x y x2 y'")
        expect = parse_moves('x2')

        result = compress_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_rotations_issues_01(self) -> None:
        """Test compress rotations issues 01."""
        provide = parse_moves("z@27089 y y z' z' z x x")
        expect = Algorithm()

        result = compress_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_rotations_impossible(self) -> None:
        """Test compress rotations impossible."""
        provide = parse_moves('x')

        result = compress_rotations(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_rotations_max(self) -> None:
        """Test compress rotations max."""
        provide = parse_moves("x' z2 x y x2 y'")

        result = compress_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformCompressEndingRotationsTestCase(unittest.TestCase):
    """Tests for compressing ending rotation sequences."""

    def test_compress_ending_rotations(self) -> None:
        """Test compress ending rotations."""
        provide = parse_moves("R2 F x x x' x x x")
        expect = parse_moves('R2 F')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_empty(self) -> None:
        """Test compress ending rotations empty."""
        provide = parse_moves('R2 F')
        expect = parse_moves('R2 F')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_timed(self) -> None:
        """Test compress ending rotations timed."""
        provide = parse_moves("R2@1 F@2 x'@3 x@4")
        expect = parse_moves('R2@1 F@2')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_impair(self) -> None:
        """Test compress ending rotations impair."""
        provide = parse_moves("R2 F x' x x'")
        expect = parse_moves("R2 F x'")

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_double_double(self) -> None:
        """Test compress ending rotations double double."""
        provide = parse_moves('R2 F x2 z2')
        expect = parse_moves('R2 F y2')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('R2 F x2 y2')
        expect = parse_moves('R2 F z2')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('R2 F y2 z2')
        expect = parse_moves('R2 F x2')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_trible_double(self) -> None:
        """Test compress ending rotations trible double."""
        provide = parse_moves('R2 F x2 z2 y2')
        expect = parse_moves('R2 F')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_trible_double_failed(self) -> None:
        """Test compress ending rotations trible double failed."""
        provide = parse_moves('R2 F x2 z2 y')
        expect = parse_moves("R2 F y'")

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_simple_double_simple(self) -> None:
        """Test compress ending rotations simple double simple."""
        provide = parse_moves("R2 F x z2 x'")
        expect = parse_moves('R2 F y2')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("R2 F x' z2 x")
        expect = parse_moves('R2 F y2')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_simple_double_simple_clear(self) -> None:
        """Test compress ending rotations simple double simple clear."""
        provide = parse_moves("R2 F x z2 x' y2")
        expect = parse_moves('R2 F')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("R2 F x' z2 x y2")
        expect = parse_moves('R2 F')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_complex(self) -> None:
        """Test compress ending rotations complex."""
        provide = parse_moves("R2 F z2 x z2 x' y2 x x y2")
        expect = parse_moves('R2 F')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_only(self) -> None:
        """Test compress ending rotations only."""
        provide = parse_moves('y')
        expect = parse_moves('y')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y y'")
        expect = parse_moves('')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y' y")
        expect = parse_moves('')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y y' y")
        expect = parse_moves('y')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_ending_rotations_timed_only(self) -> None:
        """Test compress ending rotations timed only."""
        provide = parse_moves("y'@0")
        expect = parse_moves("y'@0")

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y'@0 y@3630")
        expect = parse_moves('')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y'@0 y@3630 y'@5970")
        expect = parse_moves("y'@5970")

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y'@0 y@3630 y'@5970 y@6600")
        expect = parse_moves('')

        result = compress_ending_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class CompressEndingRotationsSingleConjugateTestCase(unittest.TestCase):
    """
    Tests for single-rotation conjugate patterns: a b a' -> c.

    These are 3-move patterns where two single quarter-turn rotations
    on different axes form a conjugate (a b a'). The result should be
    a single quarter-turn on the third axis.

    Currently NOT optimized — compress_ending_rotations only handles
    double-middle conjugates (a b2 a' -> c2).
    """

    def test_x_y_conjugate(self) -> None:
        """Test x-axis / y-axis conjugates producing z or z'."""
        cases = [
            ("R U x y x'", 'R U z'),
            ("R U x y' x'", "R U z'"),
            ("R U x' y x", "R U z'"),
            ("R U x' y' x", 'R U z'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_y_z_conjugate(self) -> None:
        """Test y-axis / z-axis conjugates producing x or x'."""
        cases = [
            ("R U y z y'", 'R U x'),
            ("R U y z' y'", "R U x'"),
            ("R U y' z y", "R U x'"),
            ("R U y' z' y", 'R U x'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_z_x_conjugate(self) -> None:
        """Test z-axis / x-axis conjugates producing y or y'."""
        cases = [
            ("R U z x z'", 'R U y'),
            ("R U z x' z'", "R U y'"),
            ("R U z' x z", "R U y'"),
            ("R U z' x' z", 'R U y'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_single_conjugate_all_rotations(self) -> None:
        """Test that a single conjugate with no face moves compresses."""
        cases = [
            ("x y x'", 'z'),
            ("y z y'", 'x'),
            ("z x z'", 'y'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))


class CompressEndingRotationsSandwichTestCase(unittest.TestCase):
    """
    Tests for same-move sandwich patterns: a b a -> result.

    Two sub-patterns exist:
    - Single wraps double: a b2 a -> b2 (single moves cancel out)
    - Double wraps single: a2 b a2 -> b' (inverts the inner move)

    Currently NOT optimized — the conjugate optimizer requires the
    first and third moves to be inverses (a ... a'), not identical.
    """

    def test_single_wraps_double(self) -> None:
        """Test a b2 a -> b2: single quarter-turns around a double cancel."""
        cases = [
            ('R U x y2 x', 'R U y2'),
            ('R U x z2 x', 'R U z2'),
            ("R U x' y2 x'", 'R U y2'),
            ("R U x' z2 x'", 'R U z2'),
            ('R U y x2 y', 'R U x2'),
            ('R U y z2 y', 'R U z2'),
            ("R U y' x2 y'", 'R U x2'),
            ('R U z x2 z', 'R U x2'),
            ('R U z y2 z', 'R U y2'),
            ("R U z' x2 z'", 'R U x2'),
            ("R U z' y2 z'", 'R U y2'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_double_wraps_single(self) -> None:
        """Test a2 b a2 -> b': double rotations invert the inner move."""
        cases = [
            ('R U x2 y x2', "R U y'"),
            ("R U x2 y' x2", 'R U y'),
            ('R U x2 z x2', "R U z'"),
            ("R U x2 z' x2", 'R U z'),
            ('R U y2 x y2', "R U x'"),
            ("R U y2 x' y2", 'R U x'),
            ('R U y2 z y2', "R U z'"),
            ("R U y2 z' y2", 'R U z'),
            ('R U z2 x z2', "R U x'"),
            ("R U z2 x' z2", 'R U x'),
            ('R U z2 y z2', "R U y'"),
            ("R U z2 y' z2", 'R U y'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))


class CompressEndingRotationsCyclicTripleTestCase(unittest.TestCase):
    """
    Tests for three-different-axes patterns that reduce to 1 move.

    When three rotations each on a different axis satisfy certain sign
    constraints, the whole triple reduces to the middle move.

    Cyclic order (x,y,z), (y,z,x), (z,x,y): odd number of primes.
    Anti-cyclic order (z,y,x), (x,z,y), (y,x,z): even number of primes.
    Mixed double outer pairs: a2 b c2 -> b.

    Currently NOT optimized.
    """

    def test_cyclic_order_single(self) -> None:
        """Test cyclic-order triples with all single quarter-turns."""
        cases = [
            # (x, y, z) family — odd primes
            ("R U x y z'", 'R U y'),
            ("R U x y' z", "R U y'"),
            ("R U x' y z", 'R U y'),
            ("R U x' y' z'", "R U y'"),
            # (y, z, x) family — odd primes
            ("R U y z x'", 'R U z'),
            ("R U y z' x", "R U z'"),
            ("R U y' z x", 'R U z'),
            ("R U y' z' x'", "R U z'"),
            # (z, x, y) family — odd primes
            ("R U z x y'", 'R U x'),
            ("R U z x' y", "R U x'"),
            ("R U z' x y", 'R U x'),
            ("R U z' x' y'", "R U x'"),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_anti_cyclic_order_single(self) -> None:
        """Test anti-cyclic-order triples with all single quarter-turns."""
        cases = [
            # (z, y, x) family — even primes
            ('R U z y x', 'R U y'),
            ("R U z y' x'", "R U y'"),
            ("R U z' y x'", 'R U y'),
            ("R U z' y' x", "R U y'"),
            # (x, z, y) family — even primes
            ('R U x z y', 'R U z'),
            ("R U x z' y'", "R U z'"),
            ("R U x' z y'", 'R U z'),
            ("R U x' z' y", "R U z'"),
            # (y, x, z) family — even primes
            ('R U y x z', 'R U x'),
            ("R U y x' z'", "R U x'"),
            ("R U y' x z'", 'R U x'),
            ("R U y' x' z", "R U x'"),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_mixed_double_outer_pairs(self) -> None:
        """Test triples with double outer moves: a2 b c2 -> b."""
        cases = [
            ('R U x2 y z2', 'R U y'),
            ("R U x2 y' z2", "R U y'"),
            ('R U x2 z y2', 'R U z'),
            ("R U x2 z' y2", "R U z'"),
            ('R U y2 x z2', 'R U x'),
            ("R U y2 x' z2", "R U x'"),
            ('R U y2 z x2', 'R U z'),
            ("R U y2 z' x2", "R U z'"),
            ('R U z2 x y2', 'R U x'),
            ("R U z2 x' y2", "R U x'"),
            ('R U z2 y x2', 'R U y'),
            ("R U z2 y' x2", "R U y'"),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))


class CompressEndingRotationsLongerSequenceTestCase(unittest.TestCase):
    """
    Tests for 4+ move rotation sequences.

    These sequences require multiple optimization passes or a
    group-multiplication approach to compress fully. Many of them
    are currently NOT reduced at all.
    """

    def test_four_move_to_identity(self) -> None:
        """Test 4-move rotation sequences that cancel to nothing."""
        cases = [
            # Conjugate then its result's inverse
            "R U x y x' z'",
            "R U y z y' x'",
            "R U z x z' y'",
            # Do-undo pairs on different axes
            "R U x x' y y'",
            "R U y2 y2 z z'",
        ]
        for provided in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves('R U'))

    def test_four_move_to_single(self) -> None:
        """Test 4-move rotation sequences that reduce to 1 move."""
        cases = [
            # Conjugate + extra move
            ("R U x y x' z", 'R U z2'),
            ("R U y z y' x", 'R U x2'),
            ("R U z x z' y", 'R U y2'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_four_move_to_double(self) -> None:
        """Test 4-move sequences that reduce to 2 moves."""
        cases = [
            ('R U x y x y', "R U x' z'"),
            ("R U x y z x'", 'R U x z'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_five_move_sequences(self) -> None:
        """Test 5-move rotation sequences."""
        cases = [
            ("R U x y z' x2 y", 'R U x2'),
            ("R U x y x' z y'", 'R U y z2'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_six_move_group_identity(self) -> None:
        """
        Test (xy)^3 = identity — a fundamental S4 relation.

        The cube rotation group is isomorphic to S4. One of its
        defining relations is (yx)^3 = identity, meaning six
        alternating y x moves cancel completely.
        """
        cases = [
            'R U x y x y x y',
            'R U y x y x y x',
            "R U x y' x y' x y'",
        ]
        for provided in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves('R U'))

    def test_six_move_to_single(self) -> None:
        """Test 6-move rotation sequences that reduce to 1 move."""
        cases = [
            ("R U x' y z y' x z'", "R U x' z'"),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))


class CompressEndingRotationsMaxTwoMovesTestCase(unittest.TestCase):
    """
    Tests asserting rotation output never exceeds 2 moves.

    The rotation group has 24 elements. Every element can be expressed
    in at most 2 quarter/half-turn rotations. Therefore, any rotation
    sequence should compress to at most 2 moves.

    These tests verify the invariant: the trailing rotation part of
    compress_ending_rotations output has length <= 2.
    """

    @staticmethod
    def _rotation_count(alg: Algorithm) -> int:
        """Count trailing rotation moves in an algorithm."""  # noqa: DOC201
        _, rotations = split_moves_ending_rotations(alg)
        return len(rotations)

    def test_three_move_max_two(self) -> None:
        """All 3-move rotation endings should compress to at most 2."""
        single = ['x', "x'", 'y', "y'", 'z', "z'", 'x2', 'y2', 'z2']
        for m1 in single:
            for m2 in single:
                if m1[0] == m2[0]:
                    continue
                for m3 in single:
                    if m2[0] == m3[0]:
                        continue
                    provided = f'R U {m1} {m2} {m3}'
                    with self.subTest(provided=provided):
                        result = compress_ending_rotations(
                            parse_moves(provided),
                        )
                        count = self._rotation_count(result)
                        self.assertLessEqual(
                            count, 2,
                            f'{provided} -> {result} has {count} '
                            f'trailing rotations (max 2)',
                        )

    def test_four_move_max_two(self) -> None:
        """Sampled 4-move rotation endings should compress to at most 2."""
        cases = [
            'R U x y x y',
            "R U x y x' z",
            "R U y z y' x",
            "R U x y z x'",
            "R U x' y' z' x",
            "R U z y x z'",
            'R U x2 y x2 z',
            "R U y z2 x y'",
        ]
        for provided in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                count = self._rotation_count(result)
                self.assertLessEqual(
                    count, 2,
                    f'{provided} -> {result} has {count} '
                    f'trailing rotations (max 2)',
                )

    def test_long_sequence_max_two(self) -> None:
        """Long rotation sequences should still compress to at most 2."""
        cases = [
            "R U x y z x' y' z'",
            'R U x y x y x y',
            'R U x y z x y z',
            'R U x2 y2 z2 x2 y2 z2',
            "R U x y' z x' y z'",
            'R U y x y x y x y x',
        ]
        for provided in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                count = self._rotation_count(result)
                self.assertLessEqual(
                    count, 2,
                    f'{provided} -> {result} has {count} '
                    f'trailing rotations (max 2)',
                )


class CompressEndingRotationsEdgeCaseTestCase(unittest.TestCase):
    """Tests for edge cases in ending rotation compression."""

    def test_empty_algorithm(self) -> None:
        """Test empty algorithm stays empty."""
        result = compress_ending_rotations(Algorithm())
        self.assertEqual(result, Algorithm())

    def test_no_rotations(self) -> None:
        """Test algorithm with no rotations is unchanged."""
        provide = parse_moves("R U F' D2 L B'")
        result = compress_ending_rotations(provide)
        self.assertEqual(result, provide)

    def test_single_rotation(self) -> None:
        """Test single trailing rotation is unchanged."""
        for rot in ['x', "x'", 'y', "y'", 'z', "z'", 'x2', 'y2', 'z2']:
            with self.subTest(rot=rot):
                provide = parse_moves(f'R U {rot}')
                result = compress_ending_rotations(provide)
                self.assertEqual(result, provide)

    def test_two_rotations_same_axis(self) -> None:
        """Test two rotations on the same axis compress normally."""
        cases = [
            ('R U x x', 'R U x2'),
            ("R U x x'", 'R U'),
            ('R U x x2', "R U x'"),
            ("R U x' x'", 'R U x2'),
            ('R U y y', 'R U y2'),
            ('R U z2 z2', 'R U'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_rotation_only_algorithm(self) -> None:
        """Test algorithm consisting entirely of rotations."""
        cases = [
            ("x y x'", 'z'),
            ('x2 y2', 'z2'),
            ("x y z'", 'y'),
            ('x2 y2 z2', ''),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))

    def test_long_face_moves_short_trailing_rotation(self) -> None:
        """Test that long face-move algorithms are preserved."""
        long_alg = "R U R' U' R' F R2 U' R' U' R U R' F'"
        for rot in ["x y x'", 'z y x', 'x2 y z2']:
            with self.subTest(rot=rot):
                provide = parse_moves(f'{long_alg} {rot}')
                result = compress_ending_rotations(provide)
                # Face moves must be preserved exactly
                moves_part, _ = split_moves_ending_rotations(result)
                self.assertEqual(
                    moves_part,
                    parse_moves(long_alg),
                )

    def test_mid_algorithm_rotations_not_touched(self) -> None:
        """
        Test that rotations in the middle of an algorithm are kept.

        compress_ending_rotations only operates on trailing rotations.
        Rotations followed by face moves must not be altered.
        """
        provide = parse_moves("x y R U z x' F")
        result = compress_ending_rotations(provide)
        self.assertEqual(result, provide)

    def test_pauses_in_trailing_rotations(self) -> None:
        """Test that pauses among trailing rotations are handled."""
        cases = [
            ("R U x . y x'", 'R U z'),
            ("R U x . y2 . x'", 'R U z2'),
        ]
        for provided, expected in cases:
            with self.subTest(provided=provided):
                result = compress_ending_rotations(parse_moves(provided))
                self.assertEqual(result, parse_moves(expected))
