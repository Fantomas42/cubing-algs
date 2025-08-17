import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.symmetry import symmetry_c_moves
from cubing_algs.transform.symmetry import symmetry_e_moves
from cubing_algs.transform.symmetry import symmetry_m_moves
from cubing_algs.transform.symmetry import symmetry_s_moves


class TransformSymmetryTestCase(unittest.TestCase):

    def test_symmetry_c_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("U L U' L'")

        result = symmetry_c_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("F R' U2")
        expect = parse_moves("B L' U2")

        self.assertEqual(
            symmetry_c_moves(provide),
            expect,
        )

    def test_symmetry_e_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("D' R' D R")

        self.assertEqual(
            symmetry_e_moves(provide),
            expect,
        )

        provide = parse_moves("F R' U2")
        expect = parse_moves("F' R D2")

        self.assertEqual(
            symmetry_e_moves(provide),
            expect,
        )

    def test_symmetry_m_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("U' L' U L")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )

        provide = parse_moves("F R' U2")
        expect = parse_moves("F' L U2")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )

        provide = parse_moves("F R' U2 M'")
        expect = parse_moves("F' L U2 M'")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )

    def test_symmetry_m_moves_sign(self):
        provide = parse_moves("U R u' r'")
        expect = parse_moves("U' L' u l")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )

    def test_symmetry_m_moves_wide_standard(self):
        provide = parse_moves("U R Uw' Rw'")
        expect = parse_moves("U' L' Uw Lw")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )

    def test_symmetry_s_moves(self):
        provide = parse_moves("U R U' R'")
        expect = parse_moves("U' R' U R")

        self.assertEqual(
            symmetry_s_moves(provide),
            expect,
        )

        provide = parse_moves("F R' U2")
        expect = parse_moves("B' R U2")

        self.assertEqual(
            symmetry_s_moves(provide),
            expect,
        )

    def test_symmetry_m_moves_big_moves(self):
        provide = parse_moves("U R 2Uw' 3Rw'")
        expect = parse_moves("U' L' 2Uw 3Lw")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )

    def test_symmetry_m_moves_big_moves_timed(self):
        provide = parse_moves("U R 2Uw'@300 3Rw'")
        expect = parse_moves("U' L' 2Uw@300 3Lw")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )

    def test_symmetry_m_moves_big_moves_timed_paused(self):
        provide = parse_moves("U R .@200 2Uw'@300 3Rw'")
        expect = parse_moves("U' L' .@200 2Uw@300 3Lw")

        self.assertEqual(
            symmetry_m_moves(provide),
            expect,
        )
