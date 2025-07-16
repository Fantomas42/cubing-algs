import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.rotation import compress_final_rotations
from cubing_algs.transform.rotation import remove_final_rotations


class TransformRemoveRotationTestCase(unittest.TestCase):

    def test_remove_final_rotations(self):
        provide = parse_moves('R2 F U x y2')
        expect = parse_moves('R2 F U')

        result = remove_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_final_rotations_timed(self):
        provide = parse_moves('R2@1 F@2 U@3 x@4 y2@5')
        expect = parse_moves('R2@1 F@2 U@3')

        result = remove_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_final_rotations_timed_paused(self):
        provide = parse_moves('R2@1 F@2 U@3 x@4 .@5 y2@6')
        expect = parse_moves('R2@1 F@2 U@3')

        result = remove_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('R2@1 F@2 U@3 .@4 x@5 .@6 y2@7')
        expect = parse_moves('R2@1 F@2 U@3')

        result = remove_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformCompressRotationTestCase(unittest.TestCase):

    def test_compress_final_rotations(self):
        provide = parse_moves("R2 F x x x' x x x")
        expect = parse_moves('R2 F')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_empty(self):
        provide = parse_moves('R2 F')
        expect = parse_moves('R2 F')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_timed(self):
        provide = parse_moves("R2@1 F@2 x'@3 x@4")
        expect = parse_moves('R2@1 F@2')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_impair(self):
        provide = parse_moves("R2 F x' x x'")
        expect = parse_moves("R2 F x'")

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
