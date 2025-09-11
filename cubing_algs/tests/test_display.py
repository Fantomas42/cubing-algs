import os
import unittest
from unittest.mock import patch

from cubing_algs.display import TERM_COLORS
from cubing_algs.display import VCubeDisplay
from cubing_algs.vcube import VCube


class TestVCubeDisplay(unittest.TestCase):

    def setUp(self):
        self.cube = VCube()
        self.printer = VCubeDisplay(self.cube)

    def test_init_default_parameters(self):
        printer = VCubeDisplay(self.cube)

        self.assertEqual(printer.cube, self.cube)
        self.assertEqual(printer.cube_size, 3)
        self.assertEqual(printer.face_size, 9)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_with_colors(self):
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('U')
            expected = f"{ TERM_COLORS['white'] } U { TERM_COLORS['reset'] }"
            self.assertEqual(result, expected)

    @patch.dict(os.environ, {'TERM': 'other'})
    def test_display_facelet_without_colors(self):
        with patch('cubing_algs.display.USE_COLORS', False):  # noqa FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('U')
            self.assertEqual(result, ' U ')

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_hidden(self):
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('U', '0')
            expected = (
                f"{ TERM_COLORS['white_hidden'] } U { TERM_COLORS['reset'] }"
            )
            self.assertEqual(result, expected)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_invalid(self):
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('X')  # Facelet invalide
            expected = f"{ TERM_COLORS['masked'] } X { TERM_COLORS['reset'] }"
            self.assertEqual(result, expected)

    def test_display_top_down_face(self):
        printer = VCubeDisplay(self.cube)
        face = 'UUUUUUUUU'

        result = printer.display_top_down_face(face, '111111111')
        lines = result.split('\n')

        self.assertEqual(len(lines), 4)

        for i in range(3):
            line = lines[i]
            self.assertTrue(line.startswith('         '))
            self.assertEqual(line.count('U'), 3)

    def test_display_without_orientation(self):
        printer = VCubeDisplay(self.cube)

        result = printer.display()

        lines = result.split('\n')

        self.assertEqual(len(lines), 10)

        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    def test_display_with_orientation(self):
        printer = VCubeDisplay(self.cube)

        initial_state = self.cube.state

        result = printer.display(orientation='DF')
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        self.assertEqual(len(lines), 10)

    def test_display_oll(self):
        self.cube.rotate("z2 F U F' R' F R U' R' F' R z2")

        printer = VCubeDisplay(self.cube)
        initial_state = self.cube.state

        result = printer.display(mode='oll')
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        self.assertEqual(len(lines), 6)

    def test_display_pll(self):
        self.cube.rotate("z2 L2 U' L2 D F2 R2 U R2 D' F2 z2")

        printer = VCubeDisplay(self.cube)
        initial_state = self.cube.state

        result = printer.display(mode='pll')
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        self.assertEqual(len(lines), 6)

    def test_display_f2l(self):
        self.cube.rotate("z2 R U R' U' z2")

        printer = VCubeDisplay(self.cube)

        result = printer.display(mode='f2l')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_af2l(self):
        self.cube.rotate("z2 B' U' B F U F' U2")

        printer = VCubeDisplay(self.cube)

        result = printer.display(mode='af2l')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_f2l_initial_no_reorientation(self):
        printer = VCubeDisplay(self.cube)

        result = printer.display(mode='f2l', orientation='UF')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_cross(self):
        self.cube.rotate('B L F L F R F L B R')

        printer = VCubeDisplay(self.cube)

        result = printer.display(mode='cross')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_structure(self):
        printer = VCubeDisplay(self.cube)
        result = printer.display()

        lines = [line for line in result.split('\n') if line.strip()]

        self.assertEqual(len(lines), 9)

        middle_lines = lines[3:6]
        top_lines = lines[0:3]

        for middle_line in middle_lines:
            for top_line in top_lines:
                self.assertGreater(len(middle_line), len(top_line))

    def test_display_face_order(self):
        cube = VCube()
        printer = VCubeDisplay(cube)

        result = printer.display()
        lines = result.split('\n')

        top_section = ''.join(lines[0:3])
        self.assertIn('U', top_section)
        self.assertNotIn('D', top_section)

        bottom_section = ''.join(lines[6:9])
        self.assertIn('D', bottom_section)
        self.assertNotIn('U', bottom_section)

        middle_section = ''.join(lines[3:6])
        for face in ['L', 'F', 'R', 'B']:
            self.assertIn(face, middle_section)

    def test_split_faces(self):
        printer = VCubeDisplay(self.cube)

        self.assertEqual(
            printer.split_faces(self.cube.state),
            [
                'UUUUUUUUU',
                'RRRRRRRRR',
                'FFFFFFFFF',
                'DDDDDDDDD',
                'LLLLLLLLL',
                'BBBBBBBBB',
            ],
        )

    def test_compute_mask(self):
        printer = VCubeDisplay(self.cube)
        base_mask = (
            '000000000'
            '111111111'
            '111111111'
            '000000000'
            '111111111'
            '111111111'
        )

        self.assertEqual(
            printer.compute_mask(
                self.cube,
                base_mask,
            ),
            base_mask,
        )

    def test_compute_mask_moves(self):
        self.cube.rotate('R U F')

        printer = VCubeDisplay(self.cube)
        base_mask = (
            '000000000'
            '111111111'
            '111111111'
            '000000000'
            '111111111'
            '111111111'
        )

        self.assertEqual(
            printer.compute_mask(
                self.cube,
                base_mask,
            ),
            '000000110'
            '111111111'
            '111111001'
            '110001001'
            '110110111'
            '111011011',
        )

    def test_compute_no_mask(self):
        printer = VCubeDisplay(self.cube)

        self.assertEqual(
            printer.compute_mask(self.cube, ''),
            54 * '1',
        )

    def test_compute_f2l_front_face(self):
        cube = VCube()
        cube.rotate("z2 R U R' U' z2")

        printer = VCubeDisplay(cube)

        self.assertEqual(
            printer.compute_f2l_front_face(),
            'F',
        )

        cube = VCube()
        cube.rotate("y2 z2 R U R' U' z2")

        printer = VCubeDisplay(cube)

        self.assertEqual(
            printer.compute_f2l_front_face(),
            'B',
        )
