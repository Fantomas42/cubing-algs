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
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R'")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves('R R R U')
        expect = parse_moves("R' U")

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R' U F")
        expect = parse_moves('R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R' 2R' U F")
        expect = parse_moves('2R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 2R'@300 U@400 F@500")
        expect = parse_moves('2R@300 U@400 F@500')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R'@200 2R'@300 U@400 F@500")
        expect = parse_moves("2R'@100 .@150 2R'@200 2R'@300 U@400 F@500")

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("U F R' R' R' U F")
        expect = parse_moves('U F R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_repeat_three_moves(provide, 0),
            provide,
        )

        provide = parse_moves('U . . . U')
        expect = parse_moves('U . . . U')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

    def test_optimize_do_undo_moves(self):
        provide = parse_moves("R R'")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R R' U")
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R@200 U@300 F@400")
        expect = parse_moves('U@300 F@400')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R@200 U@300 F@400")
        expect = parse_moves("2R'@100 .@150 2R@200 U@300 F@400")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("U F R' R U F")
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_do_undo_moves(provide, 0),
            provide,
        )

        provide = parse_moves('U . . . U')
        expect = parse_moves('U . . . U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_do_undo_double_moves(self):
        provide = parse_moves("R R R' R'")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R R")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R R R' R' U")
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R' 2R 2R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 2R@300 2R@400 U@500 F@600")
        expect = parse_moves('U@500 F@600')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 .@250 2R@300 2R@400 U@500 F@600")
        expect = parse_moves("2R'@100 2R'@200 .@250 2R@300 2R@400 U@500 F@600")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("U F R' R' R R U F")
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_do_undo_double_double_moves(self):
        provide = parse_moves('R2 R2')
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('R2 R2 U')
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('R2 R2 U F')
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('2R2 2R2 U F')
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('2R2@100 2R2@200 U@300 F@400')
        expect = parse_moves('U@300 F@400')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('2R2@100 .@150 2R2@200 U@300 F@400')
        expect = parse_moves('2R2@100 .@150 2R2@200 U@300 F@400')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('U F R2 R2 U F')
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_double_moves(self):
        provide = parse_moves('R R')
        expect = parse_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("R' R'")
        expect = parse_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves('R R U')
        expect = parse_moves('R2 U')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' U F")
        expect = parse_moves('R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R' U F")
        expect = parse_moves('2R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 U@300 F@400")
        expect = parse_moves('2R2@200 U@300 F@400')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R'@200 U@300 F@400")
        expect = parse_moves("2R'@100 .@150 2R'@200 U@300 F@400")

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 .@175 2R'@200 U@300 F@400")
        expect = parse_moves("2R'@100 .@150 .@175 2R'@200 U@300 F@400")

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves('U . . U')
        expect = parse_moves('U . . U')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves('U F R R U F')
        expect = parse_moves('U F R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_double_moves(provide, 0),
            provide,
        )

    def test_optimize_double_moves_issue_1(self):
        provide = parse_moves('R R R2 F')
        expect = parse_moves('R2 R2 F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

    def test_optimize_triple_moves(self):
        provide = parse_moves('R R2')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R' R2")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('R2 R')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R2 R'")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R' R2 U")
        expect = parse_moves('R U')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R2 R' U F")
        expect = parse_moves('R U F')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R2 R' U F F")
        expect = parse_moves('R U F F')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R2 2R' U F F")
        expect = parse_moves('2R U F F')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R2@100 2R'@200 U@300 F@400 F@500")
        expect = parse_moves('2R@200 U@300 F@400 F@500')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R2@200 U@300 F@400 F@500")
        expect = parse_moves('2R@100 U@300 F@400 F@500')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R2@200 U@300 F@400 F@500")
        expect = parse_moves("2R'@100 .@150 2R2@200 U@300 F@400 F@500")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('U F R2 R U F')
        expect = parse_moves("U F R' U F")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_triple_moves(provide, 0),
            provide,
        )

        provide = parse_moves('U . . . U')
        expect = parse_moves('U . . . U')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )
