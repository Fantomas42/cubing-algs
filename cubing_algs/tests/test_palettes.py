"""Tests for cubing_algs.palettes module."""
import os
import unittest
from unittest.mock import patch

from cubing_algs.palettes import LOADED_PALETTES
from cubing_algs.palettes import PALETTES
from cubing_algs.palettes import background_hex_to_ansi
from cubing_algs.palettes import build_ansi_color
from cubing_algs.palettes import build_ansi_palette
from cubing_algs.palettes import foreground_hex_to_ansi
from cubing_algs.palettes import hex_to_ansi
from cubing_algs.palettes import hex_to_rgb
from cubing_algs.palettes import load_palette


class TestHexToAnsi(unittest.TestCase):
    """Test HEX to ANSI conversion functions."""

    def test_hex_to_ansi(self):
        """Test basic hex to ANSI conversion."""
        result = hex_to_ansi('38', '#FF0000')
        self.assertEqual(result, '\x1b[38;2;255;0;0m')

    def test_hex_to_rgb(self):
        """Test basic hex to rgb conversion."""
        result = hex_to_rgb('#FF0000')
        self.assertEqual(result, (255, 0, 0))

    def test_hex_compressed_to_rgb(self):
        """Test compressed hex to rgb conversion."""
        result = hex_to_rgb('#F00')
        self.assertEqual(result, (255, 0, 0))

    def test_hex_to_rgb_invalid_size(self):
        """Test compressed hex to rgb invalid size."""
        with self.assertRaises(ValueError):
            hex_to_rgb('#F0')

    def test_hex_to_rgb_invalid_value(self):
        """Test compressed hex to rgb invalid value."""
        with self.assertRaises(ValueError):
            hex_to_rgb('#G00')

    def test_background_hex_to_ansi(self):
        """Test hex to background ANSI conversion."""
        result = background_hex_to_ansi('#808080')
        self.assertEqual(result, '\x1b[48;2;128;128;128m')

    def test_foreground_hex_to_ansi(self):
        """Test hex to foreground ANSI conversion."""
        result = foreground_hex_to_ansi('#FFF')
        self.assertEqual(result, '\x1b[38;2;255;255;255m')

    def test_build_ansi_color(self):
        """Test building complete ANSI color scheme."""
        bg = '#F00'
        fg = '#FFF'
        result = build_ansi_color(bg, fg)
        expected = '\x1b[48;2;255;0;0m\x1b[38;2;255;255;255m'
        self.assertEqual(result, expected)


class TestBuildAnsiPalette(unittest.TestCase):
    """Test ANSI palette building."""

    def setUp(self):
        """Set up test data used by multiple test methods."""
        self.faces_bg = (
            '#FFFFFF',  # U
            '#FF0000',  # R
            '#00FF00',  # F
            '#FFFF00',  # D
            '#FF8700',  # L
            '#0000FF',  # B
        )
        self.faces = ['U', 'R', 'F', 'D', 'L', 'B']

    def test_build_ansi_palette_minimal(self):
        """Test building palette with minimal parameters."""
        palette = build_ansi_palette(self.faces_bg)

        # Check basic structure
        self.assertIn('reset', palette)
        self.assertIn('hidden', palette)
        self.assertEqual(palette['reset'], '\x1b[0;0m')

        # Check all faces are present
        for face in self.faces:
            self.assertIn(face, palette)
            self.assertIn(f'{face}_masked', palette)
            self.assertIn(f'{face}_adjacent', palette)

    def test_build_ansi_palette_custom_parameters(self):
        """Test building palette with custom font, hidden, and masked colors."""
        custom_font = '#FFFF00'
        custom_masked = '#000000'
        custom_hidden = '\x1b[48;2;100;100;100m\x1b[38;2;200;200;200m'

        palette = build_ansi_palette(
            self.faces_bg,
            font=custom_font,
            masked_background=custom_masked,
            hidden_ansi=custom_hidden,
        )

        self.assertEqual(palette['hidden'], custom_hidden)
        # Check that faces use the custom font
        self.assertIn('\x1b[38;2;255;255;0m', palette['U'])
        self.assertIn('\x1b[48;2;255;255;255m', palette['U'])
        # Check that masked faces use the custom masked background
        self.assertIn('\x1b[48;2;0;0;0m', palette['U_masked'])

    def test_build_ansi_palette_with_face_overrides(self):
        """Test building palette with per-face font color overrides."""
        # Mix simple hex values with extended face configurations
        faces_config = (
            '#FFFFFF',
            {
                'background': '#FF0000',
                'font': '#FFFFFF',
            },
            '#00FF00',
            {
                'background': '#FFFF00',
                'font': '#000000',
                'font_masked': '#FF00FF',
                'font_adjacent': '#FF00FF',
            },
            '#FF8400',
            '#0000FF',
        )

        palette = build_ansi_palette(faces_config)

        # U should use default font
        self.assertIn('\x1b[38;2;8;8;8m', palette['U'])

        # R should use custom white font
        self.assertIn('\x1b[38;2;255;255;255m', palette['R'])

        # D should use custom black font
        self.assertIn('\x1b[38;2;0;0;0m', palette['D'])

        # D_masked and adjacent should use custom font
        self.assertIn('\x1b[38;2;255;0;255m', palette['D_masked'])
        self.assertIn('\x1b[38;2;255;0;255m', palette['D_adjacent'])

        # Other faces should use defaults
        self.assertIn('\x1b[38;2;8;8;8m', palette['F'])
        self.assertIn('\x1b[38;2;8;8;8m', palette['L'])
        self.assertIn('\x1b[38;2;8;8;8m', palette['B'])


class TestLoadPalette(unittest.TestCase):
    """Test palette loading functionality."""

    def setUp(self):
        """Clear loaded palettes cache before each test."""
        LOADED_PALETTES.clear()
        self.faces = ['U', 'R', 'F', 'D', 'L', 'B']

    def test_load_palette_existing(self):
        """Test loading an existing palette."""
        palette = load_palette('default')

        # Should have all required keys
        self.assertIn('reset', palette)
        self.assertIn('hidden', palette)
        for face in self.faces:
            self.assertIn(face, palette)
            self.assertIn(f'{face}_masked', palette)
            self.assertIn(f'{face}_adjacent', palette)

    def test_load_palette_nonexistent_fallback_to_env(self):
        """Test loading nonexistent palette falls back to env var."""
        # This should cover the branch where palette_name not in PALETTES
        with patch.dict(os.environ, {'CUBING_ALGS_PALETTE': 'rgb'}):
            palette = load_palette('nonexistent_palette')

            # Should have loaded the RGB palette from env var
            self.assertIsNotNone(palette)
            self.assertIn('U', palette)

    def test_load_palette_nonexistent_fallback_to_default(self):
        """
        Test loading nonexistent palette falls back to default
        when no env var.
        """
        # Ensure env var is not set
        with patch.dict(os.environ, {}, clear=True):
            palette = load_palette('nonexistent_palette')

            # Should have loaded the default palette
            self.assertIsNotNone(palette)
            self.assertIn('U', palette)

    def test_load_palette_caching(self):
        """Test that palettes are cached after first load."""
        # First load
        palette1 = load_palette('default')

        # Second load should return cached version
        palette2 = load_palette('default')

        self.assertIs(palette1, palette2)  # Should be the same object (cached)
        self.assertIn('default', LOADED_PALETTES)

    def test_load_all_predefined_palettes(self):
        """Test that all predefined palettes can be loaded."""
        for palette_name in PALETTES:
            palette = load_palette(palette_name)
            self.assertIsNotNone(palette)
            self.assertIn('U', palette)
            self.assertIn('reset', palette)

    def test_palette_with_extra_colors(self):
        """Test loading palettes that have extra colors defined."""
        # Test dracula palette which has extra colors
        palette = load_palette('dracula')
        self.assertIn('U', palette)
        self.assertIn('reset', palette)

        # Test alucard palette which has extra colors
        palette = load_palette('alucard')
        self.assertIn('U', palette)
        self.assertIn('reset', palette)


class TestPaletteConstants(unittest.TestCase):
    """Test palette constants and structure."""

    def test_palettes_structure(self):
        """Test that all palettes have required structure."""
        for palette_name, palette_def in PALETTES.items():
            with self.subTest(palette=palette_name):
                # All palettes must have faces
                self.assertIn('faces', palette_def)

                # Must have 6 face colors (U, R, F, D, L, B)
                faces_bg = palette_def['faces']
                self.assertEqual(len(faces_bg), 6)

                # Each face color should be either an hexa tuple
                # or a dict with background at least
                for face_config in faces_bg:
                    if isinstance(face_config, dict):
                        # Extended face configuration
                        self.assertIn('background', face_config)
                        hexa = face_config['background']
                        self.assertIn('#', hexa)
                    else:
                        # Simple hexa color
                        self.assertIn('#', face_config)
