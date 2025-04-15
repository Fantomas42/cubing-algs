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
