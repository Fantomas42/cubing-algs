import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves


class AlgorithmTestCase(unittest.TestCase):

    def test_append(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.append('F2')
        self.assertEqual(str(algo), 'R2 U F2')

    def test_extend(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.extend(['F2', 'B'])
        self.assertEqual(str(algo), 'R2 U F2 B')

    def test_extend_with_algorithm(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.extend(parse_moves('F2 B'))
        self.assertEqual(str(algo), 'R2 U F2 B')

    def test_insert(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.insert(0, 'F2')
        self.assertEqual(str(algo), 'F2 R2 U')

    def test_remove(self):
        algo = parse_moves('R2 U R2')
        self.assertEqual(str(algo), 'R2 U R2')
        algo.remove('R2')
        self.assertEqual(str(algo), 'U R2')

    def test_pop(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        popped = algo.pop()
        self.assertEqual(str(algo), 'R2')
        self.assertEqual(popped, 'U')

    def test_copy(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        copy = algo.copy()
        self.assertTrue(isinstance(copy, Algorithm))
        self.assertEqual(str(copy), 'R2 U')

        algo.pop()
        self.assertEqual(str(algo), 'R2')
        self.assertEqual(str(copy), 'R2 U')

    def test_iter(self):
        algo = parse_moves('R2 U')
        for m, n in zip(algo, ['R2', 'U'], strict=True):
            self.assertEqual(m, n)

    def test_getitem(self):
        algo = parse_moves('R2 U')
        self.assertEqual(algo[1], 'U')

    def test_setitem(self):
        algo = parse_moves('R2 U')
        algo[1] = 'B'
        self.assertEqual(str(algo), 'R2 B')

    def test_delitem(self):
        algo = parse_moves('R2 U')
        del algo[1]
        self.assertEqual(str(algo), 'R2')

    def test_length(self):
        algo = parse_moves('R2 U')

        self.assertEqual(len(algo), 2)

    def test_str(self):
        algo = parse_moves('R2 U')

        self.assertEqual(str(algo), 'R2 U')

    def test_repr(self):
        algo = parse_moves('R2 U')

        self.assertEqual(repr(algo), 'Algorithm("R2U")')

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

    def test_transform_to_fixpoint(self):
        algo = parse_moves("R R F F' R2 U F2")
        expected = parse_moves('R2 R2 U F2')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
            ),
            expected,
        )

        algo = parse_moves("R R F F' R2 U F2")
        expected = parse_moves('U F2')

        self.assertEqual(
            algo.transform(
                optimize_do_undo_moves,
                optimize_double_moves,
                to_fixpoint=True,
            ),
            expected,
        )
