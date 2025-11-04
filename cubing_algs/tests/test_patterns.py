"""Tests for cube pattern recognition and generation."""

import unittest

from cubing_algs.move import Move
from cubing_algs.patterns import PATTERNS
from cubing_algs.patterns import get_pattern


class PatternsTestCase(unittest.TestCase):
    """Tests for cube pattern recognition and generation."""

    def test_patterns_size(self) -> None:
        """Test patterns size."""
        self.assertEqual(
            len(PATTERNS.keys()),
            69,
        )

    def test_get_pattern(self) -> None:
        """Test get pattern."""
        pattern = get_pattern('DontCrossLine')

        self.assertEqual(
            len(pattern), 6,
        )

        for m in pattern:
            self.assertTrue(isinstance(m, Move))

    def test_get_pattern_inexistant(self) -> None:
        """Test get pattern inexistant."""
        pattern = get_pattern('El Matadore')

        self.assertEqual(
            len(pattern), 0,
        )
