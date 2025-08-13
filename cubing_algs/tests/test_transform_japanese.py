import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.japanese import japanese_moves
from cubing_algs.transform.japanese import unjapanese_moves


class TransformJapaneseTestCase(unittest.TestCase):

    def test_japanese_moves(self):
        provide = parse_moves("R' F u' B r")
        expect = parse_moves("R' F Uw' B Rw")

        result = japanese_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unjapanese_moves(self):
        provide = parse_moves("R' F Uw' B Rw")
        expect = parse_moves("R' F u' B r")

        result = unjapanese_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
