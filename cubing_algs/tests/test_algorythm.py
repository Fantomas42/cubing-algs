import unittest

from cubing_algs.parsing import parse_moves


class AlgorythmTestCase(unittest.TestCase):

    def test_length(self):
        algo = parse_moves('R2 U')

        self.assertEqual(len(algo), 2)

    def test_str(self):
        algo = parse_moves('R2 U')

        self.assertEqual(str(algo), 'R2 U')

    def test_repr(self):
        algo = parse_moves('R2 U')

        self.assertEqual(repr(algo), 'Algorythm("R2U")')
