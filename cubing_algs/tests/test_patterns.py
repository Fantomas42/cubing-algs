import unittest

from cubing_algs.move import Move
from cubing_algs.patterns import PATTERNS
from cubing_algs.patterns import get_pattern


class PatternsTestCase(unittest.TestCase):

    def test_patterns_size(self):
        self.assertEqual(
            len(PATTERNS.keys()),
            69,
        )

    def test_get_pattern(self):
        pattern = get_pattern('DontCrossLine')

        self.assertEqual(
            len(pattern), 6,
        )

        for m in pattern:
            self.assertTrue(isinstance(m, Move))

    def test_get_pattern_inexistant(self):
        pattern = get_pattern('El Matadore')

        self.assertEqual(
            len(pattern), 0,
        )
