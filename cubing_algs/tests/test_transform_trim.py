"""Tests for move trimming transformation functions."""

import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.trim import trim_moves


class TransformTrimTestCase(unittest.TestCase):
    """Tests for trimming moves from algorithm start and end."""

    def test_trim(self) -> None:
        provide = parse_moves('U F R B U')
        expect = parse_moves('F R B')

        result = trim_moves('U')(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_trim_multiple(self) -> None:
        provide = parse_moves("U U' F R B U2")
        expect = parse_moves('F R B')

        result = trim_moves('U')(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_trim_multiple_paused(self) -> None:
        provide = parse_moves("U' . U2 F R B U . . U'")
        expect = parse_moves('F R B')

        result = trim_moves('U')(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_trim_start(self) -> None:
        provide = parse_moves('U F R B U')
        expect = parse_moves('F R B U')

        result = trim_moves('U', end=False)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_trim_end(self) -> None:
        provide = parse_moves('U F R B U')
        expect = parse_moves('U F R B')

        result = trim_moves('U', start=False)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_trim_empty(self) -> None:
        provide = parse_moves('')

        result = trim_moves('U', start=False)(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
