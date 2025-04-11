import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.rotation import remove_final_rotations


class TransformRotationTestCase(unittest.TestCase):

    def test_remove_final_rotations(self):
        provide = parse_moves('R2 F U x y2')
        expect = parse_moves('R2 F U')

        result = remove_final_rotations(provide.moves)

        self.assertEqual(
            result,
            expect.moves,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
