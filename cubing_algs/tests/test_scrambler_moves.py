"""Tests for scramble movesets."""
import unittest
from random import Random

from cubing_algs.scrambler.moves import build_cube_move_set
from cubing_algs.scrambler.moves import is_valid_next_move
from cubing_algs.scrambler.moves import random_moves


class TestValidNextMove(unittest.TestCase):
    """Tests for valid next move generation in scrambling."""

    def test_is_valid_next_move_valid(self) -> None:
        """Test that valid next moves are recognized."""
        self.assertTrue(is_valid_next_move('F', 'R'))
        self.assertTrue(is_valid_next_move("F'", 'R'))
        self.assertTrue(is_valid_next_move('F2', "R'"))

    def test_is_valid_next_move_invalid_same_face(self) -> None:
        """Test that moves on the same face are invalid."""
        self.assertFalse(is_valid_next_move('F', 'F'))
        self.assertFalse(is_valid_next_move('F', "F'"))
        self.assertFalse(is_valid_next_move('F2', 'F'))

    def test_is_valid_next_move_invalid_none(self) -> None:
        """Test that moves does not matche."""
        self.assertFalse(is_valid_next_move('', 'F'))
        self.assertFalse(is_valid_next_move('F', ''))
        self.assertFalse(is_valid_next_move('Z', 'F'))

    def test_is_valid_next_move_invalid_opposite_faces(self) -> None:
        """Test that moves on opposite faces are invalid."""
        self.assertFalse(is_valid_next_move('F', 'B'))
        self.assertFalse(is_valid_next_move('R', 'L'))
        self.assertFalse(is_valid_next_move('U', 'D'))

    def test_is_valid_next_move_with_modifiers(self) -> None:
        """Test that modifiers don't affect face validation."""
        self.assertFalse(is_valid_next_move('Fw', 'F'))
        self.assertFalse(is_valid_next_move('Fw', 'B'))


class TestCubeMoveSet(unittest.TestCase):  # noqa: PLR0904
    """Tests for cube move set definitions and validation."""

    maxDiff = None

    def test_build_cube_move_set_2x2x2(self) -> None:
        """Test build cube move set 2x2x2."""
        self.assertEqual(
            build_cube_move_set(2),
            [
                'R', "R'", 'R2',
                'F', "F'", 'F2',
                'U', "U'", 'U2',
                'L', "L'", 'L2',
                'B', "B'", 'B2',
                'D', "D'", 'D2',
            ],
        )

    def test_build_cube_move_set_2x2x2_inner_layers(self) -> None:
        """Test build cube move set 2x2x2 inner layers."""
        self.assertEqual(
            build_cube_move_set(2, inner_layers=True),
            [
                'R', "R'", 'R2',
                'F', "F'", 'F2',
                'U', "U'", 'U2',
                'L', "L'", 'L2',
                'B', "B'", 'B2',
                'D', "D'", 'D2',
            ],
        )

    def test_build_cube_move_set_3x3x3(self) -> None:
        """Test build cube move set 3x3x3."""
        self.assertEqual(
            build_cube_move_set(3),
            [
                'R', "R'", 'R2',
                'F', "F'", 'F2',
                'U', "U'", 'U2',
                'L', "L'", 'L2',
                'B', "B'", 'B2',
                'D', "D'", 'D2',
            ],
        )

    def test_build_cube_move_set_3x3x3_inner_layers(self) -> None:
        """Test build cube move set 3x3x3 inner layers."""
        self.assertEqual(
            build_cube_move_set(3, inner_layers=True),
            [
                'R', "R'", 'R2',
                'F', "F'", 'F2',
                'U', "U'", 'U2',
                'L', "L'", 'L2',
                'B', "B'", 'B2',
                'D', "D'", 'D2',
            ],
        )

    def test_build_cube_move_set_4x4x4(self) -> None:
        """Test build cube move set 4x4x4."""
        self.assertEqual(
            build_cube_move_set(4),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                'L', "L'", 'L2',
                'B', "B'", 'B2',
                'D', "D'", 'D2',
            ],
        )

    def test_build_cube_move_set_4x4x4_left_handed(self) -> None:
        """Test build cube move set 4x4x4 left handed."""
        self.assertEqual(
            build_cube_move_set(4, right_handed=False),
            [
                'R', "R'", 'R2',
                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                'B', "B'", 'B2',
                'D', "D'", 'D2',
            ],
        )

    def test_build_cube_move_set_4x4x4_inner_layers(self) -> None:
        """Test build cube move set 4x4x4 inner layers."""
        self.assertEqual(
            build_cube_move_set(4, inner_layers=True),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '2R', "2R'", '2R2',
                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '2F', "2F'", '2F2',
                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '2U', "2U'", '2U2',
                'L', "L'", 'L2',
                '2L', "2L'", '2L2',
                'B', "B'", 'B2',
                '2B', "2B'", '2B2',
                'D', "D'", 'D2',
                '2D', "2D'", '2D2',
            ],
        )

    def test_build_cube_move_set_4x4x4_inner_layers_left_handed(self) -> None:
        """Test build cube move set 4x4x4 inner layers left handed."""
        self.assertEqual(
            build_cube_move_set(4, inner_layers=True, right_handed=False),
            [
                'R', "R'", 'R2',
                '2R', "2R'", '2R2',
                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '2F', "2F'", '2F2',
                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '2U', "2U'", '2U2',
                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '2L', "2L'", '2L2',
                'B', "B'", 'B2',
                '2B', "2B'", '2B2',
                'D', "D'", 'D2',
                '2D', "2D'", '2D2',
            ],
        )

    def test_build_cube_move_set_5x5x5(self) -> None:
        """Test build cube move set 5x5x5."""
        self.assertEqual(
            build_cube_move_set(5),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
            ],
        )

    def test_build_cube_move_set_5x5x5_left_handed(self) -> None:
        """Test build cube move set 5x5x5 left handed."""
        self.assertEqual(
            build_cube_move_set(5, right_handed=False),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
            ],
        )

    def test_build_cube_move_set_5x5x5_inner_layers(self) -> None:
        """Test build cube move set 5x5x5 inner layers."""
        self.assertEqual(
            build_cube_move_set(5, inner_layers=True),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '2R', "2R'", '2R2', '3R', "3R'", '3R2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '2F', "2F'", '2F2', '3F', "3F'", '3F2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '2U', "2U'", '2U2', '3U', "3U'", '3U2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '2L', "2L'", '2L2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '2B', "2B'", '2B2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '2D', "2D'", '2D2',
            ],
        )

    def test_build_cube_move_set_5x5x5_inner_layers_left_handed(self) -> None:
        """Test build cube move set 5x5x5 inner layers left handed."""
        self.assertEqual(
            build_cube_move_set(5, inner_layers=True, right_handed=False),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '2R', "2R'", '2R2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '2F', "2F'", '2F2', '3F', "3F'", '3F2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '2U', "2U'", '2U2', '3U', "3U'", '3U2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '2L', "2L'", '2L2', '3L', "3L'", '3L2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '2B', "2B'", '2B2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '2D', "2D'", '2D2',
            ],
        )

    def test_build_cube_move_set_6x6x6(self) -> None:
        """Test build cube move set 6x6x6."""
        self.assertEqual(
            build_cube_move_set(6),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
            ],
        )

    def test_build_cube_move_set_6x6x6_inner_layers(self) -> None:
        """Test build cube move set 6x6x6 inner layers."""
        self.assertEqual(
            build_cube_move_set(6, inner_layers=True),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',
                '2R', "2R'", '2R2',
                '3R', "3R'", '3R2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',
                '2F', "2F'", '2F2',
                '3F', "3F'", '3F2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',
                '2U', "2U'", '2U2',
                '3U', "3U'", '3U2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '2L', "2L'", '2L2',
                '3L', "3L'", '3L2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '2B', "2B'", '2B2',
                '3B', "3B'", '3B2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '2D', "2D'", '2D2',
                '3D', "3D'", '3D2',
            ],
        )

    def test_build_cube_move_set_6x6x6_left_handed(self) -> None:
        """Test build cube move set 6x6x6 left handed."""
        self.assertEqual(
            build_cube_move_set(6, right_handed=False),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
            ],
        )

    def test_build_cube_move_set_6x6x6_inner_layers_left_handed(self) -> None:
        """Test build cube move set 6x6x6 inner layers left handed."""
        self.assertEqual(
            build_cube_move_set(6, inner_layers=True, right_handed=False),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '2R', "2R'", '2R2',
                '3R', "3R'", '3R2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',
                '2F', "2F'", '2F2',
                '3F', "3F'", '3F2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',
                '2U', "2U'", '2U2',
                '3U', "3U'", '3U2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',
                '2L', "2L'", '2L2',
                '3L', "3L'", '3L2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '2B', "2B'", '2B2',
                '3B', "3B'", '3B2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '2D', "2D'", '2D2',
                '3D', "3D'", '3D2',
            ],
        )

    def test_build_cube_move_set_7x7x7(self) -> None:
        """Test build cube move set 7x7x7."""
        self.assertEqual(
            build_cube_move_set(7),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '3Bw', "3Bw'", '3Bw2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '3Dw', "3Dw'", '3Dw2',
            ],
        )

    def test_build_cube_move_set_7x7x7_inner_layers(self) -> None:
        """Test build cube move set 7x7x7 inner layers."""
        self.assertEqual(
            build_cube_move_set(7, inner_layers=True),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',
                '2R', "2R'", '2R2',
                '3R', "3R'", '3R2',
                '4R', "4R'", '4R2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',
                '2F', "2F'", '2F2',
                '3F', "3F'", '3F2',
                '4F', "4F'", '4F2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',
                '2U', "2U'", '2U2',
                '3U', "3U'", '3U2',
                '4U', "4U'", '4U2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',
                '2L', "2L'", '2L2',
                '3L', "3L'", '3L2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '3Bw', "3Bw'", '3Bw2',
                '2B', "2B'", '2B2',
                '3B', "3B'", '3B2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '3Dw', "3Dw'", '3Dw2',
                '2D', "2D'", '2D2',
                '3D', "3D'", '3D2',
            ],
        )

    def test_build_cube_move_set_8x8x8(self) -> None:
        """Test build cube move set 8x8x8."""
        self.assertEqual(
            build_cube_move_set(8),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',
                '4Rw', "4Rw'", '4Rw2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',
                '4Fw', "4Fw'", '4Fw2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',
                '4Uw', "4Uw'", '4Uw2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '3Bw', "3Bw'", '3Bw2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '3Dw', "3Dw'", '3Dw2',
            ],
        )

    def test_build_cube_move_set_8x8x8_inner_layers(self) -> None:
        """Test build cube move set 8x8x8 inner layers."""
        self.assertEqual(
            build_cube_move_set(8, inner_layers=True),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',
                '4Rw', "4Rw'", '4Rw2',
                '2R', "2R'", '2R2',
                '3R', "3R'", '3R2',
                '4R', "4R'", '4R2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',
                '4Fw', "4Fw'", '4Fw2',
                '2F', "2F'", '2F2',
                '3F', "3F'", '3F2',
                '4F', "4F'", '4F2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',
                '4Uw', "4Uw'", '4Uw2',
                '2U', "2U'", '2U2',
                '3U', "3U'", '3U2',
                '4U', "4U'", '4U2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',
                '2L', "2L'", '2L2',
                '3L', "3L'", '3L2',
                '4L', "4L'", '4L2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '3Bw', "3Bw'", '3Bw2',
                '2B', "2B'", '2B2',
                '3B', "3B'", '3B2',
                '4B', "4B'", '4B2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '3Dw', "3Dw'", '3Dw2',
                '2D', "2D'", '2D2',
                '3D', "3D'", '3D2',
                '4D', "4D'", '4D2',
            ],
        )

    def test_build_cube_move_set_9x9x9(self) -> None:
        """Test build cube move set 9x9x9."""
        self.assertEqual(
            build_cube_move_set(9),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',
                '4Rw', "4Rw'", '4Rw2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',
                '4Fw', "4Fw'", '4Fw2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',
                '4Uw', "4Uw'", '4Uw2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',
                '4Lw', "4Lw'", '4Lw2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '3Bw', "3Bw'", '3Bw2',
                '4Bw', "4Bw'", '4Bw2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '3Dw', "3Dw'", '3Dw2',
                '4Dw', "4Dw'", '4Dw2',
            ],
        )

    def test_build_cube_move_set_9x9x9_inner_layers(self) -> None:
        """Test build cube move set 9x9x9 inner layers."""
        self.assertEqual(
            build_cube_move_set(9, inner_layers=True),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',
                '4Rw', "4Rw'", '4Rw2',
                '2R', "2R'", '2R2',
                '3R', "3R'", '3R2',
                '4R', "4R'", '4R2',
                '5R', "5R'", '5R2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',
                '4Fw', "4Fw'", '4Fw2',
                '2F', "2F'", '2F2',
                '3F', "3F'", '3F2',
                '4F', "4F'", '4F2',
                '5F', "5F'", '5F2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',
                '4Uw', "4Uw'", '4Uw2',
                '2U', "2U'", '2U2',
                '3U', "3U'", '3U2',
                '4U', "4U'", '4U2',
                '5U', "5U'", '5U2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                '3Lw', "3Lw'", '3Lw2',
                '4Lw', "4Lw'", '4Lw2',
                '2L', "2L'", '2L2',
                '3L', "3L'", '3L2',
                '4L', "4L'", '4L2',

                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                '3Bw', "3Bw'", '3Bw2',
                '4Bw', "4Bw'", '4Bw2',
                '2B', "2B'", '2B2',
                '3B', "3B'", '3B2',
                '4B', "4B'", '4B2',

                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
                '3Dw', "3Dw'", '3Dw2',
                '4Dw', "4Dw'", '4Dw2',
                '2D', "2D'", '2D2',
                '3D', "3D'", '3D2',
                '4D', "4D'", '4D2',
            ],
        )

    def test_build_big_cube_move_set_no_options(self) -> None:
        """Test build big cube move set no options."""
        self.assertEqual(
            build_cube_move_set(6),
            [
                'R', "R'", 'R2', 'Rw', "Rw'", 'Rw2',
                '3Rw', "3Rw'", '3Rw2',

                'F', "F'", 'F2', 'Fw', "Fw'", 'Fw2',
                '3Fw', "3Fw'", '3Fw2',

                'U', "U'", 'U2', 'Uw', "Uw'", 'Uw2',
                '3Uw', "3Uw'", '3Uw2',

                'L', "L'", 'L2', 'Lw', "Lw'", 'Lw2',
                'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2',
                'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2',
            ],
        )


class TestRandomMoves(unittest.TestCase):
    """Tests for random move sequence generation."""

    def test_random_moves_2x2x2(self) -> None:
        """Test random moves 2x2x2."""
        moves = random_moves(2, ['F', 'R', 'U'], 0)

        self.assertGreaterEqual(
            len(moves), 9,
        )

        self.assertLessEqual(
            len(moves), 11,
        )

    def test_random_moves_2x2x2_iterations(self) -> None:
        """Test random moves 2x2x2 iterations."""
        moves = random_moves(2, ['F', 'R', 'U'], 5)

        self.assertEqual(
            len(moves), 5,
        )

    def test_random_moves_50x50x50(self) -> None:
        """Test random moves 50x50x50."""
        moves = random_moves(50, ['F', 'R', 'U'])

        self.assertEqual(
            len(moves), 100,
        )


class TestRNGParameter(unittest.TestCase):
    """Tests for random number generator parameter functionality."""

    def test_random_moves_deterministic_with_seed(self) -> None:
        """Test random_moves produces identical results with same seed."""
        move_set = ['R', 'U', 'F', "R'", "U'", "F'", 'R2', 'U2', 'F2']
        iterations = 10

        rng1 = Random(42)  # noqa: S311
        rng2 = Random(42)  # noqa: S311

        result1 = random_moves(3, move_set, iterations, rng1)
        result2 = random_moves(3, move_set, iterations, rng2)

        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed should produce identical scrambles',
        )

    def test_random_moves_different_seeds_produce_different_results(
            self) -> None:
        """Test random_moves produces different results with different seeds."""
        move_set = ['R', 'U', 'F', "R'", "U'", "F'", 'R2', 'U2', 'F2']
        iterations = 10

        rng1 = Random(42)  # noqa: S311
        rng2 = Random(123)  # noqa: S311

        result1 = random_moves(3, move_set, iterations, rng1)
        result2 = random_moves(3, move_set, iterations, rng2)

        self.assertNotEqual(
            str(result1),
            str(result2),
            'Different seeds should produce different scrambles',
        )

    def test_random_moves_uses_default_rng_when_none(self) -> None:
        """Test that random_moves works without explicit rng parameter."""
        move_set = ['R', 'U', 'F']
        iterations = 5

        result = random_moves(3, move_set, iterations)

        self.assertEqual(
            len(result),
            iterations,
            'Should generate correct number of moves with default RNG',
        )

    def test_random_moves_automatic_iterations_with_seeded_rng(self) -> None:
        """Test random_moves with automatic iterations using seeded RNG."""
        move_set = ['R', 'U', 'F', "R'", "U'", "F'", 'R2', 'U2', 'F2']

        rng1 = Random(42)  # noqa: S311
        rng2 = Random(42)  # noqa: S311

        result1 = random_moves(3, move_set, 0, rng1)
        result2 = random_moves(3, move_set, 0, rng2)

        self.assertEqual(
            len(result1),
            len(result2),
            'Same seed should produce same length with automatic iterations',
        )
        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed should produce identical scrambles',
        )
