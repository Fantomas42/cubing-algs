import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.slice import reslice_moves
from cubing_algs.transform.slice import unslice_rotation_moves
from cubing_algs.transform.slice import unslice_wide_moves


class TransformSliceTestCase(unittest.TestCase):

    def test_unslice_rotation_moves(self):
        provide = parse_moves('M2 U S E')
        expect = parse_moves("L2R2x2UF'BzD'Uy'")

        result = unslice_rotation_moves(provide.moves)

        self.assertEqual(
            result,
            expect.moves,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unslice_wide_moves(self):
        provide = parse_moves('M2 U S E')
        expect = parse_moves("r2R2UfF'u'U")

        result = unslice_wide_moves(provide.moves)

        self.assertEqual(
            result,
            expect.moves,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_reslice_moves(self):
        provide = parse_moves("U' D")
        expect = parse_moves("E'y'")

        result = reslice_moves(provide.moves)

        self.assertEqual(
            result,
            expect.moves,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
