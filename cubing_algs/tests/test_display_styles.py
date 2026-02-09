"""Tests for letter style system."""
import unittest

from cubing_algs.display.styles import ANSI_STYLES
from cubing_algs.display.styles import LOADED_STYLES
from cubing_algs.display.styles import STYLES
from cubing_algs.display.styles import StyleConfig
from cubing_algs.display.styles import build_style
from cubing_algs.display.styles import get_piece_type
from cubing_algs.display.styles import load_style
from cubing_algs.display.styles import register_style
from cubing_algs.display.styles import resolve_style_ansi
from cubing_algs.exceptions import StyleAlreadyExistsError


class TestResolveStyleAnsi(unittest.TestCase):
    """Tests for resolve_style_ansi function."""

    def test_empty_string_returns_empty(self) -> None:
        """Test that empty string produces no ANSI codes."""
        self.assertEqual(resolve_style_ansi(''), '')

    def test_single_bold(self) -> None:
        """Test bold style resolution."""
        self.assertEqual(resolve_style_ansi('bold'), '\x1b[1m')

    def test_single_dim(self) -> None:
        """Test dim style resolution."""
        self.assertEqual(resolve_style_ansi('dim'), '\x1b[2m')

    def test_single_italic(self) -> None:
        """Test italic style resolution."""
        self.assertEqual(resolve_style_ansi('italic'), '\x1b[3m')

    def test_single_underline(self) -> None:
        """Test underline style resolution."""
        self.assertEqual(resolve_style_ansi('underline'), '\x1b[4m')

    def test_single_blink(self) -> None:
        """Test blink style resolution."""
        self.assertEqual(resolve_style_ansi('blink'), '\x1b[5m')

    def test_combined_bold_italic(self) -> None:
        """Test combined bold+italic style."""
        result = resolve_style_ansi('bold+italic')
        self.assertEqual(result, '\x1b[1m\x1b[3m')

    def test_combined_three_styles(self) -> None:
        """Test three combined styles."""
        result = resolve_style_ansi('bold+dim+italic')
        self.assertEqual(result, '\x1b[1m\x1b[2m\x1b[3m')

    def test_invalid_style_ignored(self) -> None:
        """Test that invalid style names are silently ignored."""
        self.assertEqual(resolve_style_ansi('invalid'), '')

    def test_mixed_valid_invalid(self) -> None:
        """Test that invalid parts are skipped in combinations."""
        result = resolve_style_ansi('bold+invalid+italic')
        self.assertEqual(result, '\x1b[1m\x1b[3m')

    def test_whitespace_handling(self) -> None:
        """Test that whitespace around style names is handled."""
        result = resolve_style_ansi(' bold + italic ')
        self.assertEqual(result, '\x1b[1m\x1b[3m')

    def test_all_ansi_styles_defined(self) -> None:
        """Test that all expected ANSI style codes are defined."""
        expected = {
            'bold', 'dim', 'italic', 'underline',
            'blink', 'hidden', 'strike',
        }
        self.assertEqual(set(ANSI_STYLES.keys()), expected)


class TestBuildStyle(unittest.TestCase):
    """Tests for build_style function."""

    def test_empty_config(self) -> None:
        """Test building style from empty config."""
        result = build_style(StyleConfig())
        for piece_type in ('corner', 'edge', 'center', 'fixed_center'):
            self.assertEqual(result[piece_type], '')

    def test_partial_config(self) -> None:
        """Test building style with only some piece types configured."""
        config = StyleConfig(fixed_center='bold')
        result = build_style(config)
        self.assertEqual(result['fixed_center'], '\x1b[1m')
        self.assertEqual(result['corner'], '')
        self.assertEqual(result['edge'], '')
        self.assertEqual(result['center'], '')

    def test_full_config(self) -> None:
        """Test building style with all piece types configured."""
        config = StyleConfig(
            corner='dim',
            edge='italic',
            center='underline',
            fixed_center='bold',
        )
        result = build_style(config)
        self.assertEqual(result['corner'], '\x1b[2m')
        self.assertEqual(result['edge'], '\x1b[3m')
        self.assertEqual(result['center'], '\x1b[4m')
        self.assertEqual(result['fixed_center'], '\x1b[1m')

    def test_combined_styles_in_config(self) -> None:
        """Test building style with combined style strings."""
        config = StyleConfig(fixed_center='bold+italic')
        result = build_style(config)
        self.assertEqual(result['fixed_center'], '\x1b[1m\x1b[3m')


class TestLoadStyle(unittest.TestCase):
    """Tests for load_style function."""

    @staticmethod
    def setUp() -> None:
        """Clear cache before each test."""
        LOADED_STYLES.clear()

    def test_load_default_style(self) -> None:
        """Test loading the default style preset."""
        style = load_style('default')
        self.assertEqual(style['fixed_center'], '\x1b[1m')
        self.assertEqual(style['corner'], '')

    def test_load_detailed_style(self) -> None:
        """Test loading the detailed style preset."""
        style = load_style('detailed')
        self.assertEqual(style['corner'], '\x1b[2m')
        self.assertEqual(style['fixed_center'], '\x1b[1m')

    def test_load_uniform_style(self) -> None:
        """Test loading the uniform style preset (no styling)."""
        style = load_style('uniform')
        for piece_type in ('corner', 'edge', 'center', 'fixed_center'):
            self.assertEqual(style[piece_type], '')

    def test_load_bold_style(self) -> None:
        """Test loading the bold style preset."""
        style = load_style('bold')
        for piece_type in ('corner', 'edge', 'center', 'fixed_center'):
            self.assertEqual(style[piece_type], '\x1b[1m')

    def test_fallback_to_default(self) -> None:
        """Test that unknown style name falls back to default."""
        style = load_style('nonexistent')
        default_style = load_style('default')
        self.assertEqual(style, default_style)

    def test_caching(self) -> None:
        """Test that loaded styles are cached."""
        style1 = load_style('default')
        style2 = load_style('default')
        self.assertIs(style1, style2)

    def test_cache_populated(self) -> None:
        """Test that loading populates the cache."""
        self.assertNotIn('default', LOADED_STYLES)
        load_style('default')
        self.assertIn('default', LOADED_STYLES)

    def test_all_builtin_styles_loadable(self) -> None:
        """Test that all built-in styles can be loaded."""
        for name in STYLES:
            style = load_style(name)
            self.assertIsInstance(style, dict)
            self.assertIn('corner', style)
            self.assertIn('edge', style)
            self.assertIn('center', style)
            self.assertIn('fixed_center', style)


class TestRegisterStyle(unittest.TestCase):
    """Tests for register_style function."""

    def test_register_new_style(self) -> None:
        """Test successfully registering a new style."""
        config = StyleConfig(corner='bold')
        register_style('custom_test', config)

        self.assertIn('custom_test', STYLES)
        self.assertEqual(STYLES['custom_test'], config)

    def test_register_style_can_be_loaded(self) -> None:
        """Test that a registered style can be loaded."""
        register_style(
            'loadable_test',
            StyleConfig(edge='italic'),
        )
        LOADED_STYLES.clear()

        style = load_style('loadable_test')
        self.assertEqual(style['edge'], '\x1b[3m')

    def test_register_style_raises_on_duplicate(self) -> None:
        """Test that registering with an existing name raises exception."""
        config = StyleConfig(corner='bold')
        with self.assertRaises(StyleAlreadyExistsError):
            register_style('default', config)

    def test_register_style_error_message_contains_name(self) -> None:
        """Test that the error message contains the style name."""
        config = StyleConfig(corner='bold')

        with self.assertRaises(StyleAlreadyExistsError) as context:
            register_style('default', config)

        error_message = str(context.exception)
        self.assertIn('default', error_message)
        self.assertIn('already exists', error_message.lower())

    def test_register_style_raises_on_duplicate_builtin(self) -> None:
        """Test that built-in style names cannot be overwritten."""
        builtin_names = ['default', 'detailed', 'bold', 'uniform']
        config = StyleConfig(corner='bold')
        for name in builtin_names:
            with (
                self.subTest(name=name),
                self.assertRaises(StyleAlreadyExistsError),
            ):
                register_style(name, config)

    def test_register_style_with_empty_config(self) -> None:
        """Test registering a style with empty config."""
        register_style('empty_test', StyleConfig())

        self.assertIn('empty_test', STYLES)
        LOADED_STYLES.clear()
        style = load_style('empty_test')
        for piece_type in ('corner', 'edge', 'center', 'fixed_center'):
            self.assertEqual(style[piece_type], '')


class TestGetPieceType(unittest.TestCase):
    """Tests for get_piece_type function."""

    def test_3x3_corners(self) -> None:
        """Test corner detection on 3x3 for all faces."""
        corner_positions = [0, 2, 6, 8]
        for face in range(6):
            for pos in corner_positions:
                index = face * 9 + pos
                with self.subTest(face=face, pos=pos):
                    self.assertEqual(get_piece_type(index, 3), 'corner')

    def test_3x3_edges(self) -> None:
        """Test edge detection on 3x3 for all faces."""
        edge_positions = [1, 3, 5, 7]
        for face in range(6):
            for pos in edge_positions:
                index = face * 9 + pos
                with self.subTest(face=face, pos=pos):
                    self.assertEqual(get_piece_type(index, 3), 'edge')

    def test_3x3_fixed_centers(self) -> None:
        """Test fixed center detection on 3x3 for all faces."""
        for face in range(6):
            index = face * 9 + 4
            with self.subTest(face=face):
                self.assertEqual(get_piece_type(index, 3), 'fixed_center')

    def test_5x5_corners(self) -> None:
        """Test corner detection on 5x5."""
        corner_positions = [0, 4, 20, 24]
        for pos in corner_positions:
            with self.subTest(pos=pos):
                self.assertEqual(get_piece_type(pos, 5), 'corner')

    def test_5x5_edges(self) -> None:
        """Test edge detection on 5x5."""
        edge_positions = [1, 2, 3, 5, 9, 10, 14, 15, 19, 21, 22, 23]
        for pos in edge_positions:
            with self.subTest(pos=pos):
                self.assertEqual(get_piece_type(pos, 5), 'edge')

    def test_5x5_fixed_center(self) -> None:
        """Test fixed center detection on 5x5."""
        self.assertEqual(get_piece_type(12, 5), 'fixed_center')

    def test_5x5_moveable_centers(self) -> None:
        """Test moveable center detection on 5x5."""
        center_positions = [6, 7, 8, 11, 13, 16, 17, 18]
        for pos in center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(get_piece_type(pos, 5), 'center')

    def test_4x4_no_fixed_center(self) -> None:
        """Test that 4x4 has no fixed center (even cube)."""
        center_positions = [5, 6, 9, 10]
        for pos in center_positions:
            with self.subTest(pos=pos):
                self.assertEqual(get_piece_type(pos, 4), 'center')
