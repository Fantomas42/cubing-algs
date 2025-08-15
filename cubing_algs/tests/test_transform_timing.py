import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.timing import untime_moves


class TransformUntimeTestCase(unittest.TestCase):

    def test_untime_moves(self):
        provide = parse_moves(
            "F@1 R@2 U2@3 F'@4",
        )
        expect = parse_moves("F R U2 F'")

        result = untime_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_untime_big_moves(self):
        provide = parse_moves(
            "2Fw@1 R@2 3U2@3 3f'@4",
        )
        expect = parse_moves("2Fw R 3U2 3f'")

        result = untime_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_untime_moves_untimed(self):
        provide = parse_moves(
            "F@1 R U2 F'@4",
        )
        expect = parse_moves("F R U2 F'")

        result = untime_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
