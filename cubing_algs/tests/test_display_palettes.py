"""Tests for cubing_algs.palettes module."""
import os
import unittest
from unittest.mock import patch

from cubing_algs.display.palettes import LOADED_PALETTES
from cubing_algs.display.palettes import PALETTES
from cubing_algs.display.palettes import FaceColorConfig
from cubing_algs.display.palettes import PaletteConfig
from cubing_algs.display.palettes import background_hex_to_ansi
from cubing_algs.display.palettes import build_ansi_color
from cubing_algs.display.palettes import build_ansi_palette
from cubing_algs.display.palettes import foreground_hex_to_ansi
from cubing_algs.display.palettes import hex_to_ansi
from cubing_algs.display.palettes import hex_to_rgb
from cubing_algs.display.palettes import hex_to_rgba
from cubing_algs.display.palettes import load_palette
from cubing_algs.display.palettes import register_palette
from cubing_algs.exceptions import PaletteAlreadyExistsError


class TestHexToAnsi(unittest.TestCase):
    """Test HEX to ANSI conversion functions."""

    def test_hex_to_ansi(self) -> None:
        """Test basic hex to ANSI conversion."""
        result = hex_to_ansi('38', '#FF0000')
        self.assertEqual(result, '\x1b[38;2;255;0;0m')

    def test_hex_to_rgb(self) -> None:
        """Test basic hex to rgb conversion."""
        result = hex_to_rgb('#FF0000')
        self.assertEqual(result, (255, 0, 0))

    def test_hex_compressed_to_rgb(self) -> None:
        """Test compressed hex to rgb conversion."""
        result = hex_to_rgb('#F00')
        self.assertEqual(result, (255, 0, 0))

    def test_hex_to_rgb_invalid_size(self) -> None:
        """Test compressed hex to rgb invalid size."""
        with self.assertRaises(ValueError):
            hex_to_rgb('#F0')

    def test_hex_to_rgb_invalid_value(self) -> None:
        """Test compressed hex to rgb invalid value."""
        with self.assertRaises(ValueError):
            hex_to_rgb('#G00')

    def test_background_hex_to_ansi(self) -> None:
        """Test hex to background ANSI conversion."""
        result = background_hex_to_ansi('#808080')
        self.assertEqual(result, '\x1b[48;2;128;128;128m')

    def test_foreground_hex_to_ansi(self) -> None:
        """Test hex to foreground ANSI conversion."""
        result = foreground_hex_to_ansi('#FFF')
        self.assertEqual(result, '\x1b[38;2;255;255;255m')

    def test_build_ansi_color(self) -> None:
        """Test building complete ANSI color scheme."""
        bg = '#F00'
        fg = '#FFF'
        result = build_ansi_color(bg, fg)
        expected = '\x1b[48;2;255;0;0m\x1b[38;2;255;255;255m'
        self.assertEqual(result, expected)


class HexToRgbaTestCase(unittest.TestCase):
    """Tests for hex_to_rgba conversion."""

    def test_six_digit_hex(self) -> None:
        """Test #rrggbb returns full opacity."""
        r, g, b, a = hex_to_rgba('#ff0000')
        self.assertEqual((r, g, b), (255, 0, 0))
        self.assertAlmostEqual(a, 1.0)

    def test_eight_digit_hex(self) -> None:
        """Test #rrggbbaa returns correct alpha."""
        r, g, b, a = hex_to_rgba('#11111180')
        self.assertEqual((r, g, b), (17, 17, 17))
        self.assertAlmostEqual(a, 128 / 255.0, places=3)

    def test_fully_transparent(self) -> None:
        """Test #rrggbb00 returns zero alpha."""
        _, _, _, a = hex_to_rgba('#ff000000')
        self.assertAlmostEqual(a, 0.0)

    def test_fully_opaque_eight_digit(self) -> None:
        """Test #rrggbbff returns full opacity."""
        _, _, _, a = hex_to_rgba('#ff0000ff')
        self.assertAlmostEqual(a, 1.0)

    def test_without_diese(self) -> None:
        """Test rrggbbaa returns correct opacity."""
        r, g, b, a = hex_to_rgba('11111180')
        self.assertEqual((r, g, b), (17, 17, 17))
        self.assertAlmostEqual(a, 128 / 255.0, places=3)


class TestBuildAnsiPalette(unittest.TestCase):
    """Test ANSI palette building."""

    def setUp(self) -> None:
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

    def test_build_ansi_palette_minimal(self) -> None:
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

    def test_build_ansi_palette_custom_parameters(self) -> None:
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

    def test_build_ansi_palette_with_face_overrides(self) -> None:
        """Test building palette with per-face font color overrides."""
        # Mix simple hex values with extended face configurations
        faces_config: tuple[str | FaceColorConfig, ...] = (
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

    def setUp(self) -> None:
        """Clear loaded palettes cache before each test."""
        LOADED_PALETTES.clear()
        self.faces = ['U', 'R', 'F', 'D', 'L', 'B']

    def test_load_palette_existing(self) -> None:
        """Test loading an existing palette."""
        palette = load_palette('default')

        # Should have all required keys
        self.assertIn('reset', palette)
        self.assertIn('hidden', palette)
        for face in self.faces:
            self.assertIn(face, palette)
            self.assertIn(f'{face}_masked', palette)
            self.assertIn(f'{face}_adjacent', palette)

    def test_load_palette_nonexistent_fallback_to_env(self) -> None:
        """Test loading nonexistent palette falls back to env var."""
        # This should cover the branch where palette_name not in PALETTES
        with patch.dict(os.environ, {'CUBING_ALGS_PALETTE': 'rgb'}):
            palette = load_palette('nonexistent_palette')

            # Should have loaded the RGB palette from env var
            self.assertIsNotNone(palette)
            self.assertIn('U', palette)

    def test_load_palette_nonexistent_fallback_to_default(self) -> None:
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

    def test_load_palette_caching(self) -> None:
        """Test that palettes are cached after first load."""
        # First load
        palette1 = load_palette('default')

        # Second load should return cached version
        palette2 = load_palette('default')

        self.assertIs(palette1, palette2)  # Should be the same object (cached)
        self.assertIn('default', LOADED_PALETTES)

    def test_load_all_predefined_palettes(self) -> None:
        """Test that all predefined palettes can be loaded."""
        for palette_name in PALETTES:
            palette = load_palette(palette_name)
            self.assertIsNotNone(palette)
            self.assertIn('U', palette)
            self.assertIn('reset', palette)

    def test_palette_with_extra_colors(self) -> None:
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

    def test_palettes_structure(self) -> None:
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


class TestRegisterPalette(unittest.TestCase):
    """Test palette registration functionality."""

    SIMPLE_FACES: tuple[str | FaceColorConfig, ...] = (
        '#FFFFFF', '#FF0000', '#00FF00',
        '#FFFF00', '#FF8700', '#0000FF',
    )

    def setUp(self) -> None:
        """Store initial PALETTES keys for cleanup."""
        self.initial_palettes = set(PALETTES.keys())
        LOADED_PALETTES.clear()

    def tearDown(self) -> None:
        """Remove any palettes that were added during tests."""
        current_palettes = set(PALETTES.keys())
        added_palettes = current_palettes - self.initial_palettes
        for palette_name in added_palettes:
            del PALETTES[palette_name]
        LOADED_PALETTES.clear()

    def test_register_new_palette(self) -> None:
        """Test successfully registering a new palette."""
        config = PaletteConfig(faces=self.SIMPLE_FACES)

        register_palette('custom_test', config)

        self.assertIn('custom_test', PALETTES)
        self.assertEqual(PALETTES['custom_test'], config)

    def test_register_palette_can_be_loaded(self) -> None:
        """Test that a registered palette can be loaded with load_palette."""
        register_palette(
            'loadable_test',
            PaletteConfig(faces=self.SIMPLE_FACES),
        )

        loaded = load_palette('loadable_test')
        self.assertIsNotNone(loaded)
        self.assertIn('U', loaded)
        self.assertIn('reset', loaded)
        self.assertIn('hidden', loaded)

    def test_register_palette_with_custom_settings(self) -> None:
        """Test registering a palette with all optional settings."""
        config = PaletteConfig(
            faces=self.SIMPLE_FACES,
            font='#000000',
            masked_background='#333333',
            adjacent_background='#666666',
            hidden_ansi='\x1b[48;2;0;0;0m\x1b[38;2;255;255;255m',
        )

        register_palette('custom_settings_test', config)

        self.assertIn('custom_settings_test', PALETTES)
        self.assertEqual(PALETTES['custom_settings_test'], config)

    def test_register_palette_raises_on_duplicate_name(self) -> None:
        """Test that registering with an existing name raises exception."""
        config = PaletteConfig(faces=self.SIMPLE_FACES)
        with self.assertRaises(PaletteAlreadyExistsError):
            register_palette('default', config)

    def test_register_palette_error_message_contains_name(self) -> None:
        """Test that the error message contains the palette name."""
        config = PaletteConfig(faces=self.SIMPLE_FACES)

        with self.assertRaises(PaletteAlreadyExistsError) as context:
            register_palette('default', config)

        error_message = str(context.exception)
        self.assertIn('default', error_message)
        self.assertIn('already exists', error_message.lower())

    def test_register_palette_raises_on_duplicate_builtin(self) -> None:
        """Test that built-in palette names cannot be overwritten."""
        builtin_names = ['rgb', 'vibrant', 'dracula', 'matrix']
        config = PaletteConfig(faces=self.SIMPLE_FACES)
        for name in builtin_names:
            with (
                self.subTest(palette=name),
                self.assertRaises(PaletteAlreadyExistsError),
            ):
                register_palette(name, config)

    def test_register_palette_with_minimal_config(self) -> None:
        """Test registering a palette with only faces defined."""
        faces: tuple[str | FaceColorConfig, ...] = (
            '#AAA', '#BBB', '#CCC', '#DDD', '#EEE', '#FFF',
        )
        register_palette('minimal_test', PaletteConfig(faces=faces))

        self.assertIn('minimal_test', PALETTES)
        loaded = load_palette('minimal_test')
        self.assertIn('U', loaded)
        self.assertIn('reset', loaded)

    def test_register_palette_with_dict_faces(self) -> None:
        """Test registering a palette with dictionary face configurations."""
        faces: tuple[str | FaceColorConfig, ...] = (
            {
                'background': '#FFFFFF',
                'font': '#000000',
            },
            '#FF0000',
            '#00FF00',
            {
                'background': '#FFFF00',
                'font': '#333333',
                'font_masked': '#666666',
            },
            '#FF8700',
            '#0000FF',
        )
        register_palette('dict_faces_test', PaletteConfig(faces=faces))

        self.assertIn('dict_faces_test', PALETTES)
        loaded = load_palette('dict_faces_test')
        self.assertIn('U', loaded)
        self.assertIn('D_masked', loaded)
