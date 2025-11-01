"""Tests for AUF transformation functions."""

import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.auf import remove_auf_moves


class TransformRemoveAUFTestCase(unittest.TestCase):

    def test_remove_auf_moves_pre_one(self) -> None:
        provide = parse_moves('U F R B')
        expect = parse_moves('L F R')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_pre_one_prime(self) -> None:
        provide = parse_moves("U' F R B")
        expect = parse_moves('R B L')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_pre_one_double(self) -> None:
        provide = parse_moves('U2 F R B')
        expect = parse_moves('B L F')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_post_one(self) -> None:
        provide = parse_moves('F R B U')
        expect = parse_moves('L F R')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_post_one_prime(self) -> None:
        provide = parse_moves("F R B U'")
        expect = parse_moves('R B L')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_pre_post_double(self) -> None:
        provide = parse_moves('F R B U2')
        expect = parse_moves('B L F')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_pre_pause_double(self) -> None:
        provide = parse_moves('U . U F R B')
        expect = parse_moves('B L F')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_post_pause_double(self) -> None:
        provide = parse_moves('F R B U . U')
        expect = parse_moves('B L F')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_pre_pause_cancel(self) -> None:
        provide = parse_moves("U . U' F R B")
        expect = parse_moves('F R B')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_post_pause_cancel(self) -> None:
        provide = parse_moves("F R B U . U'")
        expect = parse_moves('F R B')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_double_cancel(self) -> None:
        provide = parse_moves('U U F R B U2')
        expect = parse_moves('F R B')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_pre_post(self) -> None:
        provide = parse_moves('U F R B U2')
        expect = parse_moves('R B L')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_pre_post_paused(self) -> None:
        provide = parse_moves('U F R B U . U')
        expect = parse_moves('R B L')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_remove_auf_moves_empty(self) -> None:
        provide = parse_moves('')

        result = remove_auf_moves(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
