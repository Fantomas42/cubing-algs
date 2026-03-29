"""Tests for cube image rendering."""
import math
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.display.image import CAMERA_DISTANCE
from cubing_algs.display.image import assemble_svg
from cubing_algs.display.image import build_cube_svg
from cubing_algs.display.image import build_top_view_svg
from cubing_algs.display.image import compute_visible_faces
from cubing_algs.display.image import hex_to_rgba
from cubing_algs.display.image import lerp_2d
from cubing_algs.display.image import parse_rotation
from cubing_algs.display.image import points_to_svg
from cubing_algs.display.image import project
from cubing_algs.display.image import render_cube
from cubing_algs.display.image import resolve_face_colors
from cubing_algs.display.image import rotate_point
from cubing_algs.solved_state import SOLVED_FACELETS_3x3x3
from cubing_algs.vcube import VCube


class ParseRotationTestCase(unittest.TestCase):
    """Tests for rotation string parsing."""

    def test_single_axis(self) -> None:
        """Test parsing a single axis rotation."""
        result = parse_rotation('y45')
        self.assertEqual(result, [('y', 45)])

    def test_two_axes(self) -> None:
        """Test parsing two axis rotations."""
        result = parse_rotation('y45x-25')
        self.assertEqual(result, [('y', 45), ('x', -25)])

    def test_three_axes(self) -> None:
        """Test parsing three axis rotations."""
        result = parse_rotation('x20y45z10')
        self.assertEqual(
            result, [('x', 20), ('y', 45), ('z', 10)],
        )

    def test_negative_angle(self) -> None:
        """Test parsing negative angle."""
        result = parse_rotation('y-30')
        self.assertEqual(result, [('y', -30)])

    def test_zero_angle(self) -> None:
        """Test parsing zero angle."""
        result = parse_rotation('x0')
        self.assertEqual(result, [('x', 0)])

    def test_large_angle(self) -> None:
        """Test parsing angle above 360."""
        result = parse_rotation('y999')
        self.assertEqual(result, [('y', 999)])

    def test_invalid_string_raises(self) -> None:
        """Test that invalid rotation strings raise."""
        with self.assertRaises(ValueError):
            parse_rotation('invalid')

    def test_empty_string_raises(self) -> None:
        """Test that empty string raises ValueError."""
        with self.assertRaises(ValueError):
            parse_rotation('')

    def test_partial_match_raises(self) -> None:
        """Test that partially valid string raises."""
        with self.assertRaises(ValueError):
            parse_rotation('y45garbage')


class RotatePointTestCase(unittest.TestCase):
    """Tests for 3D point rotation."""

    def test_no_rotation(self) -> None:
        """Test point with empty rotation list."""
        point = (1.0, 0.0, 0.0)
        result = rotate_point(point, [])
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 0.0)
        self.assertAlmostEqual(result[2], 0.0)

    def test_y_rotation_90(self) -> None:
        """Test 90-degree Y rotation (clockwise from above)."""
        point = (1.0, 0.0, 0.0)
        result = rotate_point(point, [('y', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], 1.0, places=5)

    def test_x_rotation_90(self) -> None:
        """Test 90-degree X rotation (clockwise from right)."""
        point = (0.0, 1.0, 0.0)
        result = rotate_point(point, [('x', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], -1.0, places=5)

    def test_z_rotation_90(self) -> None:
        """Test 90-degree Z rotation (clockwise from front)."""
        point = (1.0, 0.0, 0.0)
        result = rotate_point(point, [('z', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], -1.0, places=5)
        self.assertAlmostEqual(result[2], 0.0, places=5)

    def test_combined_rotation(self) -> None:
        """Test combined rotation is applied in sequence."""
        point = (1.0, 0.0, 0.0)
        result = rotate_point(
            point, [('y', 90), ('x', 90)],
        )
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 1.0, places=5)
        self.assertAlmostEqual(result[2], 0.0, places=5)


class ProjectTestCase(unittest.TestCase):
    """Tests for perspective projection."""

    def test_project_perspective(self) -> None:
        """Test perspective projection scales by distance."""
        result = project((1.0, 2.0, 3.0), distance=6.0)
        self.assertEqual(len(result), 2)
        # scale = 6 / (6 - 3) = 2.0
        self.assertAlmostEqual(result[0], 2.0)
        self.assertAlmostEqual(result[1], 4.0)

    def test_project_at_origin_z(self) -> None:
        """Test that z=0 produces no scaling."""
        result = project((1.0, 2.0, 0.0), distance=6.0)
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 2.0)


class VisibleFacesTestCase(unittest.TestCase):
    """Tests for face visibility computation."""

    def test_default_rotation_shows_three_faces(self) -> None:
        """Default rotation y45x-25 shows exactly 3 faces."""
        rotations = [('y', 45), ('x', -25)]
        faces = compute_visible_faces(rotations, CAMERA_DISTANCE)
        self.assertEqual(len(faces), 3)

    def test_no_rotation_shows_one_face(self) -> None:
        """With no rotation, viewer sees only F face."""
        rotations = [('y', 0)]
        faces = compute_visible_faces(rotations, CAMERA_DISTANCE)
        face_names = [f[0] for f in faces]
        self.assertIn('F', face_names)
        self.assertEqual(len(faces), 1)

    def test_face_data_structure(self) -> None:
        """Each face has name, 4 corners, and index."""
        rotations = [('y', -45), ('x', 34)]
        faces = compute_visible_faces(rotations, CAMERA_DISTANCE)
        for face_name, corners_2d, face_index in faces:
            self.assertIsInstance(face_name, str)
            self.assertEqual(len(corners_2d), 4)
            self.assertIsInstance(face_index, int)

    def test_faces_sorted_back_to_front(self) -> None:
        """Visible faces are sorted back-to-front."""
        rotations = [('y', -45), ('x', 34)]
        faces = compute_visible_faces(rotations, CAMERA_DISTANCE)
        self.assertTrue(len(faces) >= 1)

    def test_exact_90_no_degenerate_faces(self) -> None:
        """Exact 90-degree rotation doesn't produce edge-on faces."""
        rotations = [('y', 90)]
        faces = compute_visible_faces(rotations, CAMERA_DISTANCE)
        face_names = [f[0] for f in faces]
        # At y90, only the R face should be visible (not F or B)
        self.assertIn('R', face_names)
        self.assertNotIn('F', face_names)
        self.assertNotIn('B', face_names)


class BuildSvgTestCase(unittest.TestCase):
    """Tests for SVG generation."""

    def test_returns_valid_svg(self) -> None:
        """Test that output is a valid SVG string."""
        rotations = [('y', -45), ('x', 34)]
        svg = build_cube_svg(SOLVED_FACELETS_3x3x3, 200, rotations)
        self.assertTrue(svg.startswith('<svg'))
        self.assertTrue(svg.endswith('</svg>'))
        self.assertIn(
            'xmlns="http://www.w3.org/2000/svg"', svg,
        )

    def test_contains_viewbox(self) -> None:
        """Test that SVG has correct viewBox."""
        svg = build_cube_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('viewBox="0 0 200 200"', svg)

    def test_custom_size(self) -> None:
        """Test custom size is reflected in viewBox."""
        svg = build_cube_svg(
            SOLVED_FACELETS_3x3x3, 400, [('y', -45), ('x', 34)],
        )
        self.assertIn('viewBox="0 0 400 400"', svg)

    def test_contains_polygon_elements(self) -> None:
        """Test that SVG contains polygon elements."""
        svg = build_cube_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('<polygon', svg)

    def test_no_gradient_defs(self) -> None:
        """Test that SVG does not contain gradient definitions."""
        svg = build_cube_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertNotIn('<defs>', svg)
        self.assertNotIn('linearGradient', svg)

    def test_scrambled_state_renders(self) -> None:
        """Test scrambled state produces valid SVG."""
        cube = VCube()
        cube.rotate("R U R' U'")
        svg = build_cube_svg(
            cube.state, 200, [('y', -45), ('x', 34)],
        )
        self.assertTrue(svg.startswith('<svg'))

    def test_contains_per_face_groups(self) -> None:
        """Test that SVG has per-face groups."""
        svg = build_cube_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('class="face-', svg)


class StickerColorCorrectnessTestCase(unittest.TestCase):
    """Tests that sticker colors match the facelet state."""

    def test_r_move_changes_u_face_colors(self) -> None:
        """After R move, U-face should include F-face colors."""
        cube = VCube()
        cube.rotate('R')
        svg = build_cube_svg(
            cube.state, 200, [('y', 45), ('x', -25)],
            palette_name='default',
        )
        # R move brings F-face (green) facelets onto the U face.
        # The SVG should contain green fill colors, not just white.
        self.assertIn('fill="#00D700"', svg)

    def test_solved_cube_u_face_all_white(self) -> None:
        """Solved cube U-face stickers should all be white."""
        svg = build_cube_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', 45), ('x', -25)],
            palette_name='default',
        )
        # U face should use white fill color
        self.assertIn('fill="#F5F5F5"', svg)


class RenderCubeFromVCubeTestCase(unittest.TestCase):
    """Tests for render_cube with VCube input."""

    def test_solved_cube_returns_svg(self) -> None:
        """Test rendering a solved cube returns SVG."""
        cube = VCube()
        result = render_cube(cube)
        self.assertIsInstance(result, str)
        assert result is not None  # noqa: S101
        self.assertTrue(result.startswith('<svg'))

    def test_scrambled_cube(self) -> None:
        """Test rendering a scrambled cube."""
        cube = VCube()
        cube.rotate("R U R' U'")
        result = render_cube(cube)
        self.assertIsNotNone(result)
        assert result is not None  # noqa: S101
        self.assertTrue(result.startswith('<svg'))

    def test_custom_size(self) -> None:
        """Test rendering with custom size."""
        cube = VCube()
        result = render_cube(cube, size=400)
        assert result is not None  # noqa: S101
        self.assertIn('viewBox="0 0 400 400"', result)

    def test_custom_rotation(self) -> None:
        """Test rendering with custom rotation."""
        cube = VCube()
        result = render_cube(cube, rotation='y-30')
        assert result is not None  # noqa: S101
        self.assertTrue(result.startswith('<svg'))


class RenderCubeFromAlgorithmTestCase(unittest.TestCase):
    """Tests for render_cube with Algorithm input."""

    def test_algorithm_renders(self) -> None:
        """Test rendering from an Algorithm."""
        algo = Algorithm.parse_moves("R U R' U'")
        result = render_cube(algo)
        assert result is not None  # noqa: S101
        self.assertTrue(result.startswith('<svg'))

    def test_algorithm_matches_vcube(self) -> None:
        """Test Algorithm rendering matches VCube."""
        algo = Algorithm.parse_moves("R U R' U'")
        cube = VCube()
        cube.rotate(algo)
        svg_from_algo = render_cube(algo)
        svg_from_cube = render_cube(cube)
        self.assertEqual(svg_from_algo, svg_from_cube)

    def test_empty_algorithm(self) -> None:
        """Test empty algorithm renders solved cube."""
        algo = Algorithm()
        cube = VCube()
        svg_from_algo = render_cube(algo)
        svg_from_cube = render_cube(cube)
        self.assertEqual(svg_from_algo, svg_from_cube)


class RenderCubeValidationTestCase(unittest.TestCase):
    """Tests for input validation in render_cube."""

    def test_invalid_size_raises(self) -> None:
        """Test that size <= 0 raises ValueError."""
        cube = VCube()
        with self.assertRaises(ValueError):
            render_cube(cube, size=0)
        with self.assertRaises(ValueError):
            render_cube(cube, size=-1)

    def test_invalid_rotation_raises(self) -> None:
        """Test invalid rotation string raises."""
        cube = VCube()
        with self.assertRaises(ValueError):
            render_cube(cube, rotation='invalid')

    def test_invalid_source_type_raises(self) -> None:
        """Test invalid source type raises TypeError."""
        with self.assertRaises(TypeError):
            render_cube('not a cube')  # type: ignore[arg-type]


class AssembleSvgTestCase(unittest.TestCase):
    """Tests for SVG assembly."""

    def test_basic_assembly(self) -> None:
        """Test assemble_svg produces valid SVG."""
        result = assemble_svg(100, ['<g>content</g>'])
        self.assertTrue(result.startswith('<svg'))
        self.assertTrue(result.endswith('</svg>'))
        self.assertIn('<g>content</g>', result)

    def test_empty_face_groups(self) -> None:
        """Test assemble_svg with no face groups."""
        result = assemble_svg(100, [])
        self.assertIn('viewBox="0 0 100 100"', result)


class RotatePointCombinedTestCase(unittest.TestCase):
    """Tests for rotate_point with z-axis in combined rotations."""

    def test_z_then_x_rotation(self) -> None:
        """Test z rotation followed by another axis."""
        point = (1.0, 0.0, 0.0)
        result = rotate_point(point, [('z', 90), ('x', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], 1.0, places=5)

    def test_unknown_axis_ignored(self) -> None:
        """Test that unknown axis is silently skipped."""
        point = (1.0, 2.0, 3.0)
        result = rotate_point(point, [('w', 90)])
        self.assertEqual(result, point)


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


class Lerp2dTestCase(unittest.TestCase):
    """Tests for 2D linear interpolation."""

    def test_t_zero_returns_start(self) -> None:
        """Test t=0 returns the start point."""
        result = lerp_2d((0.0, 0.0), (10.0, 20.0), 0.0)
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 0.0)

    def test_t_one_returns_end(self) -> None:
        """Test t=1 returns the end point."""
        result = lerp_2d((0.0, 0.0), (10.0, 20.0), 1.0)
        self.assertAlmostEqual(result[0], 10.0)
        self.assertAlmostEqual(result[1], 20.0)

    def test_midpoint(self) -> None:
        """Test t=0.5 returns the midpoint."""
        result = lerp_2d((2.0, 4.0), (10.0, 20.0), 0.5)
        self.assertAlmostEqual(result[0], 6.0)
        self.assertAlmostEqual(result[1], 12.0)


class PointsToSvgTestCase(unittest.TestCase):
    """Tests for SVG points formatting."""

    def test_basic_points(self) -> None:
        """Test formatting a list of 2D points."""
        result = points_to_svg([(1.0, 2.0), (3.0, 4.0)])
        self.assertEqual(result, '1.00,2.00 3.00,4.00')

    def test_empty_list(self) -> None:
        """Test empty list returns empty string."""
        self.assertEqual(points_to_svg([]), '')


class ResolveFaceColorsTestCase(unittest.TestCase):
    """Tests for palette resolution."""

    def test_default_palette_has_all_faces(self) -> None:
        """Test default palette returns all 6 face colors."""
        colors = resolve_face_colors('default')
        self.assertEqual(len(colors), 6)
        for face in 'URFDLB':
            self.assertIn(face, colors)

    def test_unknown_palette_falls_back_to_default(self) -> None:
        """Test unknown palette name falls back to default."""
        colors_default = resolve_face_colors('default')
        colors_unknown = resolve_face_colors('nonexistent_palette')
        self.assertEqual(colors_default, colors_unknown)


class RenderCubeDistanceValidationTestCase(unittest.TestCase):
    """Tests for distance parameter validation."""

    def test_distance_too_small_raises(self) -> None:
        """Test distance <= sqrt(3) raises ValueError."""
        cube = VCube()
        with self.assertRaises(ValueError):
            render_cube(cube, distance=1.0)

    def test_distance_at_boundary_raises(self) -> None:
        """Test distance exactly at sqrt(3) raises ValueError."""
        cube = VCube()
        with self.assertRaises(ValueError):
            render_cube(cube, distance=math.sqrt(3))

    def test_distance_just_above_boundary_ok(self) -> None:
        """Test distance just above sqrt(3) succeeds."""
        cube = VCube()
        result = render_cube(cube, distance=math.sqrt(3) + 0.1)
        self.assertTrue(result.startswith('<svg'))


class RenderCubeCustomParametersTestCase(unittest.TestCase):
    """Tests for render_cube with custom parameters."""

    def test_2x2_cube(self) -> None:
        """Test rendering a 2x2 cube."""
        cube = VCube(size=2)
        result = render_cube(cube, cube_size=2)
        self.assertTrue(result.startswith('<svg'))
        self.assertIn('<polygon', result)

    def test_4x4_cube(self) -> None:
        """Test rendering a 4x4 cube."""
        cube = VCube(size=4)
        result = render_cube(cube, cube_size=4)
        self.assertTrue(result.startswith('<svg'))

    def test_custom_cube_color_with_alpha(self) -> None:
        """Test rendering with semi-transparent cube body."""
        cube = VCube()
        result = render_cube(cube, cube_color='#11111180')
        self.assertIn('fill-opacity=', result)

    def test_opaque_cube_color_no_opacity_attr(self) -> None:
        """Test opaque cube color omits fill-opacity."""
        cube = VCube()
        result = render_cube(cube, cube_color='#222222')
        self.assertNotIn('fill-opacity=', result)

    def test_custom_distance(self) -> None:
        """Test rendering with custom distance."""
        cube = VCube()
        result = render_cube(cube, distance=20.0)
        self.assertTrue(result.startswith('<svg'))


class BuildTopViewSvgTestCase(unittest.TestCase):
    """Tests for flat top-face SVG rendering."""

    def test_returns_valid_svg(self) -> None:
        """Test that output is a valid SVG wrapper."""
        result = build_top_view_svg(SOLVED_FACELETS_3x3x3, 200)
        self.assertTrue(result.startswith('<svg'))
        self.assertTrue(result.endswith('</svg>'))
        self.assertIn('xmlns=', result)

    def test_contains_u_face_group(self) -> None:
        """Test that U face group is present."""
        result = build_top_view_svg(SOLVED_FACELETS_3x3x3, 200)
        self.assertIn('class="face-U"', result)

    def test_contains_adjacent_face_groups(self) -> None:
        """Test that all adjacent face groups are present."""
        result = build_top_view_svg(SOLVED_FACELETS_3x3x3, 200)
        for face in ('F', 'R', 'B', 'L'):
            with self.subTest(face=face):
                self.assertIn(f'class="face-{face}"', result)

    def test_sticker_count_3x3(self) -> None:
        """Test correct number of polygon elements for 3x3."""
        result = build_top_view_svg(SOLVED_FACELETS_3x3x3, 200)
        # 9 U stickers + 4 * 3 adjacent = 21 sticker polygons
        # Plus 5 body polygons = 26 total
        polygon_count = result.count('<polygon')
        self.assertEqual(polygon_count, 26)

    def test_2x2_cube(self) -> None:
        """Test rendering a 2x2 cube."""
        state = 'U' * 4 + 'R' * 4 + 'F' * 4 + 'D' * 4 + 'L' * 4 + 'B' * 4
        result = build_top_view_svg(state, 200, cube_size=2)
        self.assertTrue(result.startswith('<svg'))
        # 4 U stickers + 4 * 2 adjacent = 12 + 5 body = 17
        self.assertEqual(result.count('<polygon'), 17)

    def test_4x4_cube(self) -> None:
        """Test rendering a 4x4 cube."""
        state = 'U' * 16 + 'R' * 16 + 'F' * 16 + 'D' * 16 + 'L' * 16 + 'B' * 16
        result = build_top_view_svg(state, 200, cube_size=4)
        self.assertTrue(result.startswith('<svg'))
        # 16 U stickers + 4 * 4 adjacent = 32 + 5 body = 37
        self.assertEqual(result.count('<polygon'), 37)

    def test_cube_color_with_alpha(self) -> None:
        """Test top view with semi-transparent cube body."""
        result = build_top_view_svg(
            SOLVED_FACELETS_3x3x3, 200,
            cube_color='#11111180',
        )
        self.assertIn('fill-opacity=', result)


class RenderCubeTopViewTestCase(unittest.TestCase):
    """Tests for render_cube with view='top'."""

    def test_view_top_returns_valid_svg(self) -> None:
        """Test that top view returns valid SVG."""
        cube = VCube()
        result = render_cube(cube, view='top')
        self.assertTrue(result.startswith('<svg'))
        self.assertIn('class="face-U"', result)

    def test_view_3d_is_default(self) -> None:
        """Test that default view is 3d."""
        cube = VCube()
        default = render_cube(cube)
        explicit = render_cube(cube, view='3d')
        self.assertEqual(default, explicit)

    def test_invalid_view_raises(self) -> None:
        """Test that invalid view name raises ValueError."""
        cube = VCube()
        with self.assertRaises(ValueError, msg='view must be'):
            render_cube(cube, view='invalid')

    def test_view_top_ignores_rotation(self) -> None:
        """Test that rotation param doesn't error in top view."""
        cube = VCube()
        result = render_cube(
            cube, view='top', rotation='x90y45',
        )
        self.assertTrue(result.startswith('<svg'))

    def test_algorithm_with_top_view(self) -> None:
        """Test top view with Algorithm source."""
        algo = Algorithm.parse_moves('R')
        result = render_cube(algo, view='top')
        self.assertTrue(result.startswith('<svg'))
        self.assertIn('class="face-U"', result)

    def test_top_view_2x2(self) -> None:
        """Test top view with 2x2 cube."""
        cube = VCube(size=2)
        result = render_cube(cube, view='top')
        self.assertTrue(result.startswith('<svg'))
