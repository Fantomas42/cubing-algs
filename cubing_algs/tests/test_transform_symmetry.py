import unittest

from cubing_algs.parsing import parse_moves
from cubing_algs.transform.symmetry import symmetry_c_moves
from cubing_algs.transform.symmetry import symmetry_e_moves
from cubing_algs.transform.symmetry import symmetry_m_moves
from cubing_algs.transform.symmetry import symmetry_s_moves


class TransformSymmetryTestCase(unittest.TestCase):

    def test_symmetry_c_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("U' R' U R")

        self.assertEqual(
            symmetry_s_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("F R' U2")
        expect = parse_moves("B L' U2")

        self.assertEqual(
            symmetry_c_moves(provide.moves),
            expect.moves,
        )

    def test_symmetry_e_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("D' R' D R")

        self.assertEqual(
            symmetry_e_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("F R' U2")
        expect = parse_moves("F' R D2")

        self.assertEqual(
            symmetry_e_moves(provide.moves),
            expect.moves,
        )

    def test_symmetry_m_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("U' L' U L")

        self.assertEqual(
            symmetry_m_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("F R' U2")
        expect = parse_moves("F' L U2")

        self.assertEqual(
            symmetry_m_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("F R' U2 M'")
        expect = parse_moves("F' L U2 M'")

        self.assertEqual(
            symmetry_m_moves(provide.moves),
            expect.moves,
        )

    def test_symmetry_s_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("U' R' U R")

        self.assertEqual(
            symmetry_s_moves(provide.moves),
            expect.moves,
        )

        provide = parse_moves("F R' U2")
        expect = parse_moves("B' R U2")

        self.assertEqual(
            symmetry_s_moves(provide.moves),
            expect.moves,
        )
