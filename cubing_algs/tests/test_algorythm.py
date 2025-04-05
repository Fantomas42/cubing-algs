import unittest

from cubing_algs.parsing import parse_moves


class AlgorythmTestCase(unittest.TestCase):

    def test_length(self):
        algo = parse_moves('R2 U')

        self.assertEqual(len(algo), 2)
