import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.degrip import degrip_full_moves
from cubing_algs.transform.rotation import remove_final_rotations
from cubing_algs.transform.wide import rewide
from cubing_algs.transform.wide import rewide_moves
from cubing_algs.transform.wide import unwide_rotation_moves
from cubing_algs.transform.wide import unwide_slice_moves


class TransformWideTestCase(unittest.TestCase):

    def test_unwide_rotation_moves(self) -> None:
        provide = parse_moves('f r u')
        expect = parse_moves('B z L x D y')

        result = unwide_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unwide_rotation_moves_part_two(self) -> None:
        provide = parse_moves('b l d')
        expect = parse_moves("F z' R x' U y'")

        result = unwide_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unwide_rotation_moves_part_three(self) -> None:
        provide = parse_moves('r F u b')
        expect = parse_moves("L x F D y F z'")

        result = unwide_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unwide_rotation_moves_cleaned(self) -> None:
        provide = parse_moves('f r u')
        expect = parse_moves('B D B')

        result = remove_final_rotations(
            degrip_full_moves(
                unwide_rotation_moves(
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

    def test_unwide_rotation_moves_cleaned_part_two(self) -> None:
        provide = parse_moves('b l d')
        expect = parse_moves('F D B')

        result = remove_final_rotations(
            degrip_full_moves(
                unwide_rotation_moves(
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

    def test_unwide_slice_moves(self) -> None:
        provide = parse_moves('f r u')
        expect = parse_moves("F S R M' U E'")

        result = unwide_slice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unwide_slice_moves_part_two(self) -> None:
        provide = parse_moves('b l d')
        expect = parse_moves("B S' L M D E")

        result = unwide_slice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unwide_slice_moves_part_three(self) -> None:
        provide = parse_moves('r F u b')
        expect = parse_moves("R M' F U E' B S'")

        result = unwide_slice_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unwide_timed_moves(self) -> None:
        provide = parse_moves('f@1 r@2 u@3')
        expect = parse_moves('B@1 z@1 L@2 x@2 D@3 y@3')

        result = unwide_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unwide_timed_pauses(self) -> None:
        provide = parse_moves('f@1 .@2 r@3 u@4')
        expect = parse_moves('B@1 z@1 .@2 L@3 x@3 D@4 y@4')

        result = unwide_rotation_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rewide_moves(self) -> None:
        provide = parse_moves('L x')
        expect = parse_moves('r')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rewide_moves_alt(self) -> None:
        provide = parse_moves('x L')
        expect = parse_moves('r')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rewide_moves_mixed(self) -> None:
        provide = parse_moves('L x f')
        expect = parse_moves('r f')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rewide_moves_mixed_big_moves(self) -> None:
        provide = parse_moves('L x 2F')
        expect = parse_moves('r 2F')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('2L x 2F')
        expect = parse_moves('2L x 2F')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rewide_moves_mixed_timed_moves(self) -> None:
        provide = parse_moves('L@1 x@2 F@3')
        expect = parse_moves('r@1 F@3')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves("L'@1 x'@2 F@3")
        expect = parse_moves("r'@1 F@3")

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rewide_moves_mixed_timed_moves_timed_pauses(self) -> None:
        provide = parse_moves('L@1 x@2 .@3 F@4')
        expect = parse_moves('r@1 .@3 F@4')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

        provide = parse_moves('L@1 x@2 F@3 .@4')
        expect = parse_moves('r@1 F@3 .@4')

        result = rewide_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_rewide_max(self) -> None:
        provide = parse_moves('L x')

        self.assertEqual(
            rewide(provide, {}, 0),
            provide,
        )
