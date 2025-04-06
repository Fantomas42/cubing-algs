import unittest

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

        self.assertEqual(
            offset_x_moves(provide.moves),
            expect.moves,
        )

    def test_offset_x2_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R D R' D'")

        self.assertEqual(
            offset_x2_moves(provide.moves),
            expect.moves,
        )

    def test_offset_xprime_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("R F R' F'")

        self.assertEqual(
            offset_xprime_moves(provide.moves),
            expect.moves,
        )

    def test_offset_y_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("F U F' U'")

        self.assertEqual(
            offset_y_moves(provide.moves),
            expect.moves,
        )

    def test_offset_y2_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("L U L' U'")

        self.assertEqual(
            offset_y2_moves(provide.moves),
            expect.moves,
        )

    def test_offset_yprime_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("B U B' U'")

        self.assertEqual(
            offset_yprime_moves(provide.moves),
            expect.moves,
        )

    def test_offset_z_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("D R D' R'")

        self.assertEqual(
            offset_z_moves(provide.moves),
            expect.moves,
        )

    def test_offset_z2_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("L D L' D'")

        self.assertEqual(
            offset_z2_moves(provide.moves),
            expect.moves,
        )

    def test_offset_zprime_moves(self):
        provide = parse_moves("R U R' U'")
        expect = parse_moves("U L U' L'")

        self.assertEqual(
            offset_zprime_moves(provide.moves),
            expect.moves,
        )
