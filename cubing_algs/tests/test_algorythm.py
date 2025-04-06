import unittest

from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves


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

    def test_eq(self):
        algo = parse_moves('R2 U')
        algo_bis = parse_moves('R2 U')

        self.assertEqual(algo, algo_bis)

    def test_hash(self):
        algo = parse_moves('R2 U')
        self.assertTrue(hash(algo))

    def test_transform(self):
        algo = parse_moves('R R U F2 F2')
        expected = parse_moves('R2 U')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
            ),
            expected,
        )

        algo = parse_moves('R U F2')
        expected = parse_moves('R U F2')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
            ),
            expected,
        )
