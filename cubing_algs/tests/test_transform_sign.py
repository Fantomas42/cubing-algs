"""Tests for SiGN notation transformation functions."""
import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.sign import sign_moves
from cubing_algs.transform.sign import unsign_moves


class TransformSignTestCase(unittest.TestCase):
    """Tests for SiGN notation transformations."""

    def test_unsign_moves(self) -> None:
        """Test unsign moves."""
        provide = parse_moves("R' F u' B r")
        expect = parse_moves("R' F Uw' B Rw")

        result = unsign_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unsign_layered_wide_moves(self) -> None:
        """Test unsign moves with layered wide moves like 3r -> 3Rw."""
        provide = parse_moves("3r 3u' R")
        expect = parse_moves("3Rw 3Uw' R")

        result = unsign_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_unsign_already_standard(self) -> None:
        """Test unsign on already-standard notation is idempotent."""
        provide = parse_moves("R' Uw 3Rw2 F")

        result = unsign_moves(provide)

        self.assertEqual(result, provide)

    def test_sign_moves(self) -> None:
        """Test sign moves."""
        provide = parse_moves("R' F Uw' B Rw")
        expect = parse_moves("R' F u' B r")

        result = sign_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_sign_layered_wide_moves(self) -> None:
        """Test sign moves with layered wide moves like 3Rw -> 3r."""
        provide = parse_moves("3Rw 3Uw' R")
        expect = parse_moves("3r 3u' R")

        result = sign_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

    def test_sign_already_sign(self) -> None:
        """Test sign on already-SiGN notation is idempotent."""
        provide = parse_moves("R' u 3r2 F")

        result = sign_moves(provide)

        self.assertEqual(result, provide)

    def test_sign_timed_moves(self) -> None:
        """Test sign preserves timing on wide moves."""
        provide = parse_moves("Rw@1 Uw'@2 R@3")
        expect = parse_moves("r@1 u'@2 R@3")

        result = sign_moves(provide)

        self.assertEqual(result, expect)

    def test_unsign_timed_moves(self) -> None:
        """Test unsign preserves timing on wide moves."""
        provide = parse_moves("r@1 u'@2 R@3")
        expect = parse_moves("Rw@1 Uw'@2 R@3")

        result = unsign_moves(provide)

        self.assertEqual(result, expect)

    def test_sign_pauses(self) -> None:
        """Test sign passes pauses through unchanged."""
        provide = parse_moves("Rw . Uw'")
        expect = parse_moves("r . u'")

        result = sign_moves(provide)

        self.assertEqual(result, expect)

    def test_unsign_pauses(self) -> None:
        """Test unsign passes pauses through unchanged."""
        provide = parse_moves("r . u'")
        expect = parse_moves("Rw . Uw'")

        result = unsign_moves(provide)

        self.assertEqual(result, expect)

    def test_sign_timed_pauses(self) -> None:
        """Test sign passes timed pauses through unchanged."""
        provide = parse_moves("Rw@1 .@2 Uw'@3")
        expect = parse_moves("r@1 .@2 u'@3")

        result = sign_moves(provide)

        self.assertEqual(result, expect)

    def test_unsign_timed_pauses(self) -> None:
        """Test unsign passes timed pauses through unchanged."""
        provide = parse_moves("r@1 .@2 u'@3")
        expect = parse_moves("Rw@1 .@2 Uw'@3")

        result = unsign_moves(provide)

        self.assertEqual(result, expect)
