import unittest

from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves
from cubing_algs.transform.optimize import optimize_repeat_three_moves
from cubing_algs.transform.optimize import optimize_triple_moves


class TransformOptimizeTestCase(unittest.TestCase):

    def test_optimize_repeat_three_moves(self):
        provide = parse_moves('R R R')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_repeat_three_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R' R'")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_repeat_three_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves('R R R U')
        expect = parse_moves("R' U")

        self.assertEqual(
            optimize_repeat_three_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R' R' U F")
        expect = parse_moves('R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("U F R' R' R' U F")
        expect = parse_moves('U F R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide.moves),
            expect.moves,
        )

    def test_optimize_do_undo_moves(self):
        provide = parse_moves("R R'")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect,
        )

        provide = parse_moves("R' R")

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect,
        )

        provide = parse_moves("R R' U")
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("U F R' R U F")
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

    def test_optimize_do_undo_double_moves(self):
        provide = parse_moves("R R R' R'")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect,
        )

        provide = parse_moves("R' R' R R")

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect,
        )

        provide = parse_moves("R R R' R' U")
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R' R R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("U F R' R' R R U F")
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

    def test_optimize_do_undo_double_double_moves(self):
        provide = parse_moves('R2 R2')
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect,
        )

        provide = parse_moves('R2 R2 U')
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves('R2 R2 U F')
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves('U F R2 R2 U F')
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide.moves),
            expect.moves,
        )

    def test_optimize_double_moves(self):
        provide = parse_moves('R R')
        expect = parse_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R'")
        expect = parse_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves('R R U')
        expect = parse_moves('R2 U')

        self.assertEqual(
            optimize_double_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R' U F")
        expect = parse_moves('R2 U F')

        self.assertEqual(
            optimize_double_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves('U F R R U F')
        expect = parse_moves('U F R2 U F')

        self.assertEqual(
            optimize_double_moves(provide.moves),
            expect.moves,
        )

    def test_optimize_triple_moves(self):
        provide = parse_moves('R R2')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R2")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves('R2 R')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R2 R'")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R' R2 U")
        expect = parse_moves('R U')

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R2 R' U F")
        expect = parse_moves('R U F')

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("R2 R' U F F")
        expect = parse_moves('R U F F')

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves('U F R2 R U F')
        expect = parse_moves("U F R' U F")

        self.assertEqual(
            optimize_triple_moves(provide.moves),
            expect.moves,
        )
