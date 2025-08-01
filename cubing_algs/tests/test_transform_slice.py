import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.slice import reslice
from cubing_algs.transform.slice import reslice_e_moves
from cubing_algs.transform.slice import reslice_e_timed_moves
from cubing_algs.transform.slice import reslice_m_moves
from cubing_algs.transform.slice import reslice_m_timed_moves
from cubing_algs.transform.slice import reslice_moves
from cubing_algs.transform.slice import reslice_s_moves
from cubing_algs.transform.slice import reslice_s_timed_moves
from cubing_algs.transform.slice import reslice_timed_moves
from cubing_algs.transform.slice import unslice_rotation_moves
from cubing_algs.transform.slice import unslice_wide_moves


class TransformSliceTestCase(unittest.TestCase):

    def test_unslice_rotation_moves(self):
        provide = parse_moves('M2 U S E')
        expect = parse_moves("L2 R2 x2 U F' B z D' U y'")

        result = unslice_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unslice_wide_moves(self):
        provide = parse_moves('M2 U S E')
        expect = parse_moves("r2 R2 U f F' u' U")

        result = unslice_wide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unslice_timed_moves(self):
        provide = parse_moves('M2@1 U@2 S@3 E@4')
        expect = parse_moves(
            "L2@1 R2@1 x2@1 U@2 F'@3 B@3 z@3 D'@4 U@4 y'@4",
        )

        result = unslice_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unslice_timed_moves_pauses(self):

        provide = parse_moves('M2@1 .@2 U@3 S@4 E@5')
        expect = parse_moves(
            "L2@1 R2@1 x2@1 .@2 U@3 F'@4 B@4 z@4 D'@5 U@5 y'@5",
        )

        result = unslice_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_moves(self):
        provide = parse_moves("U' D")
        expect = parse_moves("E' y'")

        result = reslice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_moves_alt(self):
        provide = parse_moves("D U'")
        expect = parse_moves("E' y'")

        result = reslice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_moves_fat(self):
        provide = parse_moves("r' R")
        expect = parse_moves('M')

        result = reslice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_moves_fat_alt(self):
        provide = parse_moves("R r'")
        expect = parse_moves('M')

        result = reslice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_e_moves(self):
        provide = parse_moves("U' D F")
        expect = parse_moves("E' y' F")

        result = reslice_e_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_m_moves(self):
        provide = parse_moves("L' R F")
        expect = parse_moves('M x F')

        result = reslice_m_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_m_moves_timed(self):
        provide = parse_moves("L'@100 R@200 F@300")
        expect = parse_moves('M@100 x@100 F@300')

        result = reslice_m_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_m_moves_big(self):
        provide = parse_moves("L' R 2F")
        expect = parse_moves('M x 2F')

        result = reslice_m_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("2L' R 2F")
        expect = parse_moves("2L' R 2F")

        result = reslice_m_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_m_moves_big_timed(self):
        provide = parse_moves("L' R 2F@200")
        expect = parse_moves('M x 2F@200')

        result = reslice_m_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("2L'@100 R@200 2F@300")
        expect = parse_moves("2L'@100 R@200 2F@300")

        result = reslice_m_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_m_moves_big_timed_pauses(self):
        provide = parse_moves("L' . R 2F@200")
        expect = parse_moves("L' . R 2F@200")

        result = reslice_m_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_s_moves(self):
        provide = parse_moves("B' F F")
        expect = parse_moves("S' z F")

        result = reslice_s_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_max(self):
        provide = parse_moves("U' D")

        self.assertEqual(
            reslice(provide, {}, 0),
            provide,
        )


class TransformSliceTimedTestCase(unittest.TestCase):

    def test_reslice_timed_moves(self):
        provide = parse_moves("U'@100 D@150")
        expect = parse_moves("E'@100 y'@100")

        result = reslice_timed_moves(50)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_timed_moves_failed(self):
        provide = parse_moves("U'@100 D@150")

        result = reslice_timed_moves(10)(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_timed_moves_without_time(self):
        provide = parse_moves("U' D")
        expect = parse_moves("E'y'")

        result = reslice_timed_moves()(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_m_timed_moves(self):
        provide = parse_moves("L'@0 R@30 F@70")
        expect = parse_moves('M@0 x@0 F@70')

        result = reslice_m_timed_moves(50)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_s_timed_moves(self):
        provide = parse_moves("B'@0 F@30 F@70")
        expect = parse_moves("S'@0 z@0 F@70")

        result = reslice_s_timed_moves(50)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_e_timed_moves(self):
        provide = parse_moves("U'@0 D@30 F@70")
        expect = parse_moves("E'@0 y'@0 F@70")

        result = reslice_e_timed_moves(50)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
