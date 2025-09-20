"""Tests for cubing_algs.palettes module."""

import os
import unittest
from unittest.mock import patch

from cubing_algs.palettes import LOADED_PALETTES
from cubing_algs.palettes import PALETTES
from cubing_algs.palettes import background_rgb_to_ansi
from cubing_algs.palettes import build_ansi_color
from cubing_algs.palettes import build_ansi_palette
from cubing_algs.palettes import foreground_rgb_to_ansi
from cubing_algs.palettes import load_palette
from cubing_algs.palettes import rgb_to_ansi


class TestRgbToAnsi(unittest.TestCase):
    """Test RGB to ANSI conversion functions."""

    def test_rgb_to_ansi(self):
        """Test basic RGB to ANSI conversion."""
        result = rgb_to_ansi('38', 255, 0, 0)
        self.assertEqual(result, '\x1b[38;2;255;0;0m')

    def test_background_rgb_to_ansi(self):
        """Test RGB to background ANSI conversion."""
        result = background_rgb_to_ansi(128, 128, 128)
        self.assertEqual(result, '\x1b[48;2;128;128;128m')

    def test_foreground_rgb_to_ansi(self):
        """Test RGB to foreground ANSI conversion."""
        result = foreground_rgb_to_ansi(255, 255, 255)
        self.assertEqual(result, '\x1b[38;2;255;255;255m')

    def test_build_ansi_color(self):
        """Test building complete ANSI color scheme."""
        bg = (255, 0, 0)
        fg = (255, 255, 255)
        result = build_ansi_color(bg, fg)
        expected = '\x1b[48;2;255;0;0m\x1b[38;2;255;255;255m'
        self.assertEqual(result, expected)


class TestBuildAnsiPalette(unittest.TestCase):
    """Test ANSI palette building."""

    def setUp(self):
        """Set up test data used by multiple test methods."""
        self.faces_bg = (
            (255, 255, 255),  # U
            (255, 0, 0),      # R
            (0, 255, 0),      # F
            (255, 255, 0),    # D
            (255, 135, 0),    # L
            (0, 0, 255),      # B
        )
        self.faces = ['U', 'R', 'F', 'D', 'L', 'B']

    def test_build_ansi_palette_minimal(self):
        """Test building palette with minimal parameters."""
        palette = build_ansi_palette(self.faces_bg)

        # Check basic structure
        self.assertIn('reset', palette)
        self.assertIn('masked', palette)
        self.assertEqual(palette['reset'], '\x1b[0;0m')

        # Check all faces are present
        for face in self.faces:
            self.assertIn(face, palette)
            self.assertIn(f'{face}_hidden', palette)

    def test_build_ansi_palette_custom_parameters(self):
        """Test building palette with custom font, hidden, and masked colors."""
        custom_font = '\x1b[38;2;50;50;50m'
        custom_hidden = '\x1b[48;2;200;200;200m'
        custom_masked = '\x1b[48;2;100;100;100m\x1b[38;2;200;200;200m'

        palette = build_ansi_palette(
            self.faces_bg,
            font_foreground_ansi=custom_font,
            hidden_background_ansi=custom_hidden,
            masked_ansi=custom_masked,
        )

        self.assertEqual(palette['masked'], custom_masked)
        # Check that faces use the custom font
        self.assertIn(custom_font, palette['U'])
        # Check that hidden faces use the custom hidden background
        self.assertIn(custom_hidden, palette['U_hidden'])

    def test_build_ansi_palette_with_face_overrides(self):
        """Test building palette with per-face font color overrides."""
        # Mix simple RGB tuples with extended face configurations
        faces_config = (
            (255, 255, 255),  # U - simple RGB
            {  # R - with custom font
                'background_rgb': (255, 0, 0),
                'font_ansi': '\x1b[38;2;255;255;255m',  # white font
            },
            (0, 255, 0),  # F - simple RGB
            {  # D - with custom font and hidden colors
                'background_rgb': (255, 255, 0),
                'font_ansi': '\x1b[38;2;0;0;0m',  # black font
                'hidden_background_ansi': '\x1b[48;2;100;100;0m',  # darker bg
                'hidden_font_ansi': '\x1b[38;2;200;200;0m',  # lighter font
            },
            (255, 135, 0),  # L - simple RGB
            (0, 0, 255),    # B - simple RGB
        )

        palette = build_ansi_palette(faces_config)

        # U should use default font
        self.assertIn('\x1b[38;2;8;8;8m', palette['U'])

        # R should use custom white font
        self.assertIn('\x1b[38;2;255;255;255m', palette['R'])

        # D should use custom black font
        self.assertIn('\x1b[38;2;0;0;0m', palette['D'])

        # D_hidden should use custom background and font
        self.assertIn('\x1b[48;2;100;100;0m', palette['D_hidden'])
        self.assertIn('\x1b[38;2;200;200;0m', palette['D_hidden'])

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
        self.assertIn('masked', palette)
        for face in self.faces:
            self.assertIn(face, palette)
            self.assertIn(f'{face}_hidden', palette)

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
                # All palettes must have faces_background_rgb
                self.assertIn('faces_background_rgb', palette_def)

                # Must have 6 face colors (U, R, F, D, L, B)
                faces_bg = palette_def['faces_background_rgb']
                self.assertEqual(len(faces_bg), 6)

                # Each face color should be either an RGB tuple
                # or a dict with background_rgb
                for face_config in faces_bg:
                    if isinstance(face_config, dict):
                        # Extended face configuration
                        self.assertIn('background_rgb', face_config)
                        rgb = face_config['background_rgb']
                        self.assertEqual(len(rgb), 3)
                        self.assertTrue(all(0 <= val <= 255 for val in rgb))
                    else:
                        # Simple RGB tuple
                        self.assertEqual(len(face_config), 3)
                        self.assertTrue(
                            all(0 <= val <= 255
                                for val in face_config),
                        )

    def test_palette_face_colors(self):
        """Test that palette face colors are valid RGB values."""
        for palette_name, palette_def in PALETTES.items():
            with self.subTest(palette=palette_name):
                faces_bg = palette_def['faces_background_rgb']
                for i, face_config in enumerate(faces_bg):
                    with self.subTest(face_index=i):
                        # Handle both simple RGB tuples
                        # and extended face configurations
                        if isinstance(face_config, dict):
                            # Extract RGB from dictionary configuration
                            self.assertIn('background_rgb', face_config)
                            r, g, b = face_config['background_rgb']
                        else:
                            # Simple RGB tuple
                            r, g, b = face_config

                        # Validate RGB values
                        self.assertIsInstance(r, int)
                        self.assertTrue(0 <= r <= 255)
                        self.assertIsInstance(g, int)
                        self.assertTrue(0 <= g <= 255)
                        self.assertIsInstance(b, int)
                        self.assertTrue(0 <= b <= 255)

    def test_palette_extra_keys_validity(self):
        """Test that extra keys in palettes have valid values."""
        for palette_name, palette_def in PALETTES.items():
            with self.subTest(palette=palette_name):
                if 'extra' in palette_def:
                    extra = palette_def['extra']
                    self.assertIsInstance(extra, dict)
                    # Extra should contain ANSI escape sequences
                    for key, value in extra.items():
                        self.assertIsInstance(key, str)
                        self.assertIsInstance(value, str)
                        self.assertIn('\x1b[', value)
