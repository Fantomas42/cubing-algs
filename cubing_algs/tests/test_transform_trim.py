"""Tests for move trimming transformation functions."""
import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.trim import trim_moves


class TransformTrimTestCase(unittest.TestCase):
    """Tests for trimming moves from algorithm start and end."""

    def test_trim(self) -> None:
        """Test trim."""
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
        """Test trim multiple."""
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
        """Test trim multiple paused."""
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
        """Test trim start."""
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
        """Test trim end."""
        provide = parse_moves('U F R B U')
        expect = parse_moves('U F R B')

        result = trim_moves('U', start=False)(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_trim_pause_without_target_move(self) -> None:
        """Pauses are not trimmed when the target move is absent."""
        provide = parse_moves('. F R B')
        expect = parse_moves('. F R B')

        result = trim_moves('y')(provide)

        self.assertEqual(result, expect)

    def test_trim_pause_only_after_target(self) -> None:
        """Pauses are trimmed only when adjacent to a trimmed target move."""
        provide = parse_moves('y . F R B . y')
        expect = parse_moves('F R B')

        result = trim_moves('y')(provide)

        self.assertEqual(result, expect)

    def test_trim_pause_only_after_complex_target(self) -> None:
        """Pauses trimmed with target move, complex case."""
        provide = parse_moves('y . y . F R B . . y')
        expect = parse_moves('F R B')

        result = trim_moves('y')(provide)

        self.assertEqual(result, expect)

    def test_trim_pause_only_after_complex_target_trailing_pause(self) -> None:
        """Pauses trimmed with target move, trailing pause."""
        provide = parse_moves('. y . y . F R B . . y .')
        expect = parse_moves('F R B')

        result = trim_moves('y')(provide)

        self.assertEqual(result, expect)

    def test_trim_target_not_present(self) -> None:
        """Algorithm is returned unchanged when trim target is absent."""
        provide = parse_moves('F R B')
        expect = parse_moves('F R B')

        result = trim_moves('y')(provide)

        self.assertEqual(result, expect)

    def test_trim_all_moves(self) -> None:
        """Algorithm of entirely trimmed moves returns empty."""
        provide = parse_moves("U U' U2")

        result = trim_moves('U')(provide)

        self.assertEqual(result, parse_moves(''))

    def test_trim_empty(self) -> None:
        """Test trim empty."""
        provide = parse_moves('')

        result = trim_moves('U', start=False)(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
