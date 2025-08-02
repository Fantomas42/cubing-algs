import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.rotation import compress_final_rotations
from cubing_algs.transform.rotation import compress_rotations
from cubing_algs.transform.rotation import optimize_conjugate_rotations
from cubing_algs.transform.rotation import optimize_double_rotations
from cubing_algs.transform.rotation import optimize_triple_rotations
from cubing_algs.transform.rotation import remove_final_rotations
from cubing_algs.transform.rotation import split_moves_final_rotations


class TransformRemoveFinalRotationsTestCase(unittest.TestCase):

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


class SplitMovesFinalRotationsTestCase(unittest.TestCase):

    def test_split_moves_final_rotations(self):
        provide = parse_moves("R2 F x x x'")
        expect = (parse_moves('R2 F'), parse_moves("x x x'"))

        result = split_moves_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result[1]:
            self.assertTrue(isinstance(m, Move))

    def test_split_moves_final_rotations_empty(self):
        provide = parse_moves('R2 F')
        expect = (parse_moves('R2 F'), [])

        result = split_moves_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_split_moves_final_rotations_start(self):
        provide = parse_moves('x R2 F')
        expect = (parse_moves('x R2 F'), [])

        result = split_moves_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )


class TransformOptimizeTripleRotationsTestCase(unittest.TestCase):

    def test_optimize_triple_rotations(self):
        provide = parse_moves('x2 y2 z2')
        expect = []

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        provide = parse_moves('y2 x2 z2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        provide = parse_moves('z2 x2 y2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_optimize_triple_rotations_timed(self):
        provide = parse_moves('x2@0 y2@50 z2@100')
        expect = []

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_optimize_triple_rotations_start(self):
        provide = parse_moves('x2 x2 y2 z2')
        expect = parse_moves('x2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_triple_rotations_end(self):
        provide = parse_moves('x2 y2 z2 x2')
        expect = parse_moves('x2')

        result = optimize_triple_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_triple_rotations_max(self):
        provide = parse_moves('x2 y2 z2')

        result = optimize_triple_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )


class TransformOptimizeDoubleRotationsTestCase(unittest.TestCase):

    def test_optimize_double_rotations(self):
        provide = parse_moves('x2 y2')
        expect = parse_moves('z2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('z2 x2')
        expect = parse_moves('y2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('z2 y2')
        expect = parse_moves('x2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_timed(self):
        provide = parse_moves('x2@50 y2@100')
        expect = parse_moves('z2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_start(self):
        provide = parse_moves('x x2 y2')
        expect = parse_moves('x z2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_end(self):
        provide = parse_moves('x2 y2 x')
        expect = parse_moves('z2 x')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_multiple(self):
        provide = parse_moves('x2 y2 x2')
        expect = parse_moves('y2')

        result = optimize_double_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_double_rotations_max(self):
        provide = parse_moves('x2 y2')

        result = optimize_double_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )


class TransformOptimizeConjugateRotationsTestCase(unittest.TestCase):

    def test_optimize_conjugate_rotations(self):
        provide = parse_moves("y x2 y'")
        expect = parse_moves('z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("y' x2 y")
        expect = parse_moves('z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("z x2 z'")
        expect = parse_moves('y2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("z' y2 z")
        expect = parse_moves('x2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_timed(self):
        provide = parse_moves("y@0 x2@50 y'@100")
        expect = parse_moves('z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_start(self):
        provide = parse_moves("x x y2 x'")
        expect = parse_moves('x z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_end(self):
        provide = parse_moves("x y2 x' x")
        expect = parse_moves('z2 x')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_multiple(self):
        provide = parse_moves("x' z2 x y x2 y'")
        expect = parse_moves('y2 z2')

        result = optimize_conjugate_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_optimize_conjugate_rotations_max(self):
        provide = parse_moves("y x2 y'")

        result = optimize_conjugate_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )


class TransformCompressRotationsTestCase(unittest.TestCase):

    def test_compress_rotations(self):
        provide = parse_moves("x' z2 x y x2 y'")
        expect = parse_moves('x2')

        result = compress_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_rotations_issues_01(self):
        provide = parse_moves("z@27089 y y z' z' z x x")
        expect = []

        result = compress_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_rotations_impossible(self):
        provide = parse_moves('x')

        result = compress_rotations(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_rotations_max(self):
        provide = parse_moves("x' z2 x y x2 y'")

        result = compress_rotations(provide, 0)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformCompressFinalRotationsTestCase(unittest.TestCase):

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

    def test_compress_final_rotations_double_double(self):
        provide = parse_moves('R2 F x2 z2')
        expect = parse_moves('R2 F y2')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('R2 F x2 y2')
        expect = parse_moves('R2 F z2')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('R2 F y2 z2')
        expect = parse_moves('R2 F x2')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_trible_double(self):
        provide = parse_moves('R2 F x2 z2 y2')
        expect = parse_moves('R2 F')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_trible_double_failed(self):
        provide = parse_moves('R2 F x2 z2 y')
        expect = parse_moves("R2 F y'")

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_simple_double_simple(self):
        provide = parse_moves("R2 F x z2 x'")
        expect = parse_moves('R2 F y2')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("R2 F x' z2 x")
        expect = parse_moves('R2 F y2')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_simple_double_simple_clear(self):
        provide = parse_moves("R2 F x z2 x' y2")
        expect = parse_moves('R2 F')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("R2 F x' z2 x y2")
        expect = parse_moves('R2 F')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_compress_final_rotations_complex(self):
        provide = parse_moves("R2 F z2 x z2 x' y2 x x y2")
        expect = parse_moves('R2 F')

        result = compress_final_rotations(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
