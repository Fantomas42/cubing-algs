# ruff: noqa: PLR6104 RUF005
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves


class AlgorithmTestCase(unittest.TestCase):

    def test_init_empty(self):
        algo = Algorithm()
        self.assertEqual(str(algo), '')

        algo.extend('R2 U')

        self.assertEqual(str(algo), 'R2 U')

    def test_parse_moves(self):
        algo = Algorithm.parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        algo = Algorithm.parse_moves(['R2', 'U'])
        self.assertEqual(str(algo), 'R2 U')

        algo = Algorithm.parse_moves(Algorithm.parse_moves(['R2', 'U']))
        self.assertEqual(str(algo), 'R2 U')

    def test_parse_move(self):
        move = Algorithm.parse_move('R2')
        self.assertEqual(move, 'R2')

        with self.assertRaises(InvalidMoveError):
            Algorithm.parse_move('R2 U')

    def test_append(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.append('F2')
        self.assertEqual(str(algo), 'R2 U F2')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo.append(Move('D'))
        self.assertEqual(str(algo), 'R2 U F2 D')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        with self.assertRaises(InvalidMoveError):
            algo.append('G')

        with self.assertRaises(InvalidMoveError):
            algo.append('F R')

        with self.assertRaises(InvalidMoveError):
            algo.append(Move('G'))

        with self.assertRaises(InvalidMoveError):
            algo.append(['F', 'R'])

        with self.assertRaises(InvalidMoveError):
            algo.append([])

    def test_extend(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.extend(['F2', 'B'])
        self.assertEqual(str(algo), 'R2 U F2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo.extend([])
        self.assertEqual(str(algo), 'R2 U F2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo.extend('F R')
        self.assertEqual(str(algo), 'R2 U F2 B F R')

        with self.assertRaises(InvalidMoveError):
            algo.extend(['F2', 'G'])

    def test_extend_with_algorithm(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.extend(parse_moves('F2 B'))
        self.assertEqual(str(algo), 'R2 U F2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_add_operator(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo = algo + ['F2', 'B']
        self.assertEqual(str(algo), 'R2 U F2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo = algo + 'F R'
        self.assertEqual(str(algo), 'R2 U F2 B F R')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        with self.assertRaises(InvalidMoveError):
            algo += 'F2 G'

    def test_iadd_operator(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo += ['F2', 'B']
        self.assertEqual(str(algo), 'R2 U F2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo += 'F R'
        self.assertEqual(str(algo), 'R2 U F2 B F R')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        with self.assertRaises(InvalidMoveError):
            algo + 'F2 G'

    def test_radd_operator(self):
        algo = 'F2R2' + parse_moves('D2 U')
        self.assertEqual(str(algo), 'F2 R2 D2 U')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        with self.assertRaises(InvalidMoveError):
            'F2 G' + algo

    def test_radd_operator_z(self):
        algo = 'z' + parse_moves('R2 U')
        self.assertEqual(str(algo), 'z R2 U')

    def test_radd_operator_zprime(self):
        algo = "z'" + parse_moves('R2 U')
        self.assertEqual(str(algo), "z' R2 U")

    def test_radd_operator_z2(self):
        algo = 'z2' + parse_moves('R2 U')
        self.assertEqual(str(algo), 'z2 R2 U')

    def test_add_exploded(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo += [*algo, 'F2', 'B']
        self.assertEqual(str(algo), 'R2 U R2 U F2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_add_operator_with_algorithm(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo = algo + parse_moves('F2 B')
        self.assertEqual(str(algo), 'R2 U F2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_insert(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        algo.insert(0, 'F2')
        self.assertEqual(str(algo), 'F2 R2 U')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_remove(self):
        algo = parse_moves('R2 U R2')
        self.assertEqual(str(algo), 'R2 U R2')
        algo.remove('R2')
        self.assertEqual(str(algo), 'U R2')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_pop(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')
        popped = algo.pop()
        self.assertEqual(str(algo), 'R2')
        self.assertEqual(popped, 'U')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_copy(self):
        algo = parse_moves('R2 U')
        self.assertEqual(str(algo), 'R2 U')

        copy = algo.copy()
        self.assertTrue(isinstance(copy, Algorithm))
        self.assertEqual(str(copy), 'R2 U')

        for m in algo:
            self.assertTrue(isinstance(m, Move))
        for m in copy:
            self.assertTrue(isinstance(m, Move))

        algo.pop()
        self.assertEqual(str(algo), 'R2')
        self.assertEqual(str(copy), 'R2 U')

        for m in algo:
            self.assertTrue(isinstance(m, Move))
        for m in copy:
            self.assertTrue(isinstance(m, Move))

    def test_iter(self):
        algo = parse_moves('R2 U')
        for m, n in zip(algo, ['R2', 'U'], strict=True):
            self.assertEqual(m, n)

    def test_getitem(self):
        algo = parse_moves('R2 U')
        self.assertEqual(algo[1], 'U')
        self.assertEqual(type(algo[1]), Move)

    def test_setitem_slice(self):
        algo = parse_moves('R2 U F')
        algo[2:] = []
        self.assertEqual(str(algo), 'R2 U')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo = parse_moves('R2 U F')
        algo[1:] = []
        self.assertEqual(str(algo), 'R2')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo = parse_moves('R2 U F')
        new_algo = parse_moves('B2 D')
        algo[2:] = new_algo
        self.assertEqual(str(algo), 'R2 U B2 D')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo = parse_moves('R2 U F')
        new_algo = parse_moves('B2 D')
        algo[1:] = new_algo
        self.assertEqual(str(algo), 'R2 B2 D')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

        algo = parse_moves('R2 U F L D')
        new_algo = parse_moves('B2 D')
        algo[1:3] = new_algo
        self.assertEqual(str(algo), 'R2 B2 D L D')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_setitem(self):
        algo = parse_moves('R2 U')
        algo[1] = Move('B')
        self.assertEqual(str(algo), 'R2 B')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

    def test_delitem(self):
        algo = parse_moves('R2 U')
        del algo[1]
        self.assertEqual(str(algo), 'R2')

        for m in algo:
            self.assertTrue(isinstance(m, Move))

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

    def test_eq_copy(self):
        algo = parse_moves('R2 U')
        algo_copy = algo.copy()

        self.assertEqual(algo, algo_copy)

    def test_eq_list(self):
        algo = parse_moves('R2 U')
        algo_list = [Move('R2'), Move('U')]

        self.assertEqual(algo, algo_list)

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

    def test_min_cube_size(self):
        algo = parse_moves("B' R2 U F2")

        self.assertEqual(
            algo.min_cube_size,
            2,
        )

        algo = parse_moves("B' R2 M U F2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' r2 U F2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' R2 U Fw2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' R2 U 2Fw2")

        self.assertEqual(
            algo.min_cube_size,
            3,
        )

        algo = parse_moves("B' R2 U 3Fw2")

        self.assertEqual(
            algo.min_cube_size,
            6,
        )

        algo = parse_moves("B' R2 U 2-3Fw2")

        self.assertEqual(
            algo.min_cube_size,
            6,
        )

        algo = parse_moves("B' R2 U 4Fw2")

        self.assertEqual(
            algo.min_cube_size,
            8,
        )

        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertEqual(
            algo.min_cube_size,
            8,
        )

    def test_is_standard(self):
        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertTrue(algo.is_standard)
        self.assertFalse(algo.is_sign)

    def test_is_sign(self):
        algo = parse_moves("B' R2 U 2-4f2")

        self.assertTrue(algo.is_sign)
        self.assertFalse(algo.is_standard)

    def test_has_rotations(self):
        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertTrue(algo.has_rotations)

        algo = parse_moves("B' R2 U 2-4f2")

        self.assertTrue(algo.has_rotations)

        algo = parse_moves("B' R2 U x")

        self.assertTrue(algo.has_rotations)

    def test_has_internal_rotations(self):
        algo = parse_moves("B' R2 U 2-4Fw2")

        self.assertTrue(algo.has_internal_rotations)

        algo = parse_moves("B' R2 U 2-4f2")

        self.assertTrue(algo.has_internal_rotations)

        algo = parse_moves("B' R2 U x")

        self.assertFalse(algo.has_internal_rotations)
