"""Tests for invert transformation functions."""
import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.invert import invert_moves


class TransformInvertTestCase(unittest.TestCase):
    """Tests for invert transformation."""

    def test_invert_moves(self) -> None:
        """Test invert moves."""
        provide = parse_moves(
            "F R U2 F'",
        )
        expect = parse_moves("F U2 R' F'")

        result = invert_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_invert_big_moves(self) -> None:
        """Test invert big moves."""
        provide = parse_moves(
            "2Fw R 3U2 3f'",
        )
        expect = parse_moves("3f 3U2 R' 2Fw'")

        result = invert_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_invert_empty_algorithm(self) -> None:
        """Test inverting an empty algorithm returns an empty algorithm."""
        provide = parse_moves('')
        expect = parse_moves('')

        result = invert_moves(provide)

        self.assertEqual(result, expect)

    def test_invert_double_moves(self) -> None:
        """Test that double moves remain unchanged when inverted."""
        provide = parse_moves('R2')
        expect = parse_moves('R2')

        result = invert_moves(provide)

        self.assertEqual(result, expect)

    def test_timed_moves(self) -> None:
        """Test timed moves."""
        provide = parse_moves(
            "F@1 R@2 U2@3 F'@4",
        )
        expect = parse_moves("F@1 U2@2 R'@3 F'@4")

        result = invert_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_timed_moves_with_pauses(self) -> None:
        """Test timed moves with pauses."""
        provide = parse_moves(
            "F@1 .@2 R@3 U2@4 F'@5",
        )
        expect = parse_moves("F@1 U2@2 R'@3 .@4 F'@5")

        result = invert_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
