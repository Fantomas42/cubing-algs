"""Tests for timing transformation functions."""
import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.timing import time_moves
from cubing_algs.transform.timing import untime_moves


class TransformTimeTestCase(unittest.TestCase):
    """Tests for assigning timing information to algorithms."""

    def test_time_moves_default_interval(self) -> None:
        """Test time moves with default interval."""
        provide = parse_moves("F R U2 F'")
        expect = parse_moves("F@0 R@100 U2@200 F'@300")

        result = time_moves()(provide)

        self.assertEqual(result, expect)

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_time_moves_custom_interval(self) -> None:
        """Test time moves with custom interval."""
        provide = parse_moves("F R U2 F'")
        expect = parse_moves("F@0 R@50 U2@100 F'@150")

        result = time_moves(interval=50)(provide)

        self.assertEqual(result, expect)

    def test_time_moves_already_timed(self) -> None:
        """Test time moves re-times already timed moves."""
        provide = parse_moves("F@1 R@2 U2@3 F'@4")
        expect = parse_moves("F@0 R@100 U2@200 F'@300")

        result = time_moves()(provide)

        self.assertEqual(result, expect)

    def test_time_moves_with_pauses(self) -> None:
        """Test time moves with pauses."""
        provide = parse_moves('R . U')
        expect = parse_moves('R@0 .@100 U@200')

        result = time_moves()(provide)

        self.assertEqual(result, expect)

    def test_time_moves_empty(self) -> None:
        """Test time moves on an empty algorithm."""
        provide = parse_moves('')
        expect = parse_moves('')

        result = time_moves()(provide)

        self.assertEqual(result, expect)


class TransformUntimeTestCase(unittest.TestCase):
    """Tests for removing timing information from algorithms."""

    def test_untime_moves(self) -> None:
        """Test untime moves."""
        provide = parse_moves(
            "F@1 R@2 U2@3 F'@4",
        )
        expect = parse_moves("F R U2 F'")

        result = untime_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_untime_big_moves(self) -> None:
        """Test untime big moves."""
        provide = parse_moves(
            "2Fw@1 R@2 3U2@3 3f'@4",
        )
        expect = parse_moves("2Fw R 3U2 3f'")

        result = untime_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_untime_empty_algorithm(self) -> None:
        """Test untime moves on an empty algorithm."""
        provide = parse_moves('')
        expect = parse_moves('')

        result = untime_moves(provide)

        self.assertEqual(result, expect)

    def test_untime_moves_with_pauses(self) -> None:
        """Test untime moves with timed pauses."""
        provide = parse_moves('R .@5 U .@3 F')
        expect = parse_moves('R . U . F')

        result = untime_moves(provide)

        self.assertEqual(result, expect)

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_untime_moves_untimed(self) -> None:
        """Test untime moves untimed."""
        provide = parse_moves(
            "F@1 R U2 F'@4",
        )
        expect = parse_moves("F R U2 F'")

        result = untime_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
