"""Tests for visual effects and color transformations."""
import unittest
from unittest.mock import patch

from cubing_algs.constants import FACE_NUMBER
from cubing_algs.display.effects import EFFECTS
from cubing_algs.display.effects import FACE_POSITIONS
from cubing_algs.display.effects import EffectConfig
from cubing_algs.display.effects import b_w_font
from cubing_algs.display.effects import brighten
from cubing_algs.display.effects import checkerboard
from cubing_algs.display.effects import chrome
from cubing_algs.display.effects import complement_font
from cubing_algs.display.effects import contrast
from cubing_algs.display.effects import contrast_font
from cubing_algs.display.effects import contrast_ratio
from cubing_algs.display.effects import cool_font
from cubing_algs.display.effects import copper
from cubing_algs.display.effects import diamond
from cubing_algs.display.effects import dim
from cubing_algs.display.effects import face_visible
from cubing_algs.display.effects import frosted
from cubing_algs.display.effects import get_position_factor
from cubing_algs.display.effects import global_light_position_factor
from cubing_algs.display.effects import glossy
from cubing_algs.display.effects import gold
from cubing_algs.display.effects import gradient_font
from cubing_algs.display.effects import grayscale_font
from cubing_algs.display.effects import hidden_font
from cubing_algs.display.effects import hls_to_rgb
from cubing_algs.display.effects import holographic
from cubing_algs.display.effects import hue_shift_font
from cubing_algs.display.effects import invert_luma_font
from cubing_algs.display.effects import linearize_srgb
from cubing_algs.display.effects import load_effect
from cubing_algs.display.effects import load_single_effect
from cubing_algs.display.effects import matte
from cubing_algs.display.effects import neon
from cubing_algs.display.effects import noop
from cubing_algs.display.effects import parse_effect_name
from cubing_algs.display.effects import parse_effect_parameters
from cubing_algs.display.effects import pastel_font
from cubing_algs.display.effects import plasma
from cubing_algs.display.effects import rainbow
from cubing_algs.display.effects import register_effect
from cubing_algs.display.effects import relative_luminance
from cubing_algs.display.effects import rgb_to_hls
from cubing_algs.display.effects import set_font
from cubing_algs.display.effects import shade_font
from cubing_algs.display.effects import shine
from cubing_algs.display.effects import silver
from cubing_algs.display.effects import spiral
from cubing_algs.display.effects import stripes
from cubing_algs.display.effects import vintage
from cubing_algs.display.effects import vivid_font
from cubing_algs.display.effects import warm_font
from cubing_algs.exceptions import EffectAlreadyExistsError


class TestPositioningFunctions(unittest.TestCase):
    """Test positioning and utility functions."""

    def test_face_positions_constant(self) -> None:
        """Test FACE_POSITIONS constant has correct structure."""
        self.assertEqual(len(FACE_POSITIONS), FACE_NUMBER)
        for face_index in range(FACE_NUMBER):
            self.assertIn(face_index, FACE_POSITIONS)
            self.assertEqual(len(FACE_POSITIONS[face_index]), 2)
            self.assertIsInstance(FACE_POSITIONS[face_index][0], int)
            self.assertIsInstance(FACE_POSITIONS[face_index][1], int)

    def test_global_light_position_factor_basic(self) -> None:
        """Test global_light_position_factor with basic inputs."""
        result = global_light_position_factor(0, 3)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_global_light_position_factor_different_cube_sizes(self) -> None:
        """Test global_light_position_factor with different cube sizes."""
        for cube_size in [2, 3, 4, 5]:
            result = global_light_position_factor(0, cube_size)
            self.assertIsInstance(result, float)
            self.assertGreaterEqual(result, 0.0)
            self.assertLessEqual(result, 1.0)

    def test_global_light_position_factor_all_faces(self) -> None:
        """Test global_light_position_factor across all faces."""
        cube_size = 3
        face_size = cube_size * cube_size

        for face_index in range(FACE_NUMBER):
            for local_index in range(face_size):
                facelet_index = face_index * face_size + local_index
                result = global_light_position_factor(facelet_index, cube_size)
                self.assertIsInstance(result, float)
                self.assertGreaterEqual(result, 0.0)
                self.assertLessEqual(result, 1.0)

    def test_global_light_position_factor_edge_cases(self) -> None:
        """Test global_light_position_factor with edge cases."""
        # Minimum cube size
        result = global_light_position_factor(0, 1)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

        # Test with facelet indices at the edge of valid range
        cube_size = 3
        max_valid_index = 6 * cube_size * cube_size - 1  # 53 for 3x3 cube
        result = global_light_position_factor(max_valid_index, cube_size)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_get_position_factor_default_parameters(self) -> None:
        """Test get_position_factor with default parameters."""
        result = get_position_factor(0, 3)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_get_position_factor_facelet_modes(self) -> None:
        """Test get_position_factor with different facelet modes."""
        facelet_index = 4
        cube_size = 3

        # Local mode
        result_local = get_position_factor(
            facelet_index, cube_size, facelet_mode='local',
        )
        self.assertIsInstance(result_local, float)

        # Global mode
        result_global = get_position_factor(
            facelet_index, cube_size, facelet_mode='global',
        )
        self.assertIsInstance(result_global, float)

    def test_get_position_factor_position_modes(self) -> None:
        """Test get_position_factor with different position modes."""
        facelet_index = 4
        cube_size = 3

        # Numeral mode
        result_numeral = get_position_factor(
            facelet_index, cube_size, position_mode='numeral',
        )
        self.assertIsInstance(result_numeral, float)

        # Light mode
        result_light = get_position_factor(
            facelet_index, cube_size, position_mode='light',
        )
        self.assertIsInstance(result_light, float)

    def test_get_position_factor_mode_combinations(self) -> None:
        """Test get_position_factor with all mode combinations."""
        facelet_index = 4
        cube_size = 3

        modes = [
            {'facelet_mode': 'local', 'position_mode': 'numeral'},
            {'facelet_mode': 'global', 'position_mode': 'numeral'},
            {'facelet_mode': 'local', 'position_mode': 'light'},
            {'facelet_mode': 'global', 'position_mode': 'light'},
        ]

        for kwargs in modes:
            result = get_position_factor(facelet_index, cube_size, **kwargs)  # type: ignore[arg-type]
            self.assertIsInstance(result, float)
            self.assertGreaterEqual(result, 0.0)


class RGBTestCase(unittest.TestCase):
    """Tests for RGB color manipulation and transformation effects."""

    def validate_rgb_output(self, rgb: tuple[int, int, int]) -> None:
        """Help to validate RGB output is properly clamped."""
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        for component in rgb:
            self.assertIsInstance(component, int)
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)


class TestBasicEffects(RGBTestCase):
    """Test basic lighting and surface effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.test_rgb = (128, 64, 192)
        self.facelet_index = 4
        self.cube_size = 3

    def test_shine_basic(self) -> None:
        """Test shine effect with basic parameters."""
        result = shine(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_shine_with_intensity(self) -> None:
        """Test shine effect with different intensity values."""
        intensities = [0.0, 0.3, 0.5, 0.8, 1.0]
        for intensity in intensities:
            result = shine(
                self.test_rgb,
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])

    def test_neon_basic(self) -> None:
        """Test neon effect with basic parameters."""
        result = neon(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_neon_with_parameters(self) -> None:
        """Test neon effect with different parameters."""
        result = neon(
            self.test_rgb,
            self.test_rgb,
            self.facelet_index,
            self.cube_size,
            intensity=0.8,
            saturation=1.5,
        )
        self.validate_rgb_output(result[0])

    def test_neon_black_input(self) -> None:
        """Test neon effect with black input (edge case)."""
        black_rgb = (0, 0, 0)
        result = neon(black_rgb, black_rgb, self.facelet_index, self.cube_size)
        self.validate_rgb_output(result[0])

    def test_chrome_basic(self) -> None:
        """Test chrome effect with basic parameters."""
        result = chrome(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_chrome_with_parameters(self) -> None:
        """Test chrome effect with different parameters."""
        result = chrome(
            self.test_rgb,
            self.test_rgb,
            self.facelet_index,
            self.cube_size,
            intensity=0.7,
            metallic=0.8,
        )
        self.validate_rgb_output(result[0])

    def test_gold_basic(self) -> None:
        """Test gold effect with basic parameters."""
        result = gold(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_gold_with_warmth(self) -> None:
        """Test gold effect with different warmth values."""
        warmths = [0.0, 0.5, 1.0, 1.5]
        for warmth in warmths:
            result = gold(
                self.test_rgb,
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                warmth=warmth,
            )
            self.validate_rgb_output(result[0])

    def test_silver_basic(self) -> None:
        """Test silver effect with basic parameters."""
        result = silver(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_silver_with_intensity(self) -> None:
        """Test silver effect with different intensity values."""
        intensities = [0.1, 0.5, 0.9]
        for intensity in intensities:
            result = silver(
                self.test_rgb,
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])

    def test_copper_basic(self) -> None:
        """Test copper effect with basic parameters."""
        result = copper(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_copper_with_parameters(self) -> None:
        """Test copper effect with different parameters."""
        result = copper(
            self.test_rgb,
            self.test_rgb,
            self.facelet_index,
            self.cube_size,
            intensity=0.8,
            warmth=1.2,
        )
        self.validate_rgb_output(result[0])


class TestPatternEffects(RGBTestCase):
    """Test pattern-based effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.test_rgb = (100, 150, 200)
        self.cube_size = 3

    def test_diamond_sparkle_positions(self) -> None:
        """Test diamond effect at sparkle positions."""
        # Test specific sparkle positions
        sparkle_positions = [(0, 0), (1, 1), (2, 2), (0, 2), (2, 0)]

        for row, col in sparkle_positions:
            facelet_index = row * self.cube_size + col
            result = diamond(
                self.test_rgb, self.test_rgb,
                facelet_index, self.cube_size,
            )
            self.validate_rgb_output(result[0])
            # Sparkle positions should be brighter
            self.assertGreater(sum(result[0]), sum(self.test_rgb))

    def test_diamond_non_sparkle_positions(self) -> None:
        """Test diamond effect at non-sparkle positions."""
        # Test non-sparkle position
        facelet_index = 1 * self.cube_size + 0  # Position (1, 0)
        result = diamond(
            self.test_rgb, self.test_rgb,
            facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_rainbow_basic(self) -> None:
        """Test rainbow effect with basic parameters."""
        for facelet_index in range(9):  # Test all positions on a 3x3 face
            result = rainbow(
                self.test_rgb, self.test_rgb,
                facelet_index, self.cube_size,
            )
            self.validate_rgb_output(result[0])

    def test_checkerboard_pattern(self) -> None:
        """Test checkerboard effect creates alternating pattern."""
        results = []
        for facelet_index in range(9):  # Test all positions on a 3x3 face
            result = checkerboard(
                self.test_rgb, self.test_rgb,
                facelet_index, self.cube_size,
            )
            self.validate_rgb_output(result[0])
            results.append(result)

        # Check that adjacent positions have different brightness
        # Position (0,0) and (0,1) should be different
        pos_00 = checkerboard(
            self.test_rgb, self.test_rgb,
            0, self.cube_size,
        )
        pos_01 = checkerboard(
            self.test_rgb, self.test_rgb,
            1, self.cube_size,
        )
        self.assertNotEqual(pos_00, pos_01)

    def test_checkerboard_with_intensity(self) -> None:
        """Test checkerboard effect with different intensities."""
        intensities = [0.2, 0.5, 0.8]
        for intensity in intensities:
            result = checkerboard(
                self.test_rgb, self.test_rgb,
                0, self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])

    def test_stripes_directions(self) -> None:
        """Test stripes effect with different directions."""
        directions = ['horizontal', 'vertical', 'diagonal']
        for direction in directions:
            result = stripes(
                self.test_rgb, self.test_rgb,
                4, self.cube_size,
                direction=direction,
            )
            self.validate_rgb_output(result[0])

    def test_stripes_with_parameters(self) -> None:
        """Test stripes effect with different parameters."""
        result = stripes(
            self.test_rgb, self.test_rgb,
            4, self.cube_size,
            direction='horizontal',
            frequency=3,
            intensity=0.6,
        )
        self.validate_rgb_output(result[0])

    def test_spiral_basic(self) -> None:
        """Test spiral effect with basic parameters."""
        for facelet_index in range(9):
            result = spiral(
                self.test_rgb, self.test_rgb,
                facelet_index, self.cube_size,
            )
            self.validate_rgb_output(result[0])

    def test_spiral_with_intensity(self) -> None:
        """Test spiral effect with different intensities."""
        intensities = [0.1, 0.5, 0.9]
        for intensity in intensities:
            result = spiral(
                self.test_rgb, self.test_rgb,
                4, self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])

    def test_plasma_basic(self) -> None:
        """Test plasma effect with basic parameters."""
        for facelet_index in range(9):
            result = plasma(
                self.test_rgb, self.test_rgb,
                facelet_index, self.cube_size,
            )
            self.validate_rgb_output(result[0])

    def test_plasma_with_intensity(self) -> None:
        """Test plasma effect with different intensities."""
        intensities = [0.2, 0.4, 0.8]
        for intensity in intensities:
            result = plasma(
                self.test_rgb, self.test_rgb,
                4, self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])


class TestSurfaceEffects(RGBTestCase):
    """Test surface finish effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.test_rgb = (120, 80, 160)
        self.facelet_index = 4
        self.cube_size = 3

    def test_matte_basic(self) -> None:
        """Test matte effect with basic parameters."""
        result = matte(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])
        # Matte should reduce brightness
        self.assertLessEqual(sum(result[0]), sum(self.test_rgb))

    def test_matte_ignores_position(self) -> None:
        """Test that matte effect ignores facelet position."""
        result1 = matte(
            self.test_rgb, self.test_rgb,
            0, self.cube_size,
        )
        result2 = matte(
            self.test_rgb, self.test_rgb,
            8, self.cube_size,
        )
        self.assertEqual(result1, result2)

    def test_matte_with_reduction(self) -> None:
        """Test matte effect with different reduction values."""
        reductions = [0.1, 0.3, 0.5, 0.8]
        for reduction in reductions:
            result = matte(
                self.test_rgb,
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                reduction=reduction,
            )
            self.validate_rgb_output(result[0])

    def test_glossy_basic(self) -> None:
        """Test glossy effect with basic parameters."""
        result = glossy(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_glossy_with_intensity(self) -> None:
        """Test glossy effect with different intensities."""
        intensities = [0.2, 0.5, 1.0]
        for intensity in intensities:
            result = glossy(
                self.test_rgb,
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])

    def test_frosted_basic(self) -> None:
        """Test frosted effect with basic parameters."""
        result = frosted(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_frosted_with_intensity(self) -> None:
        """Test frosted effect with different intensities."""
        intensities = [0.1, 0.4, 0.7]
        for intensity in intensities:
            result = frosted(
                self.test_rgb,
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])

    def test_holographic_basic(self) -> None:
        """Test holographic effect with basic parameters."""
        result = holographic(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_holographic_with_intensity(self) -> None:
        """Test holographic effect with different intensities."""
        intensities = [0.3, 0.6, 0.9]
        for intensity in intensities:
            result = holographic(
                self.test_rgb, self.test_rgb,
                self.facelet_index, self.cube_size,
                intensity=intensity,
            )
            self.validate_rgb_output(result[0])


class TestAdjustmentEffects(RGBTestCase):
    """Test color adjustment effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.test_rgb = (128, 128, 128)
        self.facelet_index = 4
        self.cube_size = 3

    def test_dim_basic(self) -> None:
        """Test dim effect with basic parameters."""
        result = dim(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])
        # Dim should reduce brightness
        self.assertLessEqual(sum(result[0]), sum(self.test_rgb))

    def test_dim_ignores_position(self) -> None:
        """Test that dim effect ignores facelet position."""
        result1 = dim(
            self.test_rgb, self.test_rgb,
            0, self.cube_size,
        )
        result2 = dim(
            self.test_rgb, self.test_rgb,
            8, self.cube_size,
        )
        self.assertEqual(result1, result2)

    def test_dim_with_factor(self) -> None:
        """Test dim effect with different factors."""
        factors = [0.1, 0.5, 0.7, 0.9]
        for factor in factors:
            result = dim(
                self.test_rgb, self.test_rgb,
                self.facelet_index, self.cube_size,
                factor=factor,
            )
            self.validate_rgb_output(result[0])

    def test_brighten_basic(self) -> None:
        """Test brighten effect with basic parameters."""
        result = brighten(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])
        # Brighten should increase brightness
        self.assertGreaterEqual(sum(result[0]), sum(self.test_rgb))

    def test_brighten_ignores_position(self) -> None:
        """Test that brighten effect ignores facelet position."""
        result1 = brighten(
            self.test_rgb, self.test_rgb,
            0, self.cube_size,
        )
        result2 = brighten(
            self.test_rgb, self.test_rgb,
            8, self.cube_size,
        )
        self.assertEqual(result1, result2)

    def test_brighten_with_factor(self) -> None:
        """Test brighten effect with different factors."""
        factors = [1.1, 1.3, 1.5, 2.0]
        for factor in factors:
            result = brighten(
                self.test_rgb, self.test_rgb,
                self.facelet_index, self.cube_size,
                factor=factor,
            )
            self.validate_rgb_output(result[0])

    def test_contrast_basic(self) -> None:
        """Test contrast effect with basic parameters."""
        result = contrast(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_contrast_ignores_position(self) -> None:
        """Test that contrast effect ignores facelet position."""
        result1 = contrast(
            self.test_rgb, self.test_rgb,
            0, self.cube_size,
        )
        result2 = contrast(
            self.test_rgb, self.test_rgb,
            8, self.cube_size,
        )
        self.assertEqual(result1, result2)

    def test_contrast_with_factor(self) -> None:
        """Test contrast effect with different factors."""
        factors = [0.5, 1.0, 1.5, 2.0]
        for factor in factors:
            result = contrast(
                self.test_rgb, self.test_rgb,
                self.facelet_index, self.cube_size,
                factor=factor,
            )
            self.validate_rgb_output(result[0])

    def test_contrast_with_different_colors(self) -> None:
        """Test contrast effect with colors above and below middle gray."""
        # Test with bright color
        bright_rgb = (200, 200, 200)
        result_bright = contrast(
            bright_rgb, bright_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result_bright[0])

        # Test with dark color
        dark_rgb = (50, 50, 50)
        result_dark = contrast(
            dark_rgb, dark_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result_dark[0])

    def test_vintage_basic(self) -> None:
        """Test vintage effect with basic parameters."""
        result = vintage(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_vintage_ignores_position(self) -> None:
        """Test that vintage effect ignores facelet position."""
        result1 = vintage(
            self.test_rgb, self.test_rgb,
            0, self.cube_size,
        )
        result2 = vintage(
            self.test_rgb, self.test_rgb,
            8, self.cube_size,
        )
        self.assertEqual(result1, result2)

    def test_vintage_with_parameters(self) -> None:
        """Test vintage effect with different parameters."""
        result = vintage(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
            sepia=0.8,
            desaturation=0.5,
        )
        self.validate_rgb_output(result[0])

    def test_face_visible_basic(self) -> None:
        """Test face_visible effect with basic parameters."""
        result = face_visible(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.validate_rgb_output(result[0])

    def test_face_visible_front_vs_back(self) -> None:
        """Test face_visible effect treats front and back faces differently."""
        # Front face (face index 0, 1, 2)
        front_facelet = 4  # Face 0
        result_front = face_visible(
            self.test_rgb, self.test_rgb,
            front_facelet, self.cube_size,
        )

        # Back face (face index 3, 4, 5)
        back_facelet = 3 * 9 + 4  # Face 3
        result_back = face_visible(
            self.test_rgb, self.test_rgb,
            back_facelet, self.cube_size,
        )

        self.validate_rgb_output(result_front[0])
        self.validate_rgb_output(result_back[0])

        # Front faces should be brighter
        self.assertGreater(sum(result_front[0]), sum(result_back[0]))


class TestUtilityEffects(unittest.TestCase):
    """Test utility effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.test_rgb = (100, 150, 200)
        self.facelet_index = 4
        self.cube_size = 3

    def test_noop_returns_unchanged(self) -> None:
        """Test that noop effect returns input unchanged."""
        result = noop(
            self.test_rgb, self.test_rgb,
            self.facelet_index, self.cube_size,
        )
        self.assertEqual(result, (self.test_rgb, self.test_rgb))

    def test_noop_ignores_all_parameters(self) -> None:
        """Test that noop effect ignores all parameters."""
        result1 = noop(self.test_rgb, self.test_rgb, 0, 2)
        result2 = noop(
            self.test_rgb, self.test_rgb,
            100, 10,
            intensity=5.0,
            saturation=1.0,
        )
        self.assertEqual(result1, (self.test_rgb, self.test_rgb))
        self.assertEqual(result2, (self.test_rgb, self.test_rgb))


class TestEdgeCases(RGBTestCase):
    """Test edge cases and boundary conditions."""

    def test_rgb_clamping_white(self) -> None:
        """Test RGB clamping with white input."""
        white_rgb = (255, 255, 255)
        effects_to_test = [shine, neon, chrome, gold, silver, copper, brighten]

        for effect in effects_to_test:
            result = effect(white_rgb, white_rgb, 0, 3)
            self.validate_rgb_output(result[0])

    def test_rgb_clamping_black(self) -> None:
        """Test RGB clamping with black input."""
        black_rgb = (0, 0, 0)
        effects_to_test = [shine, neon, chrome, gold, silver, copper, dim]

        for effect in effects_to_test:
            result = effect(black_rgb, black_rgb, 0, 3)
            self.validate_rgb_output(result[0])

    def test_different_cube_sizes(self) -> None:
        """Test effects with different cube sizes."""
        test_rgb = (128, 64, 192)
        cube_sizes = [1, 2, 3, 4, 5, 10]

        for cube_size in cube_sizes:
            for facelet_index in range(cube_size * cube_size):
                result = shine(test_rgb, test_rgb, facelet_index, cube_size)
                self.validate_rgb_output(result[0])

    def test_large_facelet_indices(self) -> None:
        """Test effects with large facelet indices within valid range."""
        test_rgb = (100, 100, 100)
        cube_size = 3
        # Test with indices from different faces but within valid range
        large_indices = [27, 45, 53]  # Face 3, 5, and last valid index

        for facelet_index in large_indices:
            result = diamond(test_rgb, test_rgb, facelet_index, cube_size)
            self.validate_rgb_output(result[0])

    def test_extreme_parameter_values(self) -> None:
        """Test effects with extreme parameter values."""
        test_rgb = (128, 128, 128)

        # Test with very high intensity
        result = shine(test_rgb, test_rgb, 0, 3, intensity=10.0)
        self.validate_rgb_output(result[0])

        # Test with zero intensity
        result = shine(test_rgb, test_rgb, 0, 3, intensity=0.0)
        self.validate_rgb_output(result[0])

        # Test with negative values
        result = dim(test_rgb, test_rgb, 0, 3, factor=-1.0)
        self.validate_rgb_output(result[0])

    def test_minimum_cube_size(self) -> None:
        """Test effects with minimum cube size of 1."""
        test_rgb = (128, 64, 192)
        cube_size = 1
        facelet_index = 0

        effects_to_test = [
            shine,
            neon,
            chrome,
            gold,
            silver,
            copper,
            diamond,
            rainbow,
            matte,
            glossy,
            frosted,
            checkerboard,
            stripes,
            spiral,
            plasma,
            holographic,
            dim,
            brighten,
            contrast,
            face_visible,
            vintage,
            noop,
        ]

        for effect in effects_to_test:
            result = effect(test_rgb, test_rgb, facelet_index, cube_size)
            self.validate_rgb_output(result[0])


class TestEffectsConfiguration(unittest.TestCase):
    """Test the EFFECTS configuration dictionary."""

    def test_effects_structure(self) -> None:
        """Test that EFFECTS dictionary has correct structure."""
        self.assertIsInstance(EFFECTS, dict)
        self.assertGreater(len(EFFECTS), 0)

        for effect_name, effect_config in EFFECTS.items():
            self.assertIsInstance(effect_name, str)
            self.assertIsInstance(effect_config, dict)
            self.assertIn('function', effect_config)
            self.assertTrue(callable(effect_config['function']))

    def test_effects_have_expected_functions(self) -> None:
        """Test that expected effects are present in EFFECTS."""
        expected_effects = [
            'shine',
            'soft',
            'gradient',
            'neon',
            'chrome',
            'gold',
            'silver',
            'copper',
            'diamond',
            'rainbow',
            'matte',
            'glossy',
            'frosted',
            'checkerboard',
            'h-stripes',
            'v-stripes',
            'd-stripes',
            'spiral',
            'plasma',
            'holographic',
            'dim',
            'brighten',
            'contrast',
            'vintage',
            'face-visible',
            'noop',
        ]

        for effect_name in expected_effects:
            self.assertIn(effect_name, EFFECTS)

    def test_effects_parameters_structure(self) -> None:
        """Test that effects parameters are properly structured."""
        for effect_config in EFFECTS.values():
            if 'parameters' in effect_config:
                params = effect_config['parameters']
                # Check that parameter values are reasonable types
                assert isinstance(params, dict)  # noqa: S101
                for param_name, param_value in params.items():
                    self.assertIsInstance(param_name, str)
                    self.assertIn(type(param_value), [int, float, str])

    def test_stripe_variants(self) -> None:
        """Test that stripe variants are properly configured."""
        stripe_variants = ['h-stripes', 'v-stripes', 'd-stripes']
        expected_directions = ['horizontal', 'vertical', 'diagonal']

        for variant, direction in zip(
            stripe_variants, expected_directions, strict=False,
        ):
            self.assertIn(variant, EFFECTS)
            self.assertEqual(EFFECTS[variant]['function'], stripes)
            params = EFFECTS[variant]['parameters']
            assert isinstance(params, dict)  # noqa: S101
            self.assertEqual(
                params['direction'], direction,
            )

    def test_shine_variants(self) -> None:
        """Test that shine variants are properly configured."""
        shine_variants = ['shine', 'soft', 'gradient']

        for variant in shine_variants:
            self.assertIn(variant, EFFECTS)
            self.assertEqual(EFFECTS[variant]['function'], shine)


class TestLoadEffect(unittest.TestCase):
    """Test the load_effect function."""

    def test_load_effect_valid_name(self) -> None:
        """Test load_effect with valid effect name."""
        effect_func = load_effect('shine', 'default')
        self.assertIsNotNone(effect_func)
        self.assertTrue(callable(effect_func))

    def test_load_effect_invalid_name(self) -> None:
        """Test load_effect with invalid effect name."""
        effect_func = load_effect('nonexistent', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_empty_name(self) -> None:
        """Test load_effect with empty effect name."""
        effect_func = load_effect('', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_none_name(self) -> None:
        """Test load_effect with None as effect name."""
        effect_func = load_effect(None, 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_function_works(self) -> None:
        """Test that loaded effect function works correctly."""
        effect_func = load_effect('noop', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 150, 200)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        self.assertEqual(result, (test_rgb, test_rgb))

    def test_load_effect_applies_parameters(self) -> None:
        """Test that loaded effect applies configured parameters."""
        effect_func = load_effect('dim', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)

        # Should be dimmed according to default factor
        self.assertLess(sum(result[0]), sum(test_rgb))

    def test_load_effect_palette_override(self) -> None:
        """Test load_effect with palette-specific parameters."""
        # This tests the palette override mechanism even though
        # no palette overrides exist in current EFFECTS
        effect_func = load_effect('shine', 'custom')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)

        # Should still work even if palette doesn't exist
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_load_effect_all_configured_effects(self) -> None:
        """Test that all configured effects can be loaded."""
        for effect_name in EFFECTS:
            effect_func = load_effect(effect_name, 'default')
            self.assertIsNotNone(
                effect_func, f'Failed to load effect: {effect_name}',
            )
            self.assertTrue(callable(effect_func))


class TestParameterParsing(unittest.TestCase):
    """Test parameter parsing functions."""

    def test_parse_effect_parameters_empty(self) -> None:
        """Test parsing empty parameter string."""
        result = parse_effect_parameters('')
        self.assertEqual(result, {})

    def test_parse_effect_parameters_single_int(self) -> None:
        """Test parsing single integer parameter."""
        result = parse_effect_parameters('intensity=5')
        self.assertEqual(result, {'intensity': 5})

    def test_parse_effect_parameters_single_float(self) -> None:
        """Test parsing single float parameter."""
        result = parse_effect_parameters('factor=0.75')
        self.assertEqual(result, {'factor': 0.75})

    def test_parse_effect_parameters_single_string(self) -> None:
        """Test parsing single string parameter."""
        result = parse_effect_parameters('direction=horizontal')
        self.assertEqual(result, {'direction': 'horizontal'})

    def test_parse_effect_parameters_quoted_string(self) -> None:
        """Test parsing quoted string parameter."""
        result = parse_effect_parameters('mode="light mode"')
        self.assertEqual(result, {'mode': 'light mode'})

        result = parse_effect_parameters("mode='dark mode'")
        self.assertEqual(result, {'mode': 'dark mode'})

    def test_parse_effect_parameters_boolean(self) -> None:
        """Test parsing boolean parameters."""
        result = parse_effect_parameters('enabled=true')
        self.assertEqual(result, {'enabled': True})

        result = parse_effect_parameters('disabled=false')
        self.assertEqual(result, {'disabled': False})

    def test_parse_effect_parameters_multiple(self) -> None:
        """Test parsing multiple parameters."""
        result = parse_effect_parameters(
            'intensity=0.8,factor=1.5,direction=vertical',
        )
        expected = {
            'intensity': 0.8, 'factor': 1.5,
            'direction': 'vertical',
        }
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_mixed_types(self) -> None:
        """Test parsing mixed parameter types."""
        result = parse_effect_parameters(
            'intensity=0.8,frequency=3,enabled=true,mode=glossy',
        )
        expected = {
            'intensity': 0.8, 'frequency': 3,
            'enabled': True, 'mode': 'glossy',
        }
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_negative_numbers(self) -> None:
        """Test parsing negative numbers."""
        result = parse_effect_parameters('offset=-5,factor=-0.3')
        expected = {'offset': -5, 'factor': -0.3}
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_whitespace(self) -> None:
        """Test parsing with extra whitespace."""
        result = parse_effect_parameters('  intensity = 0.8 , factor = 1.5  ')
        expected = {'intensity': 0.8, 'factor': 1.5}
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_invalid_format(self) -> None:
        """Test parsing with invalid parameter format."""
        result = parse_effect_parameters('intensity,factor=1.5')
        expected = {'factor': 1.5}  # Invalid param is ignored
        self.assertEqual(result, expected)

    def test_parse_effect_name_simple(self) -> None:
        """Test parsing simple effect name without parameters."""
        name, params = parse_effect_name('shine')
        self.assertEqual(name, 'shine')
        self.assertEqual(params, {})

    def test_parse_effect_name_with_parameters(self) -> None:
        """Test parsing effect name with parameters."""
        name, params = parse_effect_name('shine(intensity=0.8)')
        self.assertEqual(name, 'shine')
        self.assertEqual(params, {'intensity': 0.8})

    def test_parse_effect_name_with_multiple_parameters(self) -> None:
        """Test parsing effect name with multiple parameters."""
        name, params = parse_effect_name('chrome(intensity=0.7,metallic=0.9)')
        self.assertEqual(name, 'chrome')
        self.assertEqual(params, {'intensity': 0.7, 'metallic': 0.9})

    def test_parse_effect_name_empty_parameters(self) -> None:
        """Test parsing effect name with empty parameter list."""
        name, params = parse_effect_name('neon()')
        self.assertEqual(name, 'neon')
        self.assertEqual(params, {})

    def test_parse_effect_name_whitespace(self) -> None:
        """Test parsing effect name with whitespace."""
        name, params = parse_effect_name('  gold( intensity=0.6 ) ')
        self.assertEqual(name, 'gold')
        self.assertEqual(params, {'intensity': 0.6})

    def test_parse_effect_name_invalid_syntax(self) -> None:
        """Test parsing effect name with invalid syntax triggers fallback."""
        # Test case with unmatched parentheses that won't match the regex
        name, params = parse_effect_name('shine(intensity=0.8')
        self.assertEqual(name, 'shine(intensity=0.8')  # Returns as-is
        self.assertEqual(params, {})

        # Test case with multiple unmatched parentheses
        name, params = parse_effect_name('effect((invalid')
        self.assertEqual(name, 'effect((invalid')
        self.assertEqual(params, {})


class TestEnhancedLoadEffect(unittest.TestCase):
    """Test enhanced load_effect function with chaining and parameters."""

    def test_load_effect_single_effect(self) -> None:
        """Test loading single effect without changes."""
        effect_func = load_effect('noop', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 150, 200)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        self.assertEqual(result, (test_rgb, test_rgb))

    def test_load_effect_single_with_custom_params(self) -> None:
        """Test loading single effect with custom parameters."""
        effect_func = load_effect('dim(factor=0.5)', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)

        # Should be dimmed by factor 0.5
        expected = (50, 50, 50)
        self.assertEqual(result[0], expected)

    def test_load_effect_chained_effects(self) -> None:
        """Test loading chained effects."""
        effect_func = load_effect('brighten|dim', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)

        # Should apply brighten then dim
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_load_effect_chained_with_params(self) -> None:
        """Test loading chained effects with custom parameters."""
        effect_func = load_effect(
            'brighten(factor=2.0)|dim(factor=0.5)',
            'default',
        )
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)

        # Should apply brighten factor 2.0 then dim factor 0.5
        # (100 * 2.0) * 0.5 = 100, so should return to original
        expected = (100, 100, 100)
        self.assertEqual(result[0], expected)

    def test_load_effect_multiple_chained(self) -> None:
        """Test loading multiple chained effects."""
        effect_func = load_effect('noop|noop|noop', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 150, 200)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        # Chain of noops should return original
        self.assertEqual(result, (test_rgb, test_rgb))

    def test_load_effect_invalid_in_chain(self) -> None:
        """Test loading chain with invalid effect."""
        effect_func = load_effect('shine|invalid_effect|dim', 'default')
        # Should still work with valid effects
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        # Should apply shine and dim, skipping invalid
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_load_effect_all_invalid_chain(self) -> None:
        """Test loading chain with all invalid effects."""
        effect_func = load_effect('invalid1|invalid2', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_empty_chain(self) -> None:
        """Test loading empty effect chain."""
        effect_func = load_effect('', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_complex_params(self) -> None:
        """Test loading effect with complex parameter combinations."""
        effect_func = load_effect(
            'd-stripes(frequency=3,intensity=0.6)',
            'default',
        )
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_load_effect_parameter_override(self) -> None:
        """Test that custom parameters override default ones."""
        # Load with very low intensity
        effect_func1 = load_effect('dim(factor=0.1)', 'default')
        assert effect_func1 is not None  # noqa: S101

        # Load with very high intensity
        effect_func2 = load_effect('dim(factor=0.9)', 'default')
        assert effect_func2 is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result1 = effect_func1(test_rgb, test_rgb, 0, 3)
        result2 = effect_func2(test_rgb, test_rgb, 0, 3)

        # Results should be different due to different factors
        self.assertNotEqual(result1, result2)

    def test_load_effect_whitespace_handling(self) -> None:
        """Test that whitespace in effect names is handled correctly."""
        effect_func = load_effect('  shine  |  dim  ', 'default')
        self.assertIsNotNone(effect_func)

    def test_load_single_effect_palette_specific_params(self) -> None:
        """Test load_single_effect with palette-specific parameters."""
        # Create a mock effect config with palette-specific parameters
        mock_effect_config = {
            'function': noop,
            'parameters': {'base_param': 1.0},
            'default': {'palette_param': 2.0},  # Palette-specific parameter
        }

        with patch.dict(
                'cubing_algs.display.effects.EFFECTS',
                {'test_effect': mock_effect_config},
        ):
            effect_func = load_single_effect('test_effect', {}, 'default')
            self.assertIsNotNone(effect_func)
            assert effect_func is not None  # noqa: S101

            # Test that the effect function works
            result = effect_func((100, 100, 100), (100, 100, 100), 0, 3)
            # noop returns unchanged
            self.assertEqual(result, ((100, 100, 100), (100, 100, 100)))

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_load_single_effect_palette_override_non_dict(self) -> None:
        """Test load_single_effect with non-dict palette override."""
        # Create a mock effect config with a non-dict palette override
        mock_effect_config = {
            'function': noop,
            'parameters': {'base_param': 1.0},
            'default': 'not_a_dict',  # Non-dict value that should be ignored
        }

        with patch.dict(
                'cubing_algs.display.effects.EFFECTS',
                {'test_effect': mock_effect_config},
        ):
            effect_func = load_single_effect('test_effect', {}, 'default')
            self.assertIsNotNone(effect_func)
            assert effect_func is not None  # noqa: S101

            # Test that the effect function works
            result = effect_func(
                (100, 100, 100),
                (100, 100, 100),
                0, 3,
            )
            # noop returns unchanged
            self.assertEqual(result, ((100, 100, 100), (100, 100, 100)))

    def test_load_effect_real_world_combinations(self) -> None:
        """Test real-world effect combinations."""
        combinations = [
            'shine(intensity=0.8)|chrome(metallic=0.7)',
            'gold(warmth=1.2)|glossy(intensity=0.9)',
            'checkerboard(intensity=0.3)|vintage(sepia=0.4)',
            'h-stripes(frequency=2)|rainbow',
            'dim(factor=0.8)|contrast(factor=1.5)|brighten(factor=1.1)',
        ]

        test_rgb = (128, 128, 128)
        for combination in combinations:
            effect_func = load_effect(combination, 'default')
            self.assertIsNotNone(effect_func, f'Failed to load: {combination}')
            assert effect_func is not None  # noqa: S101

            results = effect_func(test_rgb, test_rgb, 4, 3)
            for result in results:
                self.assertIsInstance(result, tuple)
                self.assertEqual(len(result), 3)
                for component in result:
                    self.assertGreaterEqual(component, 0)
                    self.assertLessEqual(component, 255)


class TestRegisterEffect(unittest.TestCase):
    """Test the register_effect function."""

    @staticmethod
    def tearDown() -> None:
        """Clean up registered effects after each test."""
        for name in list(EFFECTS):
            if name.startswith('custom_test_'):
                del EFFECTS[name]

    def test_register_effect_basic(self) -> None:
        """Test registering a custom effect."""
        config: EffectConfig = {'function': noop}
        register_effect('custom_test_basic', config)

        self.assertIn('custom_test_basic', EFFECTS)
        self.assertEqual(EFFECTS['custom_test_basic'], config)

    def test_register_effect_with_parameters(self) -> None:
        """Test registering a custom effect with parameters."""
        config: EffectConfig = {
            'function': shine,
            'parameters': {
                'intensity': 0.9,
                'facelet_mode': 'local',
                'position_mode': 'light',
            },
        }
        register_effect('custom_test_params', config)

        self.assertIn('custom_test_params', EFFECTS)
        self.assertEqual(EFFECTS['custom_test_params'], config)

    def test_register_effect_can_be_loaded(self) -> None:
        """Test that a registered effect can be loaded with load_effect."""
        config: EffectConfig = {
            'function': dim,
            'parameters': {'factor': 0.5},
        }
        register_effect('custom_test_loadable', config)

        effect_func = load_effect('custom_test_loadable', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        self.assertEqual(result, ((50, 50, 50), test_rgb))

    def test_register_effect_raises_on_duplicate_name(self) -> None:
        """Test that registering with an existing name raises exception."""
        config: EffectConfig = {'function': noop}
        with self.assertRaises(EffectAlreadyExistsError):
            register_effect('shine', config)

    def test_register_effect_error_message_contains_name(self) -> None:
        """Test that the error message contains the effect name."""
        config: EffectConfig = {'function': noop}

        with self.assertRaises(EffectAlreadyExistsError) as context:
            register_effect('neon', config)

        error_message = str(context.exception)
        self.assertIn('neon', error_message)
        self.assertIn('already exists', error_message.lower())

    def test_register_effect_raises_on_duplicate_builtin(self) -> None:
        """Test that built-in effect names cannot be overwritten."""
        builtin_names = ['shine', 'chrome', 'gold', 'noop']
        config: EffectConfig = {'function': noop}
        for name in builtin_names:
            with (
                self.subTest(name=name),
                self.assertRaises(EffectAlreadyExistsError),
            ):
                register_effect(name, config)

    def test_register_effect_with_custom_function(self) -> None:
        """Test registering an effect with a custom function."""
        def custom_effect(
            background_rgb: tuple[int, int, int],
            foreground_rgb: tuple[int, int, int],
            _facelet_index: int,
            _cube_size: int,
        ) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
            r, g, b = background_rgb
            return (
                min(255, r + 10),
                min(255, g + 10),
                min(255, b + 10),
            ), foreground_rgb

        config: EffectConfig = {'function': custom_effect}
        register_effect('custom_test_func', config)

        effect_func = load_effect('custom_test_func', 'default')
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        result = effect_func(
            (100, 100, 100),
            (100, 100, 100),
            0, 3,
        )
        self.assertEqual(result, ((110, 110, 110), (100, 100, 100)))

    def test_register_effect_usable_in_chain(self) -> None:
        """Test that a registered effect can be used in effect chains."""
        config: EffectConfig = {'function': noop}
        register_effect('custom_test_chain', config)

        effect_func = load_effect(
            'custom_test_chain|dim(factor=0.5)', 'default',
        )
        self.assertIsNotNone(effect_func)
        assert effect_func is not None  # noqa: S101

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, test_rgb, 0, 3)
        self.assertEqual(result, ((50, 50, 50), test_rgb))


class TestColorUtilities(unittest.TestCase):
    """Test color utility functions."""

    def test_linearize_srgb_zero(self) -> None:
        """Test linearize_srgb with zero input."""
        self.assertAlmostEqual(linearize_srgb(0), 0.0)

    def test_linearize_srgb_white(self) -> None:
        """Test linearize_srgb with max input."""
        self.assertAlmostEqual(linearize_srgb(255), 1.0, places=2)

    def test_linearize_srgb_below_threshold(self) -> None:
        """Test linearize_srgb with value in linear region."""
        # 0.04045 * 255 ≈ 10.3, so value=10 is below threshold
        result = linearize_srgb(10)
        self.assertAlmostEqual(result, (10 / 255) / 12.92, places=6)

    def test_linearize_srgb_above_threshold(self) -> None:
        """Test linearize_srgb with value in gamma region."""
        result = linearize_srgb(128)
        v = 128 / 255
        expected = ((v + 0.055) / 1.055) ** 2.4
        self.assertAlmostEqual(result, expected, places=6)

    def test_relative_luminance_black(self) -> None:
        """Test relative luminance of black is 0."""
        self.assertAlmostEqual(relative_luminance((0, 0, 0)), 0.0)

    def test_relative_luminance_white(self) -> None:
        """Test relative luminance of white is ~1."""
        result = relative_luminance((255, 255, 255))
        self.assertAlmostEqual(result, 1.0, places=2)

    def test_relative_luminance_green_dominates(self) -> None:
        """Test that green channel contributes most to luminance."""
        lum_r = relative_luminance((255, 0, 0))
        lum_g = relative_luminance((0, 255, 0))
        lum_b = relative_luminance((0, 0, 255))
        self.assertGreater(lum_g, lum_r)
        self.assertGreater(lum_g, lum_b)

    def test_contrast_ratio_same_luminance(self) -> None:
        """Test contrast ratio of identical luminances is 1."""
        self.assertAlmostEqual(contrast_ratio(0.5, 0.5), 1.0, places=2)

    def test_contrast_ratio_black_white(self) -> None:
        """Test contrast ratio of black vs white is 21."""
        self.assertAlmostEqual(contrast_ratio(0.0, 1.0), 21.0)

    def test_contrast_ratio_order_independent(self) -> None:
        """Test contrast ratio is the same regardless of argument order."""
        self.assertEqual(
            contrast_ratio(0.2, 0.8),
            contrast_ratio(0.8, 0.2),
        )

    def test_rgb_to_hls_red(self) -> None:
        """Test RGB to HLS conversion for pure red."""
        hue, lit, sat = rgb_to_hls((255, 0, 0))
        self.assertAlmostEqual(hue, 0.0)
        self.assertAlmostEqual(lit, 0.5)
        self.assertAlmostEqual(sat, 1.0)

    def test_rgb_to_hls_gray(self) -> None:
        """Test RGB to HLS conversion for gray (zero saturation)."""
        _, lit, sat = rgb_to_hls((128, 128, 128))
        self.assertAlmostEqual(sat, 0.0)
        self.assertAlmostEqual(lit, 128 / 255, places=2)

    def test_hls_to_rgb_red(self) -> None:
        """Test HLS to RGB conversion for pure red."""
        self.assertEqual(hls_to_rgb(0.0, 0.5, 1.0), (255, 0, 0))

    def test_hls_to_rgb_clamping(self) -> None:
        """Test HLS to RGB clamps to 0-255."""
        result = hls_to_rgb(0.0, 1.5, 1.0)
        for c in result:
            self.assertGreaterEqual(c, 0)
            self.assertLessEqual(c, 255)

    def test_hls_rgb_roundtrip(self) -> None:
        """Test HLS → RGB → HLS roundtrip preserves values."""
        original = (200, 100, 50)
        hue, lit, sat = rgb_to_hls(original)
        result = hls_to_rgb(hue, lit, sat)
        for orig, res in zip(original, result, strict=True):
            self.assertAlmostEqual(orig, res, delta=2)


class TestContrastAndHiddenFontEffects(RGBTestCase):
    """Test contrast_font and hidden_font effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.fg: tuple[int, int, int] = (127, 127, 127)
        self.idx = 0
        self.size = 3

    def test_contrast_font_sufficient_contrast(self) -> None:
        """Test contrast_font returns unchanged when ok."""
        bg = (0, 0, 0)
        fg = (255, 255, 255)
        result_bg, result_fg = contrast_font(
            bg, fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertEqual(result_fg, fg)

    def test_contrast_font_adjusts_low_contrast(self) -> None:
        """Test contrast_font adjusts fg when contrast low."""
        bg = (30, 30, 30)
        fg = (40, 40, 40)
        result_bg, result_fg = contrast_font(
            bg, fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertGreater(sum(result_fg), sum(fg))

    def test_contrast_font_light_background(self) -> None:
        """Test contrast_font toward black on light bg."""
        bg = (240, 240, 240)
        fg = (220, 220, 220)
        result_bg, result_fg = contrast_font(
            bg, fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertLess(sum(result_fg), sum(fg))

    def test_contrast_font_custom_ratio(self) -> None:
        """Test contrast_font with custom min ratio."""
        bg = (100, 100, 100)
        fg = (120, 120, 120)
        _, result_fg = contrast_font(
            bg, fg, self.idx, self.size, factor=7.0,
        )
        self.validate_rgb_output(result_fg)

    def test_contrast_font_achieves_target_ratio(self) -> None:
        """Test adjusted fg achieves target contrast."""
        bg = (50, 50, 50)
        fg = (60, 60, 60)
        min_ratio = 4.5
        _, result_fg = contrast_font(
            bg, fg, self.idx, self.size, factor=min_ratio,
        )
        bg_lum = relative_luminance(bg)
        fg_lum = relative_luminance(result_fg)
        actual = contrast_ratio(bg_lum, fg_lum)
        self.assertGreaterEqual(actual, min_ratio - 0.1)

    def test_hidden_font_returns_bg_as_fg(self) -> None:
        """Test hidden_font sets fg equal to bg."""
        bg = (100, 200, 50)
        result_bg, result_fg = hidden_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertEqual(result_fg, bg)


class TestBWAndComplementFontEffects(RGBTestCase):
    """Test b_w_font and complement_font effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.fg: tuple[int, int, int] = (127, 127, 127)
        self.idx = 0
        self.size = 3

    def test_b_w_font_dark_gives_white(self) -> None:
        """Test b_w_font returns white fg on dark bg."""
        _, result_fg = b_w_font(
            (20, 20, 20), self.fg, self.idx, self.size,
        )
        self.assertEqual(result_fg, (255, 255, 255))

    def test_b_w_font_light_gives_black(self) -> None:
        """Test b_w_font returns black fg on light bg."""
        _, result_fg = b_w_font(
            (230, 230, 230), self.fg, self.idx, self.size,
        )
        self.assertEqual(result_fg, (0, 0, 0))

    def test_b_w_font_preserves_background(self) -> None:
        """Test b_w_font does not modify the background."""
        bg = (200, 50, 30)
        result_bg, _ = b_w_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)

    def test_complement_font_basic(self) -> None:
        """Test complement_font returns RGB complement."""
        bg = (100, 150, 200)
        result_bg, result_fg = complement_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertEqual(result_fg, (155, 105, 55))

    def test_complement_font_black(self) -> None:
        """Test complement of black is white."""
        _, result_fg = complement_font(
            (0, 0, 0), self.fg, self.idx, self.size,
        )
        self.assertEqual(result_fg, (255, 255, 255))

    def test_complement_font_white(self) -> None:
        """Test complement of white is black."""
        _, result_fg = complement_font(
            (255, 255, 255), self.fg, self.idx, self.size,
        )
        self.assertEqual(result_fg, (0, 0, 0))


class TestShadeAndSetFontEffects(RGBTestCase):
    """Test shade_font and set_font effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.fg: tuple[int, int, int] = (127, 127, 127)
        self.idx = 0
        self.size = 3

    def test_shade_font_dark_bg_lightens(self) -> None:
        """Test shade_font lightens fg on dark bg."""
        dark_bg = (20, 20, 20)
        _, result_fg = shade_font(
            dark_bg, self.fg, self.idx, self.size,
        )
        self.assertGreater(sum(result_fg), sum(dark_bg))

    def test_shade_font_light_bg_darkens(self) -> None:
        """Test shade_font darkens fg on light bg."""
        light_bg = (230, 230, 230)
        _, result_fg = shade_font(
            light_bg, self.fg, self.idx, self.size,
        )
        self.assertLess(sum(result_fg), sum(light_bg))

    def test_shade_font_custom_factor(self) -> None:
        """Test shade_font with custom blend factor."""
        _, result_fg = shade_font(
            (20, 20, 20), self.fg, self.idx, self.size,
            factor=0.8,
        )
        self.validate_rgb_output(result_fg)

    def test_shade_font_preserves_background(self) -> None:
        """Test shade_font does not modify the background."""
        bg = (200, 50, 30)
        result_bg, _ = shade_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)

    def test_set_font_default_color(self) -> None:
        """Test set_font with default color parameter."""
        bg = (100, 100, 100)
        result_bg, result_fg = set_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertEqual(result_fg, (127, 127, 127))

    def test_set_font_custom_color(self) -> None:
        """Test set_font with custom color string."""
        bg = (100, 100, 100)
        _, result_fg = set_font(
            bg, self.fg, self.idx, self.size,
            color='255;0;128',
        )
        self.assertEqual(result_fg, (255, 0, 128))


class TestHueShiftFontEffects(RGBTestCase):
    """Test hue_shift_font, warm_font, and cool_font effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.fg: tuple[int, int, int] = (127, 127, 127)
        self.idx = 0
        self.size = 3

    def test_hue_shift_font_half_rotation(self) -> None:
        """Test hue_shift_font shifts hue by 180 degrees."""
        bg = (255, 0, 0)
        result_bg, result_fg = hue_shift_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.validate_rgb_output(result_fg)
        self.assertGreater(result_fg[2], result_fg[0])

    def test_hue_shift_font_custom_factor(self) -> None:
        """Test hue_shift_font with custom shift."""
        bg = (255, 0, 0)
        _, result_fg = hue_shift_font(
            bg, self.fg, self.idx, self.size, factor=0.333,
        )
        self.validate_rgb_output(result_fg)

    def test_warm_font_produces_warm_hue(self) -> None:
        """Test warm_font shifts toward orange/warm tones."""
        bg = (0, 0, 255)
        result_bg, result_fg = warm_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.validate_rgb_output(result_fg)

    def test_warm_font_inverts_lightness(self) -> None:
        """Test warm_font inverts lightness."""
        bg = (20, 20, 20)
        _, result_fg = warm_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertGreater(sum(result_fg), sum(bg))

    def test_cool_font_produces_cool_hue(self) -> None:
        """Test cool_font shifts toward blue/cool tones."""
        bg = (255, 0, 0)
        result_bg, result_fg = cool_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.validate_rgb_output(result_fg)

    def test_cool_font_inverts_lightness(self) -> None:
        """Test cool_font inverts lightness."""
        bg = (200, 200, 200)
        _, result_fg = cool_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertLess(sum(result_fg), sum(bg))


class TestLumaAndGrayscaleFontEffects(RGBTestCase):
    """Test invert_luma_font and grayscale_font effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.fg: tuple[int, int, int] = (127, 127, 127)
        self.idx = 0
        self.size = 3

    def test_invert_luma_font_dark_bg(self) -> None:
        """Test invert_luma_font light fg on dark bg."""
        bg = (30, 30, 30)
        result_bg, result_fg = invert_luma_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertGreater(sum(result_fg), sum(bg))

    def test_invert_luma_font_light_bg(self) -> None:
        """Test invert_luma_font dark fg on light bg."""
        bg = (220, 220, 220)
        _, result_fg = invert_luma_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertLess(sum(result_fg), sum(bg))

    def test_grayscale_font_produces_gray(self) -> None:
        """Test grayscale_font produces equal RGB channels."""
        bg = (200, 100, 50)
        result_bg, result_fg = grayscale_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.assertEqual(result_fg[0], result_fg[1])
        self.assertEqual(result_fg[1], result_fg[2])

    def test_grayscale_font_bt601_weights(self) -> None:
        """Test grayscale_font uses BT.601 luma weights."""
        bg = (200, 100, 50)
        _, result_fg = grayscale_font(
            bg, self.fg, self.idx, self.size,
        )
        gray = int(0.299 * 200 + 0.587 * 100 + 0.114 * 50)
        self.assertEqual(result_fg, (gray, gray, gray))


class TestColorModFontEffects(RGBTestCase):
    """Test pastel_font, vivid_font, and gradient_font effects."""

    def setUp(self) -> None:
        """Set up common test data."""
        self.fg: tuple[int, int, int] = (127, 127, 127)
        self.idx = 0
        self.size = 3

    def test_pastel_font_basic(self) -> None:
        """Test pastel_font produces desaturated output."""
        bg = (255, 0, 0)
        result_bg, result_fg = pastel_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.validate_rgb_output(result_fg)

    def test_pastel_font_custom_params(self) -> None:
        """Test pastel_font with custom params."""
        bg = (0, 200, 100)
        _, result_fg = pastel_font(
            bg, self.fg, self.idx, self.size,
            saturation=0.5, lighten=0.9,
        )
        self.validate_rgb_output(result_fg)

    def test_vivid_font_maximizes_saturation(self) -> None:
        """Test vivid_font produces saturated output."""
        bg = (200, 100, 100)
        result_bg, result_fg = vivid_font(
            bg, self.fg, self.idx, self.size,
        )
        self.assertEqual(result_bg, bg)
        self.validate_rgb_output(result_fg)

    def test_vivid_font_custom_saturation(self) -> None:
        """Test vivid_font with custom saturation."""
        bg = (150, 100, 50)
        _, result_fg = vivid_font(
            bg, self.fg, self.idx, self.size, saturation=0.6,
        )
        self.validate_rgb_output(result_fg)

    def test_gradient_font_varies_by_position(self) -> None:
        """Test gradient_font differs at positions."""
        bg = (200, 50, 50)
        _, fg_pos0 = gradient_font(bg, self.fg, 0, self.size)
        _, fg_pos8 = gradient_font(bg, self.fg, 8, self.size)
        self.validate_rgb_output(fg_pos0)
        self.validate_rgb_output(fg_pos8)
        self.assertNotEqual(fg_pos0, fg_pos8)

    def test_gradient_font_custom_bounds(self) -> None:
        """Test gradient_font with custom lightness."""
        bg = (100, 100, 200)
        _, result_fg = gradient_font(
            bg, self.fg, 4, self.size,
            lighten=0.1, darken=0.9,
        )
        self.validate_rgb_output(result_fg)

    def test_gradient_font_preserves_background(self) -> None:
        """Test gradient_font keeps background unchanged."""
        bg = (100, 150, 200)
        result_bg, _ = gradient_font(
            bg, self.fg, 0, self.size,
        )
        self.assertEqual(result_bg, bg)


class TestFontEffectsConfiguration(unittest.TestCase):
    """Test that font effects are present in the EFFECTS dictionary."""

    def test_font_effects_in_effects_dict(self) -> None:
        """Test all font effects are registered in EFFECTS."""
        font_effects = [
            'contrast-font',
            'hidden-font',
            'complement-font',
            'shade-font',
            'b-w-font',
            'set-font',
            'hue-shift-font',
            'analogous-font',
            'warm-font',
            'cool-font',
            'invert-luma-font',
            'grayscale-font',
            'pastel-font',
            'vivid-font',
            'gradient-font',
        ]
        for name in font_effects:
            self.assertIn(name, EFFECTS, f'Missing font effect: {name}')

    def test_font_effects_loadable(self) -> None:
        """Test all font effects can be loaded and executed."""
        font_effects = [
            'contrast-font', 'hidden-font', 'complement-font',
            'shade-font', 'b-w-font', 'set-font', 'hue-shift-font',
            'analogous-font', 'warm-font', 'cool-font',
            'invert-luma-font', 'grayscale-font', 'pastel-font',
            'vivid-font', 'gradient-font',
        ]
        bg = (100, 100, 100)
        fg = (50, 50, 50)
        for name in font_effects:
            effect_func = load_effect(name, 'default')
            self.assertIsNotNone(effect_func, f'Failed to load: {name}')
            assert effect_func is not None  # noqa: S101
            result = effect_func(bg, fg, 0, 3)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

    def test_analogous_font_small_shift(self) -> None:
        """Test analogous-font uses a small hue shift."""
        params = EFFECTS['analogous-font'].get('parameters', {})
        assert isinstance(params, dict)  # noqa: S101
        # 0.083 ≈ 30 degrees
        self.assertAlmostEqual(  # type: ignore[misc]
            params['factor'], 0.083, places=3,  # type: ignore[arg-type]
        )
