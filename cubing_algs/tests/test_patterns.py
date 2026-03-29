"""Tests for cube pattern recognition and generation."""
import unittest

from cubing_algs.exceptions import InvalidPatternNameError
from cubing_algs.move import Move
from cubing_algs.patterns import ALPHABET
from cubing_algs.patterns import PATTERNS
from cubing_algs.patterns import get_letter
from cubing_algs.patterns import get_pattern
from cubing_algs.patterns import list_letters
from cubing_algs.patterns import list_patterns


class PatternsTestCase(unittest.TestCase):
    """Tests for cube pattern recognition and generation."""

    def test_patterns_size(self) -> None:
        """Test patterns size."""
        self.assertEqual(
            len(PATTERNS.keys()),
            68,
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
        with self.assertRaises(InvalidPatternNameError):
            get_pattern('El Matadore')

    def test_list_patterns(self) -> None:
        """Test list patterns returns all pattern names."""
        names = list_patterns()

        self.assertEqual(len(names), 68)
        self.assertIn('DontCrossLine', names)
        self.assertIn('Superflip', names)


class LetterTestCase(unittest.TestCase):
    """Tests for cube letter and generation."""

    def test_alphabet_size(self) -> None:
        """Test patterns size."""
        self.assertEqual(
            len(ALPHABET.keys()),
            26,
        )

    def test_get_letter(self) -> None:
        """Test get letter."""
        pattern = get_letter('A')

        self.assertEqual(
            len(pattern), 18,
        )

        for m in pattern:
            self.assertTrue(isinstance(m, Move))

    def test_get_letter_inexistant(self) -> None:
        """Test get letter inexistant."""
        with self.assertRaises(InvalidPatternNameError):
            get_letter('5')

    def test_list_letters(self) -> None:
        """Test list letters returns all letter names."""
        names = list_letters()

        self.assertEqual(len(names), 26)
        self.assertIn('A', names)
        self.assertIn('Z', names)
