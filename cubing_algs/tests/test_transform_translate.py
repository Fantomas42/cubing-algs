"""Tests for algorithm translation transformation functions."""

import unittest

from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.translate import translate_moves
from cubing_algs.transform.translate import translate_pov_moves


class TransformTranslateTestCase(unittest.TestCase):

    def test_translate_z2(self) -> None:
        # z2 (DR) is symmetric: should be easy
        orientation = parse_moves('z2')
        provide = parse_moves("L D L' D'")
        expect = parse_moves("R U R' U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_y_z2(self) -> None:
        # y z2 (DR)
        orientation = parse_moves('y z2')
        provide = parse_moves("F D F' D'")
        expect = parse_moves("R U R' U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_z_y(self) -> None:
        # z y (LU)
        orientation = parse_moves('z y')
        provide = parse_moves("L B2 L' U' F U' L'")
        expect = parse_moves("U R2 U' F' L F' U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_x_y(self) -> None:
        # x y (FR)
        orientation = parse_moves('x y')
        provide = parse_moves("R U R'")
        expect = parse_moves("F R F'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(result, expect)

    def test_translate_z2_with_pause(self) -> None:
        orientation = parse_moves('z2')
        provide = parse_moves("L . D L' . D'")
        expect = parse_moves("R . U R' . U'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_z2_timed(self) -> None:
        orientation = parse_moves('z2')
        provide = parse_moves("L@10 .@20 D@30 L'@40 .@50 D'@60")
        expect = parse_moves("R@10 .@20 U@30 R'@40 .@50 U'@60")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_invalid_orientation(self) -> None:
        orientation = parse_moves('x F')
        provide = parse_moves("L D L' D'")

        with self.assertRaises(InvalidMoveError):
            translate_moves(orientation)(provide)

    def test_translate_no_orientation(self) -> None:
        orientation = parse_moves('')
        provide = parse_moves("L D L' D'")

        result = translate_moves(orientation)(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformTranslatePOVTestCase(unittest.TestCase):

    def test_translate_pov_z2(self) -> None:
        provide = parse_moves("z2 L D L' D'")
        expect = parse_moves("z2 R U R' U'")

        result = translate_pov_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_y_middle(self) -> None:
        provide = parse_moves("R U R' U' y B U B' U'")
        expect = parse_moves("R U R' U' y R U R' U'")

        result = translate_pov_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_translate_pov_z2_timed(self) -> None:
        provide = parse_moves("z2@0 L@10 D@20 L'@30 D'@40")
        expect = parse_moves("z2@0 R@10 U@20 R'@30 U'@40")

        result = translate_pov_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
