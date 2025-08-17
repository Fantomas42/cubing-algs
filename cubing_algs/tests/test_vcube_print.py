import os
import unittest
from unittest.mock import patch

from cubing_algs.vcube import VCube
from cubing_algs.vcube_print import DEFAULT_COLORS
from cubing_algs.vcube_print import TERM_COLORS
from cubing_algs.vcube_print import VCubePrinter


class TestVCubePrinter(unittest.TestCase):

    def setUp(self):
        self.cube = VCube()
        self.printer = VCubePrinter(self.cube)

    def test_init_default_parameters(self):
        printer = VCubePrinter(self.cube)

        self.assertEqual(printer.cube, self.cube)
        self.assertEqual(printer.cube_size, 3)
        self.assertEqual(printer.face_size, 9)
        self.assertEqual(printer.orientation, '')
        self.assertEqual(printer.colors, DEFAULT_COLORS)

        expected_face_colors = {
            'U': 'white',
            'R': 'red',
            'F': 'green',
            'D': 'yellow',
            'L': 'orange',
            'B': 'blue',
        }
        self.assertEqual(printer.face_colors, expected_face_colors)

    def test_init_custom_parameters(self):
        custom_colors = ['black', 'purple', 'cyan', 'magenta', 'pink', 'grey']
        custom_orientation = "R U R'"

        printer = VCubePrinter(
            self.cube,
            orientation=custom_orientation,
            colors=custom_colors,
        )

        self.assertEqual(printer.orientation, custom_orientation)
        self.assertEqual(printer.colors, custom_colors)
        self.assertEqual(printer.face_colors['U'], 'black')
        self.assertEqual(printer.face_colors['R'], 'purple')

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_format_color_with_colors(self):
        with patch('cubing_algs.vcube_print.USE_COLORS', True):  # noqa FBT003
            printer = VCubePrinter(self.cube)
            result = printer.format_color('U')
            expected = f"{ TERM_COLORS['white'] } U { TERM_COLORS['reset'] }"
            self.assertEqual(result, expected)

    @patch.dict(os.environ, {'TERM': 'other'})
    def test_format_color_without_colors(self):
        with patch('cubing_algs.vcube_print.USE_COLORS', False):  # noqa FBT003
            printer = VCubePrinter(self.cube)
            result = printer.format_color('U')
            self.assertEqual(result, ' U ')

    def test_print_top_down_face(self):
        printer = VCubePrinter(self.cube)
        face = 'UUUUUUUUU'

        result = printer.print_top_down_face(face)
        lines = result.split('\n')

        self.assertEqual(len(lines), 4)

        for i in range(3):
            line = lines[i]
            self.assertTrue(line.startswith('         '))
            self.assertEqual(line.count('U'), 3)

    def test_print_cube_without_orientation(self):
        printer = VCubePrinter(self.cube)

        result = printer.print_cube()

        lines = result.split('\n')

        self.assertEqual(len(lines), 10)

        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    def test_print_cube_with_orientation(self):
        orientation = 'z2'
        printer = VCubePrinter(self.cube, orientation=orientation)

        initial_state = self.cube.state

        result = printer.print_cube()
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        self.assertEqual(len(lines), 10)

    def test_print_cube_structure(self):
        printer = VCubePrinter(self.cube)
        result = printer.print_cube()

        lines = [line for line in result.split('\n') if line.strip()]

        self.assertEqual(len(lines), 9)

        middle_lines = lines[3:6]
        top_lines = lines[0:3]

        for middle_line in middle_lines:
            for top_line in top_lines:
                self.assertGreater(len(middle_line), len(top_line))

    def test_print_cube_face_order(self):
        cube = VCube()
        printer = VCubePrinter(cube)

        result = printer.print_cube()
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
