import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves


class TransformMirrorTestCase(unittest.TestCase):

    def test_mirror_moves(self):
        provide = parse_moves(
            "F R U2 F'",
        )
        expect = parse_moves("F U2 R' F'")

        result = mirror_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_mirror_big_moves(self):
        provide = parse_moves(
            "2Fw R 3U2 3f'",
        )
        expect = parse_moves("3f 3U2 R' 2Fw'")

        result = mirror_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_timed_moves(self):
        provide = parse_moves(
            "F@1 R@2 U2@3 F'@4",
        )
        expect = parse_moves("F@4 U2@3 R'@2 F'@1")

        result = mirror_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_timed_moves_with_pauses(self):
        provide = parse_moves(
            "F@1 .@2 R@3 U2@4 F'@5",
        )
        expect = parse_moves("F@5 U2@4 R'@3 .@2 F'@1")

        result = mirror_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
