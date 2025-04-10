import unittest

from cubing_algs.parsing import parse_moves
from cubing_algs.transform.slice import unslice_rotation_moves
from cubing_algs.transform.slice import unslice_wide_moves


class TransformSliceTestCase(unittest.TestCase):

    def test_unslice_rotation_moves(self):
        provide = parse_moves('M2 U S E')
        expect = parse_moves("L2R2x2UF'BzD'Uy'")

        self.assertEqual(
            unslice_rotation_moves(provide.moves),
            expect.moves,
        )

    def test_unslice_wide_moves(self):
        provide = parse_moves('M2 U S E')
        expect = parse_moves("r2R2UfF'u'U")

        self.assertEqual(
            unslice_wide_moves(provide.moves),
            expect.moves,
        )
