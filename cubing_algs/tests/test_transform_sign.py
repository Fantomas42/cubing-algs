"""Tests for SiGN notation transformation functions."""

import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.sign import sign_moves
from cubing_algs.transform.sign import unsign_moves


class TransformSignTestCase(unittest.TestCase):

    def test_unsign_moves(self) -> None:
        provide = parse_moves("R' F u' B r")
        expect = parse_moves("R' F Uw' B Rw")

        result = unsign_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_sign_moves(self) -> None:
        provide = parse_moves("R' F Uw' B Rw")
        expect = parse_moves("R' F u' B r")

        result = sign_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
