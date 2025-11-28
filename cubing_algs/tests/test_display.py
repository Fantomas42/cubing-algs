"""Tests for VCubeDisplay rendering and formatting."""

import os
import unittest
from unittest.mock import patch

from cubing_algs.constants import FACE_ORDER
from cubing_algs.display import VCubeDisplay
from cubing_algs.vcube import VCube


class TestVCubeDisplay(unittest.TestCase):  # noqa: PLR0904
    """Tests for VCube display rendering and formatting."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()
        self.printer = VCubeDisplay(self.cube)

    def test_init_default_parameters(self) -> None:
        """Test init default parameters."""
        self.assertEqual(self.printer.cube, self.cube)
        self.assertEqual(self.printer.cube_size, 3)
        self.assertEqual(self.printer.face_size, 9)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_with_colors(self) -> None:
        """Test display facelet with colors."""
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa: FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('U')
            expected = 'm U \x1b[0;0m'
            self.assertIn(expected, result)

    @patch.dict(os.environ, {'TERM': 'other'})
    def test_display_facelet_without_colors(self) -> None:
        """Test display facelet without colors."""
        with patch('cubing_algs.display.USE_COLORS', False):  # noqa: FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('U')
            self.assertEqual(result, ' U ')

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_hidden(self) -> None:
        """Test display facelet hidden."""
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa: FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('U', '0')
            expected = 'm U \x1b[0;0m'
            self.assertIn(expected, result)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_invalid(self) -> None:
        """Test display facelet invalid."""
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa: FBT003
            printer = VCubeDisplay(self.cube)
            result = printer.display_facelet('X')  # Invalid facelet
            expected = 'm X \x1b[0;0m'
            self.assertIn(expected, result)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_display_facelet_with_effect(self) -> None:
        """
        Test display_facelet with an effect to cover
        position_based_effect call.
        """
        with patch('cubing_algs.display.USE_COLORS', True):  # noqa: FBT003
            printer = VCubeDisplay(self.cube, effect_name='shine')
            result = printer.display_facelet('U', facelet_index=0)
            # Should call position_based_effect since effect is set
            self.assertIsInstance(result, str)
            self.assertIn('U', result)

    def test_position_based_effect_method(self) -> None:
        """Test position_based_effect method directly."""
        printer = VCubeDisplay(self.cube, effect_name='shine')

        # Create valid ANSI color string that matches ANSI_TO_RGB pattern
        ansi_color = '\x1b[48;2;255;255;255m\x1b[38;2;0;0;0m'

        result = printer.position_based_effect(ansi_color, 0)

        self.assertIsInstance(result, str)
        self.assertIn('\x1b[', result)  # Should contain ANSI codes

    def test_display_top_down_face(self) -> None:
        """Test display top down face."""
        face = 'UUUUUUUUU'

        result = self.printer.display_top_down_face(face, '111111111', 0)
        lines = result.split('\n')

        self.assertEqual(len(lines), 4)

        for i in range(3):
            line = lines[i]
            self.assertTrue(line.startswith('         '))
            self.assertEqual(line.count('U'), 3)

    def test_display_without_orientation(self) -> None:
        """Test display without orientation."""
        result = self.printer.display()

        lines = result.split('\n')

        self.assertEqual(len(lines), 10)

        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    def test_display_with_orientation(self) -> None:
        """Test display with orientation."""
        initial_state = self.cube.state

        result = self.printer.display(orientation='DF')
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        self.assertEqual(len(lines), 10)

    def test_display_oll(self) -> None:
        """Test display oll."""
        self.cube.rotate("z2 F U F' R' F R U' R' F' R z2")

        initial_state = self.cube.state

        result = self.printer.display(mode='oll')
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        self.assertEqual(len(lines), 6)

    def test_display_pll(self) -> None:
        """Test display pll."""
        self.cube.rotate("z2 L2 U' L2 D F2 R2 U R2 D' F2 z2")

        initial_state = self.cube.state

        result = self.printer.display(mode='pll')
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        self.assertEqual(len(lines), 6)

    def test_display_f2l(self) -> None:
        """Test display f2l."""
        self.cube.rotate("z2 R U R' U' z2")

        result = self.printer.display(mode='f2l')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_af2l(self) -> None:
        """Test display af2l."""
        self.cube.rotate("z2 B' U' B F U F' U2")

        result = self.printer.display(mode='af2l')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_f2l_initial_no_reorientation(self) -> None:
        """Test display f2l initial no reorientation."""
        result = self.printer.display(mode='f2l', orientation='UF')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_cross(self) -> None:
        """Test display cross."""
        self.cube.rotate('B L F L F R F L B R')

        result = self.printer.display(mode='cross')
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_extended(self) -> None:
        """Test display with extended mode."""
        self.cube.rotate("R U R' U'")
        initial_state = self.cube.state

        result = self.printer.display(mode='extended')
        lines = result.split('\n')

        self.assertEqual(self.cube.state, initial_state)
        # Extended net should have more lines
        self.assertGreater(len(lines), 10)

    def test_display_structure(self) -> None:
        """Test display structure."""
        result = self.printer.display()

        lines = [line for line in result.split('\n') if line.strip()]

        self.assertEqual(len(lines), 9)

        middle_lines = lines[3:6]
        top_lines = lines[0:3]

        for middle_line in middle_lines:
            for top_line in top_lines:
                self.assertGreater(len(middle_line), len(top_line))

    def test_display_face_order(self) -> None:
        """Test display face order."""
        result = self.printer.display()
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

    def test_split_faces(self) -> None:
        """Test split faces."""
        self.assertEqual(
            self.printer.split_faces(self.cube.state),
            [
                'UUUUUUUUU',
                'RRRRRRRRR',
                'FFFFFFFFF',
                'DDDDDDDDD',
                'LLLLLLLLL',
                'BBBBBBBBB',
            ],
        )

    def test_split_faces_edge_case(self) -> None:
        """Test split_faces with non-standard state length."""
        result = self.printer.split_faces(self.cube.state)
        self.assertEqual(len(result), 6)

        for face in result:
            self.assertEqual(len(face), 9)

    def test_compute_mask(self) -> None:
        """Test compute mask."""
        base_mask = (
            '000000000'
            '111111111'
            '111111111'
            '000000000'
            '111111111'
            '111111111'
        )

        self.assertEqual(
            self.printer.compute_mask(
                self.cube,
                base_mask,
            ),
            base_mask,
        )

    def test_compute_mask_moves(self) -> None:
        """Test compute mask moves."""
        self.cube.rotate('R U F')

        base_mask = (
            '000000000'
            '111111111'
            '111111111'
            '000000000'
            '111111111'
            '111111111'
        )

        self.assertEqual(
            self.printer.compute_mask(
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

    def test_compute_no_mask(self) -> None:
        """Test compute no mask."""
        self.assertEqual(
            self.printer.compute_mask(self.cube, ''),
            54 * '1',
        )

    def test_compute_f2l_front_face(self) -> None:
        """Test compute f2l front face."""
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

    def test_compute_f2l_front_face_edge_cases(self) -> None:
        """Test compute_f2l_front_face with various edge cases."""
        # Should return empty string for solved cube
        result = self.printer.compute_f2l_front_face()
        self.assertEqual(result, '')

    def test_display_top_down_adjacent_facelets_no_break_line(self) -> None:
        """
        Test display_top_down_adjacent_facelets with break_line=False.

        This test covers the missing branch line 292->295 where break_line=False
        and no newline is added to the result.
        """
        face = 'UUUUUUUUU'
        face_mask = '111111111'
        face_index = 0

        # Test with break_line=False to cover the missing branch
        result = self.printer.display_top_down_adjacent_facelets(
            face, face_mask, face_index,
            break_line=False,
        )

        # Should not end with newline when break_line=False
        self.assertFalse(result.endswith('\n'))
        # Should contain the face characters
        self.assertIn('U', result)
        # Should contain exactly 3 face characters (for 3x3 cube)
        face_count = result.count('U')
        self.assertEqual(face_count, 3)

    def test_display_top_down_adjacent_facelets_with_break_line(self) -> None:
        """
        Test display_top_down_adjacent_facelets with break_line=True.

        This ensures the default behavior still works correctly.
        """
        face = 'FFFFFFFFF'
        face_mask = '111111111'
        face_index = 2

        # Test with break_line=True (default)
        result = self.printer.display_top_down_adjacent_facelets(
            face, face_mask, face_index,
            break_line=True,
        )

        # Should end with newline when break_line=True
        self.assertTrue(result.endswith('\n'))
        # Should contain the face characters
        self.assertIn('F', result)

    def test_display_top_down_adjacent_facelets_with_top_parameter(
        self,
    ) -> None:
        """
        Test display_top_down_adjacent_facelets
        with top=True and break_line=False.
        """
        face = 'LLLLLLLLL'
        face_mask = '111111111'
        face_index = 4

        result = self.printer.display_top_down_adjacent_facelets(
            face, face_mask, face_index,
            top=True,
            break_line=False,
        )

        # Should not end with newline
        self.assertFalse(result.endswith('\n'))
        # Should contain face characters in reversed order
        self.assertIn('L', result)

    def test_display_top_down_adjacent_facelets_with_end_parameter(
        self,
    ) -> None:
        """
        Test display_top_down_adjacent_facelets
        with end=True and break_line=False.
        """
        face = 'RRRRRRRRR'
        face_mask = '111111111'
        face_index = 1

        result = self.printer.display_top_down_adjacent_facelets(
            face, face_mask, face_index,
            end=True,
            break_line=False,
        )

        # Should not end with newline
        self.assertFalse(result.endswith('\n'))
        # Should contain face characters (end=True reverses the face)
        self.assertIn('R', result)

    def test_position_based_effect_no_effect_set(self) -> None:
        """
        Test position_based_effect
        when no effect is set raises AssertionError.
        """
        # Create printer without effect
        printer = VCubeDisplay(self.cube, effect_name='')
        ansi_color = '\x1b[48;2;255;255;255m\x1b[38;2;0;0;0m'

        # This should raise AssertionError due to assert self.effect is not None
        with self.assertRaises(AssertionError):
            printer.position_based_effect(ansi_color, 0)

    def test_position_based_effect_with_non_matching_ansi_colors(self) -> None:
        """
        Test position_based_effect with colors
        that don't match ANSI_TO_RGB pattern.

        This test covers the missing branch line 490->498 where the regex
        doesn't match and the if matches: block is skipped.
        This reveals a bug in the code where background_rgb and foreground_rgb
        are not initialized when matches is None.
        """
        printer = VCubeDisplay(self.cube, effect_name='shine')

        # Test with invalid ANSI color string that won't match the regex
        invalid_ansi_colors = 'invalid_color_string'

        result = printer.position_based_effect(invalid_ansi_colors, 0)

        self.assertEqual(result, invalid_ansi_colors)

    def test_compute_f2l_front_face_single_impacted_face(self) -> None:
        """Test compute_f2l_front_face with single impacted face."""
        # Create a state where only one face is impacted
        self.cube.rotate('R')

        result = self.printer.compute_f2l_front_face()
        # Should handle single face case
        self.assertIsInstance(result, str)

    def test_display_facelet_with_adjacent_flag(self) -> None:
        """
        Test display_facelet with adjacent=True
        to ensure effect is not applied.
        """
        printer = VCubeDisplay(self.cube, effect_name='shine')

        # Test with adjacent=True - effect should not be applied
        result = printer.display_facelet('U', facelet_index=0, adjacent=True)

        self.assertIsInstance(result, str)
        self.assertIn('U', result)

    def test_display_facelet_invalid_facelet_not_in_face_order(self) -> None:
        """Test display_facelet with facelet not in FACE_ORDER."""
        # Test with invalid facelet character
        result = self.printer.display_facelet('X')  # X is not in FACE_ORDER

        self.assertIsInstance(result, str)
        self.assertIn('X', result)

    def test_display_facelet_masked_hidden(self) -> None:
        """Test display_facelet with mask='0' (hidden)."""
        result = self.printer.display_facelet('U', mask='0')

        self.assertIsInstance(result, str)
        self.assertIn('U', result)

    def test_display_method_selection_edge_cases(self) -> None:
        """Test display method selection for different modes."""
        # Test unknown mode - should use default display_cube method
        result = self.printer.display(mode='unknown_mode')
        self.assertIsInstance(result, str)

        # Should contain standard cube layout
        lines = result.split('\n')
        self.assertEqual(len(lines), 10)

    def test_display_with_empty_orientation(self) -> None:
        """Test display with empty orientation string."""
        # Test with explicitly empty orientation
        result = self.printer.display(orientation='')

        self.assertIsInstance(result, str)
        self.assertIn('U', result)

    def test_display_spaces_various_counts(self) -> None:
        """Test display_spaces with different count values."""
        # Test with zero spaces
        result = self.printer.display_spaces(0)
        self.assertEqual(result, '')

        # Test with positive count
        result = self.printer.display_spaces(2)
        expected_length = self.printer.facelet_size * 2
        self.assertEqual(len(result), expected_length)
        self.assertTrue(all(c == ' ' for c in result))

    def test_display_spaces_emoji(self) -> None:
        """Test display_spaces with emoji facelets."""
        printer = VCubeDisplay(self.cube, facelet_type='emoji')
        # Test with zero spaces
        result = printer.display_spaces(0)
        self.assertEqual(result, '')

        # Test with positive count
        result = printer.display_spaces(2)
        self.assertEqual(len(result), 4)
        self.assertTrue(all(c == ' ' for c in result))

    def test_display_face_row_all_positions(self) -> None:
        """Test display_face_row for different faces and rows."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        # Test each face
        for face_key in ['U', 'R', 'F', 'D', 'L', 'B']:
            for row in range(3):
                result = self.printer.display_face_row(
                    faces, faces_mask, face_key, row,
                )
                self.assertIsInstance(result, str)
                # Should contain the face character 3 times (3x3 cube)
                self.assertEqual(result.count(face_key), 3)

    def test_display_facelet_by_face_all_positions(self) -> None:
        """Test display_facelet_by_face for all face positions."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        # Test all positions for each face
        for face_key in ['U', 'R', 'F', 'D', 'L', 'B']:
            for index in range(9):  # 9 positions per face
                result = self.printer.display_facelet_by_face(
                    faces, faces_mask, face_key, index,
                )
                self.assertIsInstance(result, str)
                self.assertIn(face_key, result)

    def test_display_face_indexes_multiple_indexes(self) -> None:
        """Test display_face_indexes with various index combinations."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        # Test with different index combinations
        test_indexes = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 4, 8],  # diagonal
            [2, 4, 6],  # other diagonal
        ]

        for indexes in test_indexes:
            result = self.printer.display_face_indexes(
                faces, faces_mask, 'U', indexes,
            )
            self.assertIsInstance(result, str)
            # Should contain U for each index
            self.assertEqual(result.count('U'), len(indexes))


class TestVCubeDisplayExtendedNet(unittest.TestCase):  # noqa: PLR0904
    """Tests for extended net display format."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()
        self.printer = VCubeDisplay(self.cube)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_solved_cube_all_visible(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_scrambled_cube_all_visible(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_partial_masking(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_all_faces_masked(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_single_face_state(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_specific_rotation_state(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_complex_masking_pattern(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_line_structure(self) -> None:
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
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_empty_faces_list(self) -> None:
        """Test extended net display with empty faces list."""
        # This should raise an IndexError or similar
        with self.assertRaises((IndexError, KeyError)):
            self.printer.display_extended_net([], [])

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_mismatched_faces_masks(self) -> None:
        """Test extended net display with mismatched faces and masks lengths."""
        faces = self.printer.split_faces(self.cube.state)
        # Provide fewer masks than faces
        faces_mask = self.printer.split_faces('1' * 27)  # Only half the masks

        # This should raise an IndexError
        with self.assertRaises(IndexError):
            self.printer.display_extended_net(faces, faces_mask)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_extended_net_face_character_counts(self) -> None:
        """Test that extended net contains expected character counts."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_extended_net(faces, faces_mask)

        # Verify that face characters appear in expected proportions
        face_counts: dict[str, int] = {}
        for char in result:
            if char.isalpha():
                face_counts[char] = face_counts.get(char, 0) + 1

        # Each face should appear multiple times in the extended net
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, face_counts)
            # Each face should appear at least 9 times
            # (some faces appear more in extended net)
            self.assertGreaterEqual(face_counts[face], 9)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_solved_cube(self) -> None:
        """Test display_linear with solved cube state."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)

        # Expected output:
        # 3 rows (for 3x3 cube), each with 6 faces + spaces + newline
        expected_lines = [
            ' U  U  U   R  R  R   F  F  F   D  D  D   L  L  L   B  B  B  ',
            ' U  U  U   R  R  R   F  F  F   D  D  D   L  L  L   B  B  B  ',
            ' U  U  U   R  R  R   F  F  F   D  D  D   L  L  L   B  B  B  ',
            '',
        ]
        expected = '\n'.join(expected_lines)

        self.assertEqual(result, expected)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_scrambled_cube(self) -> None:
        """Test display_linear with scrambled cube state."""
        self.cube.rotate("R U R' U'")
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)

        # Should have 4 lines (3 rows + empty line)
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)

        # Each line (except last) should contain all 6 face types
        for i in range(3):
            line = lines[i]
            # Should have some content for each face
            self.assertGreater(len(line.strip()), 0)

        # Last line should be empty
        self.assertEqual(lines[3], '')

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_with_masking(self) -> None:
        """Test display_linear with different masking patterns."""
        faces = self.printer.split_faces(self.cube.state)

        # Test with partial masking
        mask = (
            '111000111'  # U face - middle row hidden
            '111111111'  # R face - all visible
            '000111000'  # F face - top and bottom rows hidden
            '111111111'  # D face - all visible
            '101010101'  # L face - checkerboard pattern
            '111111111'  # B face - all visible
        )
        faces_mask = self.printer.split_faces(mask)

        result = self.printer.display_linear(faces, faces_mask)

        # Structure should remain the same - 4 lines
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)

        # Should still contain face characters
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_all_faces_masked(self) -> None:
        """Test display_linear with all faces masked."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('0' * 54)

        result = self.printer.display_linear(faces, faces_mask)

        # Structure should remain the same
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)

        # Should still show all face characters
        # (masking affects display color, not content)
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_structure_and_spacing(self) -> None:
        """Test that display_linear has correct structure and spacing."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)
        lines = result.split('\n')

        # Should have exactly 4 lines (3 data lines + 1 empty)
        self.assertEqual(len(lines), 4)

        # Each of the first 3 lines should have the same structure
        for i in range(3):
            line = lines[i]
            # Should end with a space (from the loop logic)
            self.assertTrue(line.endswith(' '))

            # Count face characters - should be 18 (3 per face * 6 faces)
            face_chars = [c for c in line if c.isalpha()]
            self.assertEqual(len(face_chars), 18)

        # Last line should be empty
        self.assertEqual(lines[3], '')

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_face_order_consistency(self) -> None:
        """Test that display_linear maintains consistent face order."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)
        lines = result.split('\n')

        # For each row, verify face order matches FACE_ORDER
        for i in range(3):  # 3 rows
            line = lines[i]
            # Extract face characters in groups of 3
            face_chars = [c for c in line if c.isalpha()]

            # Should have groups of 3 consecutive same characters
            for j in range(6):  # 6 faces
                start_idx = j * 3
                face_group = face_chars[start_idx:start_idx + 3]
                expected_face = FACE_ORDER[j]

                # All 3 characters in this group should be the same face
                self.assertEqual(len(set(face_group)), 1)
                self.assertEqual(face_group[0], expected_face)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_with_complex_state(self) -> None:
        """Test display_linear with complex mixed face state."""
        # Create a cube state with mixed face characters
        mixed_state = (
            'URFDLBURD'  # U face - mixed
            'FDLBURFDL'  # R face - mixed
            'LBURDFLBU'  # F face - mixed
            'RDFLBURDL'  # D face - mixed
            'BURLDBURL'  # L face - mixed
            'DLFBURFDL'  # B face - mixed
        )
        faces = self.printer.split_faces(mixed_state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)
        lines = result.split('\n')

        # Structure should be maintained
        self.assertEqual(len(lines), 4)

        # Should contain all face types
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

        # Each line should have 18 face characters
        for i in range(3):
            face_chars = [c for c in lines[i] if c.isalpha()]
            self.assertEqual(len(face_chars), 18)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_with_invalid_face_characters(self) -> None:
        """Test display_linear with invalid face characters."""
        # Create state with invalid characters
        invalid_state = 'X' * 54
        faces = self.printer.split_faces(invalid_state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)
        lines = result.split('\n')

        # Structure should be maintained
        self.assertEqual(len(lines), 4)

        # Should contain X characters
        self.assertIn('X', result)

        # Each line should still have 18 characters
        for i in range(3):
            face_chars = [c for c in lines[i] if c.isalpha()]
            self.assertEqual(len(face_chars), 18)

    def test_display_linear_integration_with_display_method(self) -> None:
        """Test display_linear integration through display() method."""
        result = self.printer.display(mode='linear')

        # Should be same as calling display_linear directly
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)
        expected = self.printer.display_linear(faces, faces_mask)

        self.assertEqual(result, expected)

    def test_display_linear_integration_with_orientation(self) -> None:
        """Test display_linear with orientation parameter."""
        # Test with different orientation
        result = self.printer.display(mode='linear', orientation='D')

        # Should produce valid output
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)

        # Should contain face characters
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    def test_display_linear_integration_with_mask(self) -> None:
        """Test display_linear with mask parameter."""
        # Test with custom mask
        test_mask = '1' * 27 + '0' * 27  # Half visible, half hidden
        result = self.printer.display(mode='linear', mask=test_mask)

        # Should produce valid output
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)

        # Should still show all face types
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_empty_faces_error_handling(self) -> None:
        """Test display_linear error handling with empty faces list."""
        # Should raise IndexError when trying to access faces
        with self.assertRaises(IndexError):
            self.printer.display_linear([], [])

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_mismatched_faces_masks_lengths(self) -> None:
        """Test display_linear with mismatched faces and masks lengths."""
        faces = self.printer.split_faces(self.cube.state)
        # Provide fewer masks than faces
        faces_mask = self.printer.split_faces('1' * 27)  # Only half

        # Should raise IndexError when accessing missing mask
        with self.assertRaises(IndexError):
            self.printer.display_linear(faces, faces_mask)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_insufficient_face_data(self) -> None:
        """Test display_linear with insufficient face data."""
        # Create faces with insufficient data
        short_faces = ['UUU', 'RRR', 'FFF', 'DDD', 'LLL', 'BBB']
        short_masks = ['111', '111', '111', '111', '111', '111']

        # Should raise IndexError when trying to access non-existent face rows
        with self.assertRaises(IndexError):
            self.printer.display_linear(short_faces, short_masks)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_boundary_cube_sizes(self) -> None:
        """Test display_linear behavior with current cube size assumptions."""
        # This test verifies the method works with the current cube_size (3)
        # and helps identify issues if cube_size changes in the future

        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)
        lines = result.split('\n')

        # Number of lines should equal cube_size + 1
        expected_lines = self.printer.cube_size + 1
        self.assertEqual(len(lines), expected_lines)

        # Each data line should have cube_size rows represented
        for i in range(self.printer.cube_size):
            line = lines[i]
            # Should have content for all faces
            self.assertGreater(len(line.strip()), 0)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    @patch('cubing_algs.display.USE_COLORS', True)  # noqa: FBT003
    def test_display_linear_with_colors_enabled(self) -> None:
        """Test display_linear with colors enabled."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)

        # Should contain ANSI color codes when colors are enabled
        self.assertIn('\x1b[', result)

        # Structure should remain the same
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    @patch('cubing_algs.display.USE_COLORS', True)  # noqa: FBT003
    def test_display_linear_with_effects_enabled(self) -> None:
        """Test display_linear with visual effects enabled."""
        printer = VCubeDisplay(self.cube, effect_name='shine')
        faces = printer.split_faces(self.cube.state)
        faces_mask = printer.split_faces('1' * 54)

        result = printer.display_linear(faces, faces_mask)

        # Should contain color codes (effects modify colors)
        self.assertIn('\x1b[', result)

        # Structure should remain the same
        lines = result.split('\n')
        self.assertEqual(len(lines), 4)

        # Should still contain face characters
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertIn(face, result)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_character_counting(self) -> None:
        """Test that display_linear produces expected character counts."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)

        # Count each face character in the result
        face_counts: dict[str, int] = {}
        for char in result:
            if char.isalpha():
                face_counts[char] = face_counts.get(char, 0) + 1

        # For a solved cube, each face should appear exactly 9 times
        # (3 rows * 3 characters per row)
        for face in ['U', 'R', 'F', 'D', 'L', 'B']:
            self.assertEqual(face_counts[face], 9)

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_linear_spacing_consistency(self) -> None:
        """Test that display_linear maintains consistent spacing."""
        faces = self.printer.split_faces(self.cube.state)
        faces_mask = self.printer.split_faces('1' * 54)

        result = self.printer.display_linear(faces, faces_mask)
        lines = result.split('\n')

        # Test spacing pattern in each line
        for i in range(3):  # First 3 lines
            line = lines[i]

            # Line should match expected pattern:
            # " X  X  X  Y  Y  Y  Z  Z  Z  A  A  A  B  B  B  C  C  C "
            # Starting with space, groups of 3 chars with 2 spaces between

            self.assertTrue(line.startswith(' '))  # Starts with space
            self.assertTrue(line.endswith(' '))    # Ends with space

            # Remove leading/trailing space for easier analysis
            trimmed = line.strip()

            # Should have specific pattern of spaces
            # Expected: "X  X  X   Y  Y  Y   ..." with
            # triple spaces between face groups
            parts = trimmed.split('   ')

            # Should have 6 face groups (one per face)
            self.assertEqual(len(parts), 6)

            # Each part should be a face section like "X  X  X"
            for part in parts:
                face_chars_in_part = [c for c in part if c.isalpha()]
                self.assertEqual(len(face_chars_in_part), 3)
                # Each face section should have the pattern "X  X  X"
                # (double spaces between chars)
                subparts = part.split('  ')
                self.assertEqual(len(subparts), 3)
                # Each subpart should be a single character
                for subpart in subparts:
                    self.assertEqual(len(subpart.strip()), 1)


class TestVCubeDisplayFaceletTypes(unittest.TestCase):
    """Test different facelet_type configurations and their display behavior."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.cube = VCube()

    def test_facelet_type_compact_initialization(self) -> None:
        """Test VCubeDisplay initialization with compact facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='compact')

        self.assertEqual(printer.facelet_type, 'compact')
        self.assertEqual(printer.facelet_size, 2)

    def test_facelet_type_condensed_initialization(self) -> None:
        """Test VCubeDisplay initialization with condensed facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='condensed')

        self.assertEqual(printer.facelet_type, 'condensed')
        self.assertEqual(printer.facelet_size, 1)

    def test_facelet_type_emoji_initialization(self) -> None:
        """Test VCubeDisplay initialization with emoji facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='emoji')

        self.assertEqual(printer.facelet_type, 'emoji')
        self.assertEqual(printer.facelet_size, 1)

    def test_facelet_type_default_initialization(self) -> None:
        """Test VCubeDisplay initialization with default facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='')

        self.assertEqual(printer.facelet_type, '')
        self.assertEqual(printer.facelet_size, 3)  # Default size

    def test_facelet_type_unknown_initialization(self) -> None:
        """Test VCubeDisplay initialization with unknown facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='unknown')

        self.assertEqual(printer.facelet_type, 'unknown')
        self.assertEqual(printer.facelet_size, 3)  # Default size when unknown

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    @patch('cubing_algs.display.USE_COLORS', True)  # noqa: FBT003
    def test_display_facelet_unlettered_type(self) -> None:
        """Test display_facelet with unlettered facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='unlettered')

        result = printer.display_facelet('U')

        # Should contain color codes but no letter
        self.assertIn('\x1b[', result)
        self.assertIn('   ', result)  # Three spaces instead of letter
        self.assertNotIn(' U ', result)  # Should not contain letter

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    @patch('cubing_algs.display.USE_COLORS', True)  # noqa: FBT003
    def test_display_facelet_compact_type(self) -> None:
        """Test display_facelet with compact facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='compact')

        result = printer.display_facelet('U')

        # Should contain color codes and block character
        self.assertIn('\x1b[', result)
        self.assertIn('◼︎ ', result)  # Block character with space
        self.assertNotIn(' U ', result)  # Should not contain letter

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    @patch('cubing_algs.display.USE_COLORS', True)  # noqa: FBT003
    def test_display_facelet_condensed_type(self) -> None:
        """Test display_facelet with condensed facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='condensed')

        result = printer.display_facelet('U')

        # Should contain color codes and block character without space
        self.assertIn('\x1b[', result)
        self.assertIn('◼︎', result)  # Block character without trailing space
        self.assertNotIn(' U ', result)  # Should not contain letter
        # Condensed should be shorter than compact
        compact_printer = VCubeDisplay(self.cube, facelet_type='compact')
        compact_result = compact_printer.display_facelet('U')
        self.assertLess(len(result), len(compact_result))

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    @patch('cubing_algs.display.USE_COLORS', True)  # noqa: FBT003
    def test_display_facelet_emoji_type(self) -> None:
        """Test display_facelet with emoji facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='emoji')

        result = printer.display_facelet('U')

        # Should contain color codes and block character without space
        self.assertNotIn('\x1b[', result)
        self.assertIn('⬜', result)  # Block character without trailing space
        self.assertNotIn(' U ', result)  # Should not contain letter

    @patch.dict(os.environ, {'TERM': 'other'})
    @patch('cubing_algs.display.USE_COLORS', False)  # noqa: FBT003
    def test_display_facelet_types_without_colors(self) -> None:
        """Test all facelet_types behave correctly when colors are disabled."""
        # When colors are disabled, all facelet types should return " U "
        for facelet_type in ['', 'compact', 'condensed', 'unlettered']:
            with self.subTest(facelet_type=facelet_type):
                printer = VCubeDisplay(self.cube, facelet_type=facelet_type)
                result = printer.display_facelet('U')
                self.assertEqual(result, ' U ')

    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    @patch('cubing_algs.display.USE_COLORS', True)  # noqa: FBT003
    def test_display_facelet_no_color_type(self) -> None:
        """Test display_facelet with no-color facelet_type."""
        printer = VCubeDisplay(self.cube, facelet_type='no-color')

        result = printer.display_facelet('U')

        # Should return plain text even when colors are available
        self.assertEqual(result, ' U ')
        self.assertNotIn('\x1b[', result)
