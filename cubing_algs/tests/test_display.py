import os
import unittest
from unittest.mock import patch

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
            expected = 'm U \x1b[0;0m'
            self.assertIn(expected, result)

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
            expected = 'm U \x1b[0;0m'
            self.assertIn(expected, result)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_invalid(self):
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('X')  # Invalid facelet
            expected = 'm X \x1b[0;0m'
            self.assertIn(expected, result)

    def test_display_top_down_face(self):
        printer = VCubeDisplay(self.cube)
        face = 'UUUUUUUUU'

        result = printer.display_top_down_face(face, '111111111', 0)
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


class TestVCubeDisplayExtendedNet(unittest.TestCase):

    def setUp(self):
        self.cube = VCube()
        self.printer = VCubeDisplay(self.cube)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_solved_cube_all_visible(self):
        """Test extended net display with solved cube and all faces visible."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)

        expected = (
            '                B  B  B \n'
            '             L  U  U  U  R \n'
            '             L  U  U  U  R \n'
            '             L  U  U  U  R \n'
            '    U  U  U                 U  U  U  U  U  U \n'
            ' B  L  L  L     F  F  F     R  R  R  B  B  B  L \n'
            ' B  L  L  L     F  F  F     R  R  R  B  B  B  L \n'
            ' B  L  L  L     F  F  F     R  R  R  B  B  B  L \n'
            '    D  D  D                 D  D  D  D  D  D \n'
            '             L  D  D  D  R \n'
            '             L  D  D  D  R \n'
            '             L  D  D  D  R \n'
            '                B  B  B \n'
        )

        self.assertEqual(result, expected)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_scrambled_cube_all_visible(self):
        """
        Test extended net display with scrambled cube
        and all faces visible.
        """
        self.cube.rotate("R U R' U'")

        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify structure - should have 14 lines (including empty line)
        lines = result.split('\n')
        self.assertEqual(len(lines), 14)

        # Verify each line contains expected
        # number of characters (excluding spaces)
        # Top line should have 3 face characters (B face)
        top_line_chars = [c for c in lines[0] if c.isalpha()]
        self.assertEqual(len(top_line_chars), 3)

        # Middle extended lines should have appropriate
        # number of face characters
        # Line with all faces should have many characters
        middle_lines = [lines[5], lines[6], lines[7]]  # Main horizontal strip
        for line in middle_lines:
            face_chars = [c for c in line if c.isalpha()]
            self.assertGreater(len(face_chars), 10)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_partial_masking(self):
        """Test extended net display with partial face masking."""
        faces = self.printer.split_faces(self.cube.state)
        # Create specific mask pattern - hide some U face facelets
        mask = (
            '000111111'  # U face - first 3 hidden, rest visible
            '111111111'  # R face - all visible
            '111111111'  # F face - all visible
            '111111111'  # D face - all visible
            '111111111'  # L face - all visible
            '111111111'  # B face - all visible
        )
        faces_mask = self.printer.split_faces(mask)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify structure is maintained
        lines = result.split('\n')
        self.assertEqual(len(lines), 14)

        # Result should still contain proper layout with some masked elements
        self.assertIn('U', result)
        self.assertIn('F', result)
        self.assertIn('R', result)
        self.assertIn('L', result)
        self.assertIn('B', result)
        self.assertIn('D', result)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_all_faces_masked(self):
        """Test extended net display with all faces masked (all zeros)."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('0' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify structure is maintained even when all masked
        lines = result.split('\n')
        self.assertEqual(len(lines), 14)

        # Should still contain face letters (masked display still shows them)
        self.assertIn('U', result)
        self.assertIn('F', result)
        self.assertIn('R', result)
        self.assertIn('L', result)
        self.assertIn('B', result)
        self.assertIn('D', result)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_single_face_state(self):
        """Test extended net display with non-standard single face state."""
        # Create cube with all facelets as 'X' for testing edge case
        test_state = 'X' * 54
        faces = self.printer.split_faces(test_state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify structure
        lines = result.split('\n')
        self.assertEqual(len(lines), 14)

        # Should contain all X characters
        x_count = result.count('X')
        self.assertGreater(x_count, 54)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_specific_rotation_state(self):
        """Test extended net display after specific rotation."""
        # Apply F move to create known state
        self.cube.rotate('F')

        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify structure
        lines = result.split('\n')
        self.assertEqual(len(lines), 14)

        # After F move, some faces should have mixed colors
        # Verify that not all characters in result are the same
        unique_faces = {c for c in result if c.strip() and c.isalpha()}
        # Should have all 6 face types
        self.assertGreaterEqual(len(unique_faces), 6)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_complex_masking_pattern(self):
        """Test extended net display with complex masking pattern."""
        faces = self.printer.split_faces(self.cube.state)
        # Create checkerboard-like mask pattern
        mask = (
            '101010101'  # U face - alternating pattern
            '010101010'  # R face - opposite pattern
            '101010101'  # F face - alternating pattern
            '010101010'  # D face - opposite pattern
            '101010101'  # L face - alternating pattern
            '010101010'  # B face - opposite pattern
        )
        faces_mask = self.printer.split_faces(mask)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify structure maintained
        lines = result.split('\n')
        self.assertEqual(len(lines), 14)

        # Should still show all face types
        for face_char in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face_char, result)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_line_structure(self):
        """Test that extended net display has correct line structure."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)
        lines = result.split('\n')

        # Should have exactly 14 lines (including empty line)
        self.assertEqual(len(lines), 14)

        # First line should be indented and contain B faces
        self.assertTrue(lines[0].startswith(' '))
        self.assertIn('B', lines[0])

        # Lines 1-3 should contain U face with L and R on sides
        for i in range(1, 4):
            self.assertIn('U', lines[i])
            self.assertIn('L', lines[i])
            self.assertIn('R', lines[i])

        # Line 4 should be the U extension line
        self.assertIn('U', lines[4])

        # Lines 5-7 should be the main horizontal strip with all faces
        for i in range(5, 8):
            line = lines[i]
            self.assertIn('B', line)
            self.assertIn('L', line)
            self.assertIn('F', line)
            self.assertIn('R', line)

        # Line 8 should be the D extension line
        self.assertIn('D', lines[8])

        # Lines 9-11 should contain D face with L and R on sides
        for i in range(9, 12):
            self.assertIn('D', lines[i])
            self.assertIn('L', lines[i])
            self.assertIn('R', lines[i])

        # Line 12 should contain B faces
        self.assertIn('B', lines[12])

        # Line 13 should be empty
        self.assertEqual(lines[13], '')

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_empty_faces_list(self):
        """Test extended net display with empty faces list."""
        # This tests error handling for edge case
        empty_faces = []
        empty_masks = []

        # This should raise an IndexError or similar
        with self.assertRaises((IndexError, KeyError)):
            self.printer.display_extended_net(empty_faces, empty_masks)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_mismatched_faces_masks(self):
        """Test extended net display with mismatched faces and masks lengths."""
        faces = self.printer.split_faces(self.cube.state)
        # Provide fewer masks than faces
        faces_mask = self.printer.split_faces('1' * 27)  # Only half the masks

        # This should raise an IndexError
        with self.assertRaises(IndexError):
            self.printer.display_extended_net(faces, faces_mask)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa FBT003
    def test_display_extended_net_face_character_counts(self):
        """Test that extended net contains expected character counts."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify that face characters appear in expected proportions
        face_counts = {}
        for char in result:
            if char.isalpha():
                face_counts[char] = face_counts.get(char, 0) + 1

        # Each face should appear multiple times in the extended net
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, face_counts)
            # Each face should appear at least 9 times
            # (some faces appear more in extended net)
            self.assertGreaterEqual(face_counts[face], 9)
