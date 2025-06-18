import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.pause import unpause_moves


class TransformUnpauseTestCase(unittest.TestCase):

    def test_unpause_moves(self):
        provide = parse_moves(
            "F@1 R@2 .@3 U2@4 F'@5",
        )
        expect = parse_moves("F@1 R@2 U2@4 F'@5")

        result = unpause_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unpause_moves_untimed(self):
        provide = parse_moves(
            "F@1 R . U2 F'@4",
        )
        expect = parse_moves("F@1 R U2 F'@4")

        result = unpause_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
