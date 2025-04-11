import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.size import compress_moves
from cubing_algs.transform.size import expand_moves


class TransformSizeTestCase(unittest.TestCase):

    def test_compress_moves(self):
        provide = parse_moves(
            "U (R U2 R' U' R U' R') "
            "(R U2 R' U' R U' R') "
            "(R U2 R' U' R U' R')",
        )
        expect = parse_moves("U R U2 R' U' R U R' U' R U R' U' R U' R'")

        result = compress_moves(provide.moves)

        self.assertEqual(
            result,
            expect.moves,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_expand_moves(self):
        provide = parse_moves('R2 F U')
        expect = parse_moves('R R F U')

        result = expand_moves(provide.moves)

        self.assertEqual(
            result,
            expect.moves,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
