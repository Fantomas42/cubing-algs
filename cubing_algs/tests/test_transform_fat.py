import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.degrip import degrip_full_moves
from cubing_algs.transform.fat import refat
from cubing_algs.transform.fat import refat_moves
from cubing_algs.transform.fat import unfat_rotation_moves
from cubing_algs.transform.fat import unfat_slice_moves
from cubing_algs.transform.rotation import remove_final_rotations


class TransformFatTestCase(unittest.TestCase):

    def test_unfat_rotation_moves(self):
        provide = parse_moves('f r u')
        expect = parse_moves('B z L x D y')

        result = unfat_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_rotation_moves_part_two(self):
        provide = parse_moves('b l d')
        expect = parse_moves("F z' R x' U y'")

        result = unfat_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_rotation_moves_part_three(self):
        provide = parse_moves('r F u b')
        expect = parse_moves("L x F D y F z'")

        result = unfat_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_rotation_moves_cleaned(self):
        provide = parse_moves('f r u')
        expect = parse_moves('B D B')

        result = remove_final_rotations(
            degrip_full_moves(
                unfat_rotation_moves(
                    provide,
                ),
            ),
        )

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_rotation_moves_cleaned_part_two(self):
        provide = parse_moves('b l d')
        expect = parse_moves('F D B')

        result = remove_final_rotations(
            degrip_full_moves(
                unfat_rotation_moves(
                    provide,
                ),
            ),
        )

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_slice_moves(self):
        provide = parse_moves('f r u')
        expect = parse_moves("F S R M' U E'")

        result = unfat_slice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_slice_moves_part_two(self):
        provide = parse_moves('b l d')
        expect = parse_moves("B S' L M D E")

        result = unfat_slice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_slice_moves_part_three(self):
        provide = parse_moves('r F u b')
        expect = parse_moves("R M' F U E' B S'")

        result = unfat_slice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_timed_moves(self):
        provide = parse_moves('f@1 r@2 u@3')
        expect = parse_moves('B@1 z@1 L@2 x@2 D@3 y@3')

        result = unfat_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_timed_pauses(self):
        provide = parse_moves('f@1 .@2 r@3 u@4')
        expect = parse_moves('B@1 z@1 .@2 L@3 x@3 D@4 y@4')

        result = unfat_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_refat_moves(self):
        provide = parse_moves('L x')
        expect = parse_moves('r')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_refat_moves_alt(self):
        provide = parse_moves('x L')
        expect = parse_moves('r')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_refat_moves_mixed(self):
        provide = parse_moves('L x f')
        expect = parse_moves('r f')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_refat_moves_mixed_big_moves(self):
        provide = parse_moves('L x 2F')
        expect = parse_moves('r 2F')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('2L x 2F')
        expect = parse_moves('2L x 2F')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_refat_moves_mixed_timed_moves(self):
        provide = parse_moves('L@1 x@2 F@3')
        expect = parse_moves('r@1 F@3')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("L'@1 x'@2 F@3")
        expect = parse_moves("r'@1 F@3")

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_refat_moves_mixed_timed_moves_timed_pauses(self):
        provide = parse_moves('L@1 x@2 .@3 F@4')
        expect = parse_moves('r@1 .@3 F@4')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('L@1 x@2 F@3 .@4')
        expect = parse_moves('r@1 F@3 .@4')

        result = refat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_refat_max(self):
        provide = parse_moves('L x')

        self.assertEqual(
            refat(provide, {}, 0),
            provide,
        )
