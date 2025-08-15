import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.offset import offset_x2_moves
from cubing_algs.transform.offset import offset_x_moves
from cubing_algs.transform.offset import offset_xprime_moves
from cubing_algs.transform.offset import offset_y2_moves
from cubing_algs.transform.offset import offset_y_moves
from cubing_algs.transform.offset import offset_yprime_moves
from cubing_algs.transform.offset import offset_z2_moves
from cubing_algs.transform.offset import offset_z_moves
from cubing_algs.transform.offset import offset_zprime_moves


class TransformOffsetTestCase(unittest.TestCase):

    def test_offset_x_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R B R' B'")

        result = offset_x_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_offset_x_moves_wide_standard(self):
        provide = parse_moves("R U Rw' Uw'")
        expect = parse_moves("R B Rw' Bw'")

        result = offset_x_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_offset_x_moves_wide_sign(self):
        provide = parse_moves("R U r' u'")
        expect = parse_moves("R B r' b'")

        result = offset_x_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_offset_x2_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R D R' D'")

        self.assertEqual(
            offset_x2_moves(provide),
            expect,
        )

    def test_offset_xprime_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R F R' F'")

        self.assertEqual(
            offset_xprime_moves(provide),
            expect,
        )

    def test_offset_y_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("F U F' U'")

        self.assertEqual(
            offset_y_moves(provide),
            expect,
        )

    def test_offset_y2_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("L U L' U'")

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

    def test_offset_yprime_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("B U B' U'")

        self.assertEqual(
            offset_yprime_moves(provide),
            expect,
        )

    def test_offset_z_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("D R D' R'")

        self.assertEqual(
            offset_z_moves(provide),
            expect,
        )

    def test_offset_z2_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("L D L' D'")

        self.assertEqual(
            offset_z2_moves(provide),
            expect,
        )

    def test_offset_zprime_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("U L U' L'")

        self.assertEqual(
            offset_zprime_moves(provide),
            expect,
        )

    def test_offset_big_moves(self):
        provide = parse_moves('3R')
        expect = parse_moves('3L')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves('3R2')
        expect = parse_moves('3L2')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves("3R'")
        expect = parse_moves("3L'")

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

    def test_offset_big_moves_timed(self):
        provide = parse_moves('3R@100')
        expect = parse_moves('3L@100')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves('3R2@100')
        expect = parse_moves('3L2@100')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

        provide = parse_moves("3R'@100")
        expect = parse_moves("3L'@100")

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )

    def test_offset_big_moves_timed_with_pauses(self):
        provide = parse_moves('.@50 3R@100 .@150')
        expect = parse_moves('.@50 3L@100 .@150')

        self.assertEqual(
            offset_y2_moves(provide),
            expect,
        )
