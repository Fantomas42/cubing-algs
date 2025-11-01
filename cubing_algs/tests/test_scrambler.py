"""Tests for scramble generation."""

import time
import unittest
from collections import Counter
from statistics import mean
from statistics import stdev

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.scrambler import build_cube_move_set
from cubing_algs.scrambler import is_valid_next_move
from cubing_algs.scrambler import random_moves
from cubing_algs.scrambler import scramble
from cubing_algs.scrambler import scramble_easy_cross
from cubing_algs.vcube import VCube


class TestValidNextMove(unittest.TestCase):

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
    maxDiff = None

    def test_build_cube_move_set_2x2x2(self) -> None:
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

    def test_random_moves_2x2x2(self) -> None:
        moves = random_moves(2, ['F', 'R', 'U'], 0)

        self.assertGreaterEqual(
            len(moves), 9,
        )

        self.assertLessEqual(
            len(moves), 11,
        )

    def test_random_moves_2x2x2_iterations(self) -> None:
        moves = random_moves(2, ['F', 'R', 'U'], 5)

        self.assertEqual(
            len(moves), 5,
        )

    def test_random_moves_50x50x50(self) -> None:
        moves = random_moves(50, ['F', 'R', 'U'])

        self.assertEqual(
            len(moves), 100,
        )


class TestScramble(unittest.TestCase):

    def test_scramble_3x3x3(self) -> None:
        moves = scramble(3)

        self.assertGreaterEqual(
            len(moves), 25,
        )

        self.assertLessEqual(
            len(moves), 30,
        )

    def test_scramble_3x3x3_iterations(self) -> None:
        moves = scramble(3, 5)

        self.assertEqual(
            len(moves), 5,
        )


class TestScrambleEasyCross(unittest.TestCase):

    def test_scramble_easy_cross(self) -> None:
        moves = scramble_easy_cross()

        self.assertEqual(
            len(moves), 10,
        )
        self.assertTrue(
            'U' not in moves,
        )
        self.assertTrue(
            'D' not in moves,
        )


class TestScrambleEffectivenessByLength(unittest.TestCase):
    """
    Test suite measuring scramble effectiveness across different lengths.

    Tests randomness, state space coverage, consistency, and performance
    characteristics of scrambles at various lengths.
    """

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.test_lengths = [5, 10, 15, 20, 25, 30, 50]
        self.sample_size = 100  # Number of scrambles to test per length
        self.small_sample_size = 20  # For performance tests

    @staticmethod
    def get_face_from_move(move: str) -> str:
        """Extract the face character from a move string."""
        for face in FACE_ORDER:
            if move.startswith((face, face.lower())):
                return face
        return ''

    @staticmethod
    def calculate_move_distribution(algorithm: Algorithm) -> dict[
            str, float]:
        """Calculate the distribution of face moves in an algorithm."""
        face_counts: Counter[str] = Counter()
        total_moves = len(algorithm)

        for move in algorithm:
            face = TestScrambleEffectivenessByLength.get_face_from_move(
                str(move),
            )
            if face:
                face_counts[face] += 1

        # Convert to percentages
        return {
            face: (count / total_moves) * 100
            for face, count in face_counts.items()
        }

    @staticmethod
    def calculate_state_scrambledness(algorithm: Algorithm) -> float:
        """
        Calculate how scrambled a cube becomes after applying an algorithm.

        Returns a value between 0.0 (solved) and 1.0 (maximally scrambled).
        """
        # Count how many facelets are not in their original position
        cube = VCube()
        solved_state = cube.state
        cube.rotate(algorithm)
        scrambled_state = cube.state

        different_facelets = sum(
            1
            for i, j in zip(solved_state, scrambled_state, strict=False)
            if i != j
        )

        # Normalize by total number of facelets (54 for a 3x3x3 cube)
        return different_facelets / 54.0

    @staticmethod
    def has_consecutive_same_or_opposite_faces(algorithm: Algorithm) -> bool:
        """
        Check if algorithm has consecutive moves on same
        or opposite faces.
        """
        moves = [str(move) for move in algorithm]

        for i in range(len(moves) - 1):
            current_face = TestScrambleEffectivenessByLength.get_face_from_move(
                moves[i],
            )
            next_face = TestScrambleEffectivenessByLength.get_face_from_move(
                moves[i + 1],
            )

            if current_face and next_face:
                # Check same face
                if current_face == next_face:
                    return True
                # Check opposite faces
                if OPPOSITE_FACES.get(current_face) == next_face:
                    return True

        return False

    def test_scramble_length_consistency(self) -> None:
        """Test that scrambles generate the requested length consistently."""
        for length in self.test_lengths:
            with self.subTest(length=length):
                for _ in range(10):  # Test multiple samples
                    scramble_alg = scramble(3, length)
                    self.assertEqual(
                        len(scramble_alg), length,
                        f'Scramble should be exactly {length} moves',
                    )

    def test_move_distribution_randomness(self) -> None:
        """Test that move distributions approach uniform across face types."""
        for length in [15, 25, 50]:  # Test representative lengths
            with self.subTest(length=length):
                all_distributions = []

                for _ in range(self.sample_size):
                    scramble_alg = scramble(3, length)
                    distribution = self.calculate_move_distribution(
                        scramble_alg,
                    )
                    all_distributions.append(distribution)

                # Calculate average distribution across all scrambles
                face_averages = {}
                for face in FACE_ORDER:
                    face_percentages = [
                        d.get(face, 0) for d in all_distributions
                    ]
                    face_averages[face] = mean(face_percentages)

                # For longer scrambles, distribution should be more uniform
                if length >= 25:
                    # Each face should appear roughly 16.67% of the time (1/6)
                    expected_percentage = 100.0 / 6
                    tolerance = 5.0  # Allow 5% deviation

                    for face, avg_percentage in face_averages.items():
                        self.assertGreater(
                            avg_percentage,
                            expected_percentage - tolerance,
                            f'Face {face} appears too rarely: '
                            f'{avg_percentage:.1f}%',
                        )
                        self.assertLess(
                            avg_percentage, expected_percentage + tolerance,
                            f'Face {face} appears too frequently: '
                            f'{avg_percentage:.1f}%',
                        )

    def test_state_space_coverage_by_length(self) -> None:
        """Test that longer scrambles achieve better state space coverage."""
        scrambledness_by_length = {}

        for length in self.test_lengths:
            scrambledness_values = []

            for _ in range(self.sample_size):
                scramble_alg = scramble(3, length)
                scrambledness = self.calculate_state_scrambledness(scramble_alg)
                scrambledness_values.append(scrambledness)

            avg_scrambledness = mean(scrambledness_values)
            scrambledness_by_length[length] = avg_scrambledness

        # Test that scrambledness generally increases with length
        lengths = sorted(scrambledness_by_length.keys())
        for i in range(len(lengths) - 1):
            current_length = lengths[i]
            next_length = lengths[i + 1]

            current_scrambledness = scrambledness_by_length[current_length]
            next_scrambledness = scrambledness_by_length[next_length]

            # Allow some variance, but general trend should be increasing
            self.assertGreaterEqual(
                next_scrambledness,
                current_scrambledness - 0.05,
                f'Scrambledness should increase with length: '
                f'{current_length}({current_scrambledness:.3f}) vs '
                f'{next_length}({next_scrambledness:.3f})',
            )

    def test_no_consecutive_invalid_moves(self) -> None:
        """Test that scrambles never contain consecutive invalid moves."""
        for length in self.test_lengths:
            with self.subTest(length=length):
                for _ in range(self.sample_size):
                    scramble_alg = scramble(3, length)
                    self.assertFalse(
                        self.has_consecutive_same_or_opposite_faces(scramble_alg),
                        f'Scramble of length {length} contains '
                        'consecutive invalid moves',
                    )

    def test_scramble_uniqueness(self) -> None:
        """Test that repeated scramble calls produce different results."""
        for length in [15, 25]:
            with self.subTest(length=length):
                scrambles = set()

                for _ in range(50):  # Generate 50 scrambles
                    scramble_alg = scramble(3, length)
                    scrambles.add(str(scramble_alg))

                # Should have high uniqueness (at least 90% unique)
                uniqueness_ratio = len(scrambles) / 50
                self.assertGreater(
                    uniqueness_ratio, 0.9,
                    f'Scrambles of length {length} not unique enough: '
                    f'{uniqueness_ratio:.2f}',
                )

    def test_very_short_scrambles(self) -> None:
        """Test edge cases with very short scrambles (1-5 moves)."""
        for length in range(1, 6):
            with self.subTest(length=length):
                scramble_alg = scramble(3, length)

                # Should generate exactly the requested length
                self.assertEqual(len(scramble_alg), length)

                # Should not have invalid consecutive moves
                self.assertFalse(
                    self.has_consecutive_same_or_opposite_faces(scramble_alg),
                )

                # Should produce some scrambling effect
                if length >= 3:
                    scrambledness = self.calculate_state_scrambledness(
                        scramble_alg,
                    )
                    self.assertGreater(
                        scrambledness, 0.0,
                        'Even short scrambles should change cube state',
                    )

    def test_very_long_scrambles(self) -> None:
        """Test edge cases with very long scrambles (50+ moves)."""
        long_lengths = [50, 75, 100]

        for length in long_lengths:
            with self.subTest(length=length):
                scramble_alg = scramble(3, length)

                # Should generate exactly the requested length
                self.assertEqual(len(scramble_alg), length)

                # Should not have invalid consecutive moves
                self.assertFalse(
                    self.has_consecutive_same_or_opposite_faces(scramble_alg),
                )

                # Should achieve high scrambledness
                scrambledness = self.calculate_state_scrambledness(scramble_alg)
                self.assertGreater(
                    scrambledness, 0.6,
                    'Long scrambles should achieve '
                    f'high scrambledness: {scrambledness:.3f}',
                )

    def test_scramble_performance_by_length(self) -> None:
        """Test performance characteristics of scramble generation."""
        performance_results = {}

        for length in [10, 25, 50, 100]:
            start_time = time.time()

            for _ in range(self.small_sample_size):
                scramble(3, length)

            end_time = time.time()
            avg_time_per_scramble = (
                (end_time - start_time) / self.small_sample_size
            )
            performance_results[length] = avg_time_per_scramble

        # Performance should scale reasonably with length
        for length, avg_time in performance_results.items():
            # Should generate scrambles quickly (under 10ms each)
            self.assertLess(
                avg_time, 0.01,
                'Scramble generation too slow '
                f'for length {length}: {avg_time:.4f}s',
            )

    def test_scramble_consistency_across_runs(self) -> None:
        """
        Test that scramble quality metrics are consistent
        across multiple runs.
        """
        length = 25  # Test with a representative length

        run_scrambledness = []
        run_uniqueness = []

        # Run multiple test batches
        for _ in range(5):
            batch_scrambledness = []
            batch_scrambles = set()

            for _ in range(20):
                scramble_alg = scramble(3, length)
                batch_scrambledness.append(
                    self.calculate_state_scrambledness(scramble_alg),
                )
                batch_scrambles.add(str(scramble_alg))

            run_scrambledness.append(mean(batch_scrambledness))
            run_uniqueness.append(len(batch_scrambles) / 20)

        # Consistency check: standard deviation should be reasonably low
        scrambledness_stdev = stdev(run_scrambledness)
        uniqueness_stdev = stdev(run_uniqueness)

        self.assertLess(
            scrambledness_stdev, 0.05,
            'Scrambledness too inconsistent across runs: '
            f'{scrambledness_stdev:.4f}')
        self.assertLess(
            uniqueness_stdev, 0.1,
            'Uniqueness too inconsistent across runs: '
            f'{uniqueness_stdev:.4f}')

    def test_move_type_distribution(self) -> None:
        """
        Test that different move types (normal, prime, double)
        are well distributed.
        """
        length = 30

        move_type_counts = {'normal': 0, 'prime': 0, 'double': 0}
        total_moves = 0

        for _ in range(self.sample_size):
            scramble_alg = scramble(3, length)

            for move in scramble_alg:
                total_moves += 1

                if move.is_counter_clockwise:
                    move_type_counts['prime'] += 1
                elif move.is_double:
                    move_type_counts['double'] += 1
                else:
                    move_type_counts['normal'] += 1

        # Convert to percentages
        move_type_percentages = {}
        for move_type, count in move_type_counts.items():
            move_type_percentages[move_type] = (count / total_moves) * 100

        # Each move type should appear roughly equally (around 33% each)
        expected_percentage = 100.0 / 3
        tolerance = 8.0  # Allow 8% deviation

        for move_type, percentage in move_type_percentages.items():
            self.assertGreater(
                percentage, expected_percentage - tolerance,
                f'Move type {move_type} appears too rarely: {percentage:.1f}%',
            )
            self.assertLess(
                percentage, expected_percentage + tolerance,
                f'Move type {move_type} appears '
                f'too frequently: {percentage:.1f}%',
            )
