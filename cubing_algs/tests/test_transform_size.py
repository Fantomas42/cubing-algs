import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.size import compress_moves
from cubing_algs.transform.size import expand_moves


class TransformCompressTestCase(unittest.TestCase):

    def test_compress_moves(self):
        provide = parse_moves(
            "U (R U2 R' U' R U' R') "
            "(R U2 R' U' R U' R') "
            "(R U2 R' U' R U' R')",
            secure=False,
        )
        expect = parse_moves("U R U2 R' U' R U R' U' R U R' U' R U' R'")

        result = compress_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_big_moves(self):
        provide = parse_moves(
            "3-4Uw (R U2 R' U' R U' 2R') "
            "(2R U2 R' U' R U' R') "
            "(R U2 R' U' R U' 4R')",
            secure=False,
        )
        expect = parse_moves("3-4Uw R U2 R' U' R U R' U' R U R' U' R U' 4R'")

        result = compress_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_moves_timed(self):
        provide = parse_moves(
            "U@1 (R@2 U2@3 R'@4 U'@5 R@6 U'@7 R'@8) "
            "(R@9 U2@10 R'@11 U'@12 R@13 U'@14 R'@15) "
            "(R@16 U2@17 R'@18 U'@19 R@20 U'@21 R'@22)",
            secure=False,
        )

        expect = parse_moves(
            "U@1 R@2 U2@3 R'@4 U'@5 R@6 U@7 "
            "R'@11 U'@12 R@13 U@14 "
            "R'@18 U'@19 R@20 U'@21 R'@22",
        )

        result = compress_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_moves_timed_paused(self):
        provide = parse_moves(
            "U@0 .@1 (R@2 U2@3 R'@4 U'@5 R@6 U'@7 R'@8) "
            "(R@9 U2@10 R'@11 U'@12 R@13 U'@14 R'@15) "
            "(R@16 U2@17 R'@18 U'@19 R@20 U'@21 R'@22)",
            secure=False,
        )

        expect = parse_moves(
            "U@0 .@1 R@2 U2@3 R'@4 U'@5 R@6 U@7 "
            "R'@11 U'@12 R@13 U@14 "
            "R'@18 U'@19 R@20 U'@21 R'@22",
        )

        result = compress_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_moves_timed_paused_middle(self):
        provide = parse_moves(
            "U@1 (R@2 U2@3 R'@4 U'@5 R@6 U'@7 R'@8) "
            "(R@9 .@9 U2@10 R'@11 U'@12 R@13 U'@14 R'@15) "
            "(R@16 U2@17 R'@18 U'@19 R@20 U'@21 R'@22)",
            secure=False,
        )

        expect = parse_moves(
            "U@1 R@2 U2@3 R'@4 U'@5 R@6 U'@7 "
            ".@9 U2@10 R'@11 U'@12 R@13 U@14 "
            "R'@18 U'@19 R@20 U'@21 R'@22",
        )

        result = compress_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_pauses(self):
        provide = parse_moves(
            'U . . . U',
        )

        expect = parse_moves(
            'U . . . U',
        )

        result = compress_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_pauses_timed(self):
        provide = parse_moves(
            'U@1 .@2 .@3 .@4 U@5',
        )

        expect = parse_moves(
            'U@1 .@2 .@3 .@4 U@5',
        )

        result = compress_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_moves_max(self):
        provide = parse_moves(
            "U (R U2 R' U' R U' R') "
            "(R U2 R' U' R U' R') "
            "(R U2 R' U' R U' R')",
            secure=False,
        )

        result = compress_moves(provide, 0)

        self.assertEqual(
            result,
            provide,
        )


class TransformExpandTestCase(unittest.TestCase):

    def test_expand_moves(self):
        provide = parse_moves('R2 F U')
        expect = parse_moves('R R F U')

        result = expand_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_expand_big_moves(self):
        provide = parse_moves('2R2 F U')
        expect = parse_moves('2R 2R F U')

        result = expand_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_expand_timed_moves(self):
        provide = parse_moves('2R2@1 F@2 U@3')
        expect = parse_moves('2R@1 2R@1 F@2 U@3')

        result = expand_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_expand_timed_moves_paused(self):
        provide = parse_moves('2R2@1 .@2 F@3 U@4')
        expect = parse_moves('2R@1 2R@1 .@2 F@3 U@4')

        result = expand_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
