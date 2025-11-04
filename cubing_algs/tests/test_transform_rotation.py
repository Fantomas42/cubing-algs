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

    def test_optimize_double_rotations_max(self) -> None:
        """Test optimize double rotations max."""
        provide = parse_moves('x2 y2')

        result = optimize_double_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )


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

    def test_optimize_conjugate_rotations_max(self) -> None:
        """Test optimize conjugate rotations max."""
        provide = parse_moves("y x2 y'")

        result = optimize_conjugate_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )


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
