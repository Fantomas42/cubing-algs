import unittest
from unittest.mock import patch

from cubing_algs.effects import EFFECTS
from cubing_algs.effects import FACE_POSITIONS
from cubing_algs.effects import brighten
from cubing_algs.effects import checkerboard
from cubing_algs.effects import chrome
from cubing_algs.effects import contrast
from cubing_algs.effects import copper
from cubing_algs.effects import diamond
from cubing_algs.effects import dim
from cubing_algs.effects import face_visible
from cubing_algs.effects import frosted
from cubing_algs.effects import get_position_factor
from cubing_algs.effects import global_light_position_factor
from cubing_algs.effects import glossy
from cubing_algs.effects import gold
from cubing_algs.effects import holographic
from cubing_algs.effects import load_effect
from cubing_algs.effects import load_single_effect
from cubing_algs.effects import matte
from cubing_algs.effects import neon
from cubing_algs.effects import noop
from cubing_algs.effects import parse_effect_name
from cubing_algs.effects import parse_effect_parameters
from cubing_algs.effects import plasma
from cubing_algs.effects import rainbow
from cubing_algs.effects import shine
from cubing_algs.effects import silver
from cubing_algs.effects import spiral
from cubing_algs.effects import stripes
from cubing_algs.effects import vintage


class TestPositioningFunctions(unittest.TestCase):
    """Test positioning and utility functions."""

    def test_face_positions_constant(self):
        """Test FACE_POSITIONS constant has correct structure."""
        self.assertEqual(len(FACE_POSITIONS), 6)
        for face_index in range(6):
            self.assertIn(face_index, FACE_POSITIONS)
            self.assertEqual(len(FACE_POSITIONS[face_index]), 2)
            self.assertIsInstance(FACE_POSITIONS[face_index][0], int)
            self.assertIsInstance(FACE_POSITIONS[face_index][1], int)

    def test_global_light_position_factor_basic(self):
        """Test global_light_position_factor with basic inputs."""
        result = global_light_position_factor(0, 3)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_global_light_position_factor_different_cube_sizes(self):
        """Test global_light_position_factor with different cube sizes."""
        for cube_size in [2, 3, 4, 5]:
            result = global_light_position_factor(0, cube_size)
            self.assertIsInstance(result, float)
            self.assertGreaterEqual(result, 0.0)
            self.assertLessEqual(result, 1.0)

    def test_global_light_position_factor_all_faces(self):
        """Test global_light_position_factor across all faces."""
        cube_size = 3
        face_size = cube_size * cube_size

        for face_index in range(6):
            for local_index in range(face_size):
                facelet_index = face_index * face_size + local_index
                result = global_light_position_factor(facelet_index, cube_size)
                self.assertIsInstance(result, float)
                self.assertGreaterEqual(result, 0.0)
                self.assertLessEqual(result, 1.0)

    def test_global_light_position_factor_edge_cases(self):
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

    def test_get_position_factor_default_parameters(self):
        """Test get_position_factor with default parameters."""
        result = get_position_factor(0, 3)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_get_position_factor_facelet_modes(self):
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

    def test_get_position_factor_position_modes(self):
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

    def test_get_position_factor_mode_combinations(self):
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
            result = get_position_factor(facelet_index, cube_size, **kwargs)
            self.assertIsInstance(result, float)
            self.assertGreaterEqual(result, 0.0)


class TestBasicEffects(unittest.TestCase):
    """Test basic lighting and surface effects."""

    def setUp(self):
        """Set up common test data."""
        self.test_rgb = (128, 64, 192)
        self.facelet_index = 4
        self.cube_size = 3

    def _validate_rgb_output(self, rgb):
        """Helper to validate RGB output is properly clamped."""
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        for component in rgb:
            self.assertIsInstance(component, int)
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)

    def test_shine_basic(self):
        """Test shine effect with basic parameters."""
        result = shine(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_shine_with_intensity(self):
        """Test shine effect with different intensity values."""
        intensities = [0.0, 0.3, 0.5, 0.8, 1.0]
        for intensity in intensities:
            result = shine(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self._validate_rgb_output(result)

    def test_neon_basic(self):
        """Test neon effect with basic parameters."""
        result = neon(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_neon_with_parameters(self):
        """Test neon effect with different parameters."""
        result = neon(
            self.test_rgb,
            self.facelet_index,
            self.cube_size,
            intensity=0.8,
            saturation=1.5,
        )
        self._validate_rgb_output(result)

    def test_neon_black_input(self):
        """Test neon effect with black input (edge case)."""
        black_rgb = (0, 0, 0)
        result = neon(black_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_chrome_basic(self):
        """Test chrome effect with basic parameters."""
        result = chrome(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_chrome_with_parameters(self):
        """Test chrome effect with different parameters."""
        result = chrome(
            self.test_rgb,
            self.facelet_index,
            self.cube_size,
            intensity=0.7,
            metallic=0.8,
        )
        self._validate_rgb_output(result)

    def test_gold_basic(self):
        """Test gold effect with basic parameters."""
        result = gold(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_gold_with_warmth(self):
        """Test gold effect with different warmth values."""
        warmths = [0.0, 0.5, 1.0, 1.5]
        for warmth in warmths:
            result = gold(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                warmth=warmth,
            )
            self._validate_rgb_output(result)

    def test_silver_basic(self):
        """Test silver effect with basic parameters."""
        result = silver(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_silver_with_intensity(self):
        """Test silver effect with different intensity values."""
        intensities = [0.1, 0.5, 0.9]
        for intensity in intensities:
            result = silver(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self._validate_rgb_output(result)

    def test_copper_basic(self):
        """Test copper effect with basic parameters."""
        result = copper(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_copper_with_parameters(self):
        """Test copper effect with different parameters."""
        result = copper(
            self.test_rgb,
            self.facelet_index,
            self.cube_size,
            intensity=0.8,
            warmth=1.2,
        )
        self._validate_rgb_output(result)


class TestPatternEffects(unittest.TestCase):
    """Test pattern-based effects."""

    def setUp(self):
        """Set up common test data."""
        self.test_rgb = (100, 150, 200)
        self.cube_size = 3

    def _validate_rgb_output(self, rgb):
        """Helper to validate RGB output is properly clamped."""
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        for component in rgb:
            self.assertIsInstance(component, int)
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)

    def test_diamond_sparkle_positions(self):
        """Test diamond effect at sparkle positions."""
        # Test specific sparkle positions
        sparkle_positions = [(0, 0), (1, 1), (2, 2), (0, 2), (2, 0)]

        for row, col in sparkle_positions:
            facelet_index = row * self.cube_size + col
            result = diamond(self.test_rgb, facelet_index, self.cube_size)
            self._validate_rgb_output(result)
            # Sparkle positions should be brighter
            self.assertGreater(sum(result), sum(self.test_rgb))

    def test_diamond_non_sparkle_positions(self):
        """Test diamond effect at non-sparkle positions."""
        # Test non-sparkle position
        facelet_index = 1 * self.cube_size + 0  # Position (1, 0)
        result = diamond(self.test_rgb, facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_rainbow_basic(self):
        """Test rainbow effect with basic parameters."""
        for facelet_index in range(9):  # Test all positions on a 3x3 face
            result = rainbow(self.test_rgb, facelet_index, self.cube_size)
            self._validate_rgb_output(result)

    def test_checkerboard_pattern(self):
        """Test checkerboard effect creates alternating pattern."""
        results = []
        for facelet_index in range(9):  # Test all positions on a 3x3 face
            result = checkerboard(self.test_rgb, facelet_index, self.cube_size)
            self._validate_rgb_output(result)
            results.append(result)

        # Check that adjacent positions have different brightness
        # Position (0,0) and (0,1) should be different
        pos_00 = checkerboard(self.test_rgb, 0, self.cube_size)
        pos_01 = checkerboard(self.test_rgb, 1, self.cube_size)
        self.assertNotEqual(pos_00, pos_01)

    def test_checkerboard_with_intensity(self):
        """Test checkerboard effect with different intensities."""
        intensities = [0.2, 0.5, 0.8]
        for intensity in intensities:
            result = checkerboard(
                self.test_rgb, 0, self.cube_size, intensity=intensity,
            )
            self._validate_rgb_output(result)

    def test_stripes_directions(self):
        """Test stripes effect with different directions."""
        directions = ['horizontal', 'vertical', 'diagonal']
        for direction in directions:
            result = stripes(
                self.test_rgb, 4, self.cube_size, direction=direction,
            )
            self._validate_rgb_output(result)

    def test_stripes_with_parameters(self):
        """Test stripes effect with different parameters."""
        result = stripes(
            self.test_rgb,
            4,
            self.cube_size,
            direction='horizontal',
            frequency=3,
            intensity=0.6,
        )
        self._validate_rgb_output(result)

    def test_spiral_basic(self):
        """Test spiral effect with basic parameters."""
        for facelet_index in range(9):
            result = spiral(self.test_rgb, facelet_index, self.cube_size)
            self._validate_rgb_output(result)

    def test_spiral_with_intensity(self):
        """Test spiral effect with different intensities."""
        intensities = [0.1, 0.5, 0.9]
        for intensity in intensities:
            result = spiral(
                self.test_rgb, 4, self.cube_size, intensity=intensity,
            )
            self._validate_rgb_output(result)

    def test_plasma_basic(self):
        """Test plasma effect with basic parameters."""
        for facelet_index in range(9):
            result = plasma(self.test_rgb, facelet_index, self.cube_size)
            self._validate_rgb_output(result)

    def test_plasma_with_intensity(self):
        """Test plasma effect with different intensities."""
        intensities = [0.2, 0.4, 0.8]
        for intensity in intensities:
            result = plasma(
                self.test_rgb, 4, self.cube_size, intensity=intensity,
            )
            self._validate_rgb_output(result)


class TestSurfaceEffects(unittest.TestCase):
    """Test surface finish effects."""

    def setUp(self):
        """Set up common test data."""
        self.test_rgb = (120, 80, 160)
        self.facelet_index = 4
        self.cube_size = 3

    def _validate_rgb_output(self, rgb):
        """Helper to validate RGB output is properly clamped."""
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        for component in rgb:
            self.assertIsInstance(component, int)
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)

    def test_matte_basic(self):
        """Test matte effect with basic parameters."""
        result = matte(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)
        # Matte should reduce brightness
        self.assertLessEqual(sum(result), sum(self.test_rgb))

    def test_matte_ignores_position(self):
        """Test that matte effect ignores facelet position."""
        result1 = matte(self.test_rgb, 0, self.cube_size)
        result2 = matte(self.test_rgb, 8, self.cube_size)
        self.assertEqual(result1, result2)

    def test_matte_with_reduction(self):
        """Test matte effect with different reduction values."""
        reductions = [0.1, 0.3, 0.5, 0.8]
        for reduction in reductions:
            result = matte(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                reduction=reduction,
            )
            self._validate_rgb_output(result)

    def test_glossy_basic(self):
        """Test glossy effect with basic parameters."""
        result = glossy(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_glossy_with_intensity(self):
        """Test glossy effect with different intensities."""
        intensities = [0.2, 0.5, 1.0]
        for intensity in intensities:
            result = glossy(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self._validate_rgb_output(result)

    def test_frosted_basic(self):
        """Test frosted effect with basic parameters."""
        result = frosted(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_frosted_with_intensity(self):
        """Test frosted effect with different intensities."""
        intensities = [0.1, 0.4, 0.7]
        for intensity in intensities:
            result = frosted(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self._validate_rgb_output(result)

    def test_holographic_basic(self):
        """Test holographic effect with basic parameters."""
        result = holographic(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_holographic_with_intensity(self):
        """Test holographic effect with different intensities."""
        intensities = [0.3, 0.6, 0.9]
        for intensity in intensities:
            result = holographic(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                intensity=intensity,
            )
            self._validate_rgb_output(result)


class TestAdjustmentEffects(unittest.TestCase):
    """Test color adjustment effects."""

    def setUp(self):
        """Set up common test data."""
        self.test_rgb = (128, 128, 128)
        self.facelet_index = 4
        self.cube_size = 3

    def _validate_rgb_output(self, rgb):
        """Helper to validate RGB output is properly clamped."""
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        for component in rgb:
            self.assertIsInstance(component, int)
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)

    def test_dim_basic(self):
        """Test dim effect with basic parameters."""
        result = dim(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)
        # Dim should reduce brightness
        self.assertLessEqual(sum(result), sum(self.test_rgb))

    def test_dim_ignores_position(self):
        """Test that dim effect ignores facelet position."""
        result1 = dim(self.test_rgb, 0, self.cube_size)
        result2 = dim(self.test_rgb, 8, self.cube_size)
        self.assertEqual(result1, result2)

    def test_dim_with_factor(self):
        """Test dim effect with different factors."""
        factors = [0.1, 0.5, 0.7, 0.9]
        for factor in factors:
            result = dim(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                factor=factor,
            )
            self._validate_rgb_output(result)

    def test_brighten_basic(self):
        """Test brighten effect with basic parameters."""
        result = brighten(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)
        # Brighten should increase brightness
        self.assertGreaterEqual(sum(result), sum(self.test_rgb))

    def test_brighten_ignores_position(self):
        """Test that brighten effect ignores facelet position."""
        result1 = brighten(self.test_rgb, 0, self.cube_size)
        result2 = brighten(self.test_rgb, 8, self.cube_size)
        self.assertEqual(result1, result2)

    def test_brighten_with_factor(self):
        """Test brighten effect with different factors."""
        factors = [1.1, 1.3, 1.5, 2.0]
        for factor in factors:
            result = brighten(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                factor=factor,
            )
            self._validate_rgb_output(result)

    def test_contrast_basic(self):
        """Test contrast effect with basic parameters."""
        result = contrast(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_contrast_ignores_position(self):
        """Test that contrast effect ignores facelet position."""
        result1 = contrast(self.test_rgb, 0, self.cube_size)
        result2 = contrast(self.test_rgb, 8, self.cube_size)
        self.assertEqual(result1, result2)

    def test_contrast_with_factor(self):
        """Test contrast effect with different factors."""
        factors = [0.5, 1.0, 1.5, 2.0]
        for factor in factors:
            result = contrast(
                self.test_rgb,
                self.facelet_index,
                self.cube_size,
                factor=factor,
            )
            self._validate_rgb_output(result)

    def test_contrast_with_different_colors(self):
        """Test contrast effect with colors above and below middle gray."""
        # Test with bright color
        bright_rgb = (200, 200, 200)
        result_bright = contrast(bright_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result_bright)

        # Test with dark color
        dark_rgb = (50, 50, 50)
        result_dark = contrast(dark_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result_dark)

    def test_vintage_basic(self):
        """Test vintage effect with basic parameters."""
        result = vintage(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_vintage_ignores_position(self):
        """Test that vintage effect ignores facelet position."""
        result1 = vintage(self.test_rgb, 0, self.cube_size)
        result2 = vintage(self.test_rgb, 8, self.cube_size)
        self.assertEqual(result1, result2)

    def test_vintage_with_parameters(self):
        """Test vintage effect with different parameters."""
        result = vintage(
            self.test_rgb,
            self.facelet_index,
            self.cube_size,
            sepia=0.8,
            desaturation=0.5,
        )
        self._validate_rgb_output(result)

    def test_face_visible_basic(self):
        """Test face_visible effect with basic parameters."""
        result = face_visible(self.test_rgb, self.facelet_index, self.cube_size)
        self._validate_rgb_output(result)

    def test_face_visible_front_vs_back(self):
        """Test face_visible effect treats front and back faces differently."""
        # Front face (face index 0, 1, 2)
        front_facelet = 4  # Face 0
        result_front = face_visible(
            self.test_rgb, front_facelet, self.cube_size,
        )

        # Back face (face index 3, 4, 5)
        back_facelet = 3 * 9 + 4  # Face 3
        result_back = face_visible(self.test_rgb, back_facelet, self.cube_size)

        self._validate_rgb_output(result_front)
        self._validate_rgb_output(result_back)

        # Front faces should be brighter
        self.assertGreater(sum(result_front), sum(result_back))


class TestUtilityEffects(unittest.TestCase):
    """Test utility effects."""

    def setUp(self):
        """Set up common test data."""
        self.test_rgb = (100, 150, 200)
        self.facelet_index = 4
        self.cube_size = 3

    def test_noop_returns_unchanged(self):
        """Test that noop effect returns input unchanged."""
        result = noop(self.test_rgb, self.facelet_index, self.cube_size)
        self.assertEqual(result, self.test_rgb)

    def test_noop_ignores_all_parameters(self):
        """Test that noop effect ignores all parameters."""
        result1 = noop(self.test_rgb, 0, 2)
        result2 = noop(
            self.test_rgb, 100, 10, intensity=5.0, random_param='test',
        )
        self.assertEqual(result1, self.test_rgb)
        self.assertEqual(result2, self.test_rgb)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def _validate_rgb_output(self, rgb):
        """Helper to validate RGB output is properly clamped."""
        self.assertIsInstance(rgb, tuple)
        self.assertEqual(len(rgb), 3)
        for component in rgb:
            self.assertIsInstance(component, int)
            self.assertGreaterEqual(component, 0)
            self.assertLessEqual(component, 255)

    def test_rgb_clamping_white(self):
        """Test RGB clamping with white input."""
        white_rgb = (255, 255, 255)
        effects_to_test = [shine, neon, chrome, gold, silver, copper, brighten]

        for effect in effects_to_test:
            result = effect(white_rgb, 0, 3)
            self._validate_rgb_output(result)

    def test_rgb_clamping_black(self):
        """Test RGB clamping with black input."""
        black_rgb = (0, 0, 0)
        effects_to_test = [shine, neon, chrome, gold, silver, copper, dim]

        for effect in effects_to_test:
            result = effect(black_rgb, 0, 3)
            self._validate_rgb_output(result)

    def test_different_cube_sizes(self):
        """Test effects with different cube sizes."""
        test_rgb = (128, 64, 192)
        cube_sizes = [1, 2, 3, 4, 5, 10]

        for cube_size in cube_sizes:
            for facelet_index in range(cube_size * cube_size):
                result = shine(test_rgb, facelet_index, cube_size)
                self._validate_rgb_output(result)

    def test_large_facelet_indices(self):
        """Test effects with large facelet indices within valid range."""
        test_rgb = (100, 100, 100)
        cube_size = 3
        # Test with indices from different faces but within valid range
        large_indices = [27, 45, 53]  # Face 3, 5, and last valid index

        for facelet_index in large_indices:
            result = diamond(test_rgb, facelet_index, cube_size)
            self._validate_rgb_output(result)

    def test_extreme_parameter_values(self):
        """Test effects with extreme parameter values."""
        test_rgb = (128, 128, 128)

        # Test with very high intensity
        result = shine(test_rgb, 0, 3, intensity=10.0)
        self._validate_rgb_output(result)

        # Test with zero intensity
        result = shine(test_rgb, 0, 3, intensity=0.0)
        self._validate_rgb_output(result)

        # Test with negative values
        result = dim(test_rgb, 0, 3, factor=-1.0)
        self._validate_rgb_output(result)

    def test_minimum_cube_size(self):
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
            result = effect(test_rgb, facelet_index, cube_size)
            self._validate_rgb_output(result)


class TestEffectsConfiguration(unittest.TestCase):
    """Test the EFFECTS configuration dictionary."""

    def test_effects_structure(self):
        """Test that EFFECTS dictionary has correct structure."""
        self.assertIsInstance(EFFECTS, dict)
        self.assertGreater(len(EFFECTS), 0)

        for effect_name, effect_config in EFFECTS.items():
            self.assertIsInstance(effect_name, str)
            self.assertIsInstance(effect_config, dict)
            self.assertIn('function', effect_config)
            self.assertTrue(callable(effect_config['function']))

    def test_effects_have_expected_functions(self):
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

    def test_effects_parameters_structure(self):
        """Test that effects parameters are properly structured."""
        for _effect_name, effect_config in EFFECTS.items():
            if 'parameters' in effect_config:
                self.assertIsInstance(effect_config['parameters'], dict)

                # Check that parameter values are reasonable types
                for param_name, param_value in effect_config[
                    'parameters'
                ].items():
                    self.assertIsInstance(param_name, str)
                    self.assertIn(type(param_value), [int, float, str])

    def test_stripe_variants(self):
        """Test that stripe variants are properly configured."""
        stripe_variants = ['h-stripes', 'v-stripes', 'd-stripes']
        expected_directions = ['horizontal', 'vertical', 'diagonal']

        for variant, direction in zip(
            stripe_variants, expected_directions, strict=False,
        ):
            self.assertIn(variant, EFFECTS)
            self.assertEqual(EFFECTS[variant]['function'], stripes)
            self.assertEqual(
                EFFECTS[variant]['parameters']['direction'], direction,
            )

    def test_shine_variants(self):
        """Test that shine variants are properly configured."""
        shine_variants = ['shine', 'soft', 'gradient']

        for variant in shine_variants:
            self.assertIn(variant, EFFECTS)
            self.assertEqual(EFFECTS[variant]['function'], shine)


class TestLoadEffect(unittest.TestCase):
    """Test the load_effect function."""

    def test_load_effect_valid_name(self):
        """Test load_effect with valid effect name."""
        effect_func = load_effect('shine', 'default')
        self.assertIsNotNone(effect_func)
        self.assertTrue(callable(effect_func))

    def test_load_effect_invalid_name(self):
        """Test load_effect with invalid effect name."""
        effect_func = load_effect('nonexistent', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_empty_name(self):
        """Test load_effect with empty effect name."""
        effect_func = load_effect('', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_none_name(self):
        """Test load_effect with None as effect name."""
        effect_func = load_effect(None, 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_function_works(self):
        """Test that loaded effect function works correctly."""
        effect_func = load_effect('noop', 'default')
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 150, 200)
        result = effect_func(test_rgb, 0, 3)
        self.assertEqual(result, test_rgb)

    def test_load_effect_applies_parameters(self):
        """Test that loaded effect applies configured parameters."""
        effect_func = load_effect('dim', 'default')
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)

        # Should be dimmed according to default factor
        self.assertLess(sum(result), sum(test_rgb))

    def test_load_effect_palette_override(self):
        """Test load_effect with palette-specific parameters."""
        # This tests the palette override mechanism even though
        # no palette overrides exist in current EFFECTS
        effect_func = load_effect('shine', 'custom')
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)

        # Should still work even if palette doesn't exist
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_load_effect_all_configured_effects(self):
        """Test that all configured effects can be loaded."""
        for effect_name in EFFECTS:
            effect_func = load_effect(effect_name, 'default')
            self.assertIsNotNone(
                effect_func, f'Failed to load effect: {effect_name}',
            )
            self.assertTrue(callable(effect_func))


class TestParameterParsing(unittest.TestCase):
    """Test parameter parsing functions."""

    def test_parse_effect_parameters_empty(self):
        """Test parsing empty parameter string."""
        result = parse_effect_parameters('')
        self.assertEqual(result, {})

    def test_parse_effect_parameters_single_int(self):
        """Test parsing single integer parameter."""
        result = parse_effect_parameters('intensity=5')
        self.assertEqual(result, {'intensity': 5})

    def test_parse_effect_parameters_single_float(self):
        """Test parsing single float parameter."""
        result = parse_effect_parameters('factor=0.75')
        self.assertEqual(result, {'factor': 0.75})

    def test_parse_effect_parameters_single_string(self):
        """Test parsing single string parameter."""
        result = parse_effect_parameters('direction=horizontal')
        self.assertEqual(result, {'direction': 'horizontal'})

    def test_parse_effect_parameters_quoted_string(self):
        """Test parsing quoted string parameter."""
        result = parse_effect_parameters('mode="light mode"')
        self.assertEqual(result, {'mode': 'light mode'})

        result = parse_effect_parameters("mode='dark mode'")
        self.assertEqual(result, {'mode': 'dark mode'})

    def test_parse_effect_parameters_boolean(self):
        """Test parsing boolean parameters."""
        result = parse_effect_parameters('enabled=true')
        self.assertEqual(result, {'enabled': True})

        result = parse_effect_parameters('disabled=false')
        self.assertEqual(result, {'disabled': False})

    def test_parse_effect_parameters_multiple(self):
        """Test parsing multiple parameters."""
        result = parse_effect_parameters(
            'intensity=0.8,factor=1.5,direction=vertical',
        )
        expected = {
            'intensity': 0.8, 'factor': 1.5,
            'direction': 'vertical',
        }
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_mixed_types(self):
        """Test parsing mixed parameter types."""
        result = parse_effect_parameters(
            'intensity=0.8,frequency=3,enabled=true,mode=glossy',
        )
        expected = {
            'intensity': 0.8, 'frequency': 3,
            'enabled': True, 'mode': 'glossy',
        }
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_negative_numbers(self):
        """Test parsing negative numbers."""
        result = parse_effect_parameters('offset=-5,factor=-0.3')
        expected = {'offset': -5, 'factor': -0.3}
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_whitespace(self):
        """Test parsing with extra whitespace."""
        result = parse_effect_parameters('  intensity = 0.8 , factor = 1.5  ')
        expected = {'intensity': 0.8, 'factor': 1.5}
        self.assertEqual(result, expected)

    def test_parse_effect_parameters_invalid_format(self):
        """Test parsing with invalid parameter format."""
        result = parse_effect_parameters('intensity,factor=1.5')
        expected = {'factor': 1.5}  # Invalid param is ignored
        self.assertEqual(result, expected)

    def test_parse_effect_name_simple(self):
        """Test parsing simple effect name without parameters."""
        name, params = parse_effect_name('shine')
        self.assertEqual(name, 'shine')
        self.assertEqual(params, {})

    def test_parse_effect_name_with_parameters(self):
        """Test parsing effect name with parameters."""
        name, params = parse_effect_name('shine(intensity=0.8)')
        self.assertEqual(name, 'shine')
        self.assertEqual(params, {'intensity': 0.8})

    def test_parse_effect_name_with_multiple_parameters(self):
        """Test parsing effect name with multiple parameters."""
        name, params = parse_effect_name('chrome(intensity=0.7,metallic=0.9)')
        self.assertEqual(name, 'chrome')
        self.assertEqual(params, {'intensity': 0.7, 'metallic': 0.9})

    def test_parse_effect_name_empty_parameters(self):
        """Test parsing effect name with empty parameter list."""
        name, params = parse_effect_name('neon()')
        self.assertEqual(name, 'neon')
        self.assertEqual(params, {})

    def test_parse_effect_name_whitespace(self):
        """Test parsing effect name with whitespace."""
        name, params = parse_effect_name('  gold( intensity=0.6 ) ')
        self.assertEqual(name, 'gold')
        self.assertEqual(params, {'intensity': 0.6})

    def test_parse_effect_name_invalid_syntax(self):
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

    def test_load_effect_single_effect(self):
        """Test loading single effect without changes."""
        effect_func = load_effect('noop', 'default')
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 150, 200)
        result = effect_func(test_rgb, 0, 3)
        self.assertEqual(result, test_rgb)

    def test_load_effect_single_with_custom_params(self):
        """Test loading single effect with custom parameters."""
        effect_func = load_effect('dim(factor=0.5)', 'default')
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)

        # Should be dimmed by factor 0.5
        expected = (50, 50, 50)
        self.assertEqual(result, expected)

    def test_load_effect_chained_effects(self):
        """Test loading chained effects."""
        effect_func = load_effect('brighten|dim', 'default')
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)

        # Should apply brighten then dim
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_load_effect_chained_with_params(self):
        """Test loading chained effects with custom parameters."""
        effect_func = load_effect(
            'brighten(factor=2.0)|dim(factor=0.5)',
            'default',
        )
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)

        # Should apply brighten factor 2.0 then dim factor 0.5
        # (100 * 2.0) * 0.5 = 100, so should return to original
        expected = (100, 100, 100)
        self.assertEqual(result, expected)

    def test_load_effect_multiple_chained(self):
        """Test loading multiple chained effects."""
        effect_func = load_effect('noop|noop|noop', 'default')
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 150, 200)
        result = effect_func(test_rgb, 0, 3)
        # Chain of noops should return original
        self.assertEqual(result, test_rgb)

    def test_load_effect_invalid_in_chain(self):
        """Test loading chain with invalid effect."""
        effect_func = load_effect('shine|invalid_effect|dim', 'default')
        # Should still work with valid effects
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)
        # Should apply shine and dim, skipping invalid
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_load_effect_all_invalid_chain(self):
        """Test loading chain with all invalid effects."""
        effect_func = load_effect('invalid1|invalid2', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_empty_chain(self):
        """Test loading empty effect chain."""
        effect_func = load_effect('', 'default')
        self.assertIsNone(effect_func)

    def test_load_effect_complex_params(self):
        """Test loading effect with complex parameter combinations."""
        effect_func = load_effect(
            'd-stripes(frequency=3,intensity=0.6)',
            'default',
        )
        self.assertIsNotNone(effect_func)

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_load_effect_parameter_override(self):
        """Test that custom parameters override default ones."""
        # Load with very low intensity
        effect_func1 = load_effect('dim(factor=0.1)', 'default')

        # Load with very high intensity
        effect_func2 = load_effect('dim(factor=0.9)', 'default')

        test_rgb = (100, 100, 100)
        result1 = effect_func1(test_rgb, 0, 3)
        result2 = effect_func2(test_rgb, 0, 3)

        # Results should be different due to different factors
        self.assertNotEqual(result1, result2)

    def test_load_effect_whitespace_handling(self):
        """Test that whitespace in effect names is handled correctly."""
        effect_func = load_effect('  shine  |  dim  ', 'default')
        self.assertIsNotNone(effect_func)

    def test_load_single_effect_palette_specific_params(self):
        """Test load_single_effect with palette-specific parameters."""
        # Create a mock effect config with palette-specific parameters
        mock_effect_config = {
            'function': noop,
            'parameters': {'base_param': 1.0},
            'default': {'palette_param': 2.0},  # Palette-specific parameter
        }

        with patch.dict(
                'cubing_algs.effects.EFFECTS',
                {'test_effect': mock_effect_config},
        ):
            effect_func = load_single_effect('test_effect', {}, 'default')
            self.assertIsNotNone(effect_func)

            # Test that the effect function works
            result = effect_func((100, 100, 100), 0, 3)
            self.assertEqual(result, (100, 100, 100))  # noop returns unchanged

        test_rgb = (100, 100, 100)
        result = effect_func(test_rgb, 0, 3)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_load_effect_real_world_combinations(self):
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

            result = effect_func(test_rgb, 4, 3)
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 3)
            for component in result:
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)
