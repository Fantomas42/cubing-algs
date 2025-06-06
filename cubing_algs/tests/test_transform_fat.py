import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.degrip import degrip_full_moves
from cubing_algs.transform.fat import refat_moves
from cubing_algs.transform.fat import unfat_moves
from cubing_algs.transform.rotation import remove_final_rotations


class TransformFatTestCase(unittest.TestCase):

    def test_unfat_moves(self):
        provide = parse_moves('f r u')
        expect = parse_moves('B z L x D y')

        result = unfat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_moves_part_two(self):
        provide = parse_moves('b l d')
        expect = parse_moves("F z' R x' U y'")

        result = unfat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_moves_part_three(self):
        provide = parse_moves('r F u b')
        expect = parse_moves("L x F D y F z'")

        result = unfat_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unfat_moves_cleaned(self):
        provide = parse_moves('f r u')
        expect = parse_moves('B D B')

        result = remove_final_rotations(
            degrip_full_moves(
                unfat_moves(
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

    def test_unfat_moves_cleaned_part_two(self):
        provide = parse_moves('b l d')
        expect = parse_moves('F D B')

        result = remove_final_rotations(
            degrip_full_moves(
                unfat_moves(
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

    def test_refat_max(self):
        provide = parse_moves('L x')

        self.assertEqual(
            refat_moves(provide, {}, 0),
            provide,
        )
