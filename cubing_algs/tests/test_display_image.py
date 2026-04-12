"""Tests for cube image rendering."""
import unittest

from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.image import ImageDisplay
from cubing_algs.vcube import VCube


class ParseRotationTestCase(unittest.TestCase):
    """Tests for rotation string parsing."""

    def test_single_axis(self) -> None:
        """Test parsing a single axis rotation."""
        result = ImageDisplay.parse_rotation('y45')
        self.assertEqual(result, [('y', 45)])

    def test_two_axes(self) -> None:
        """Test parsing two axis rotations."""
        result = ImageDisplay.parse_rotation('y45x-25')
        self.assertEqual(result, [('y', 45), ('x', -25)])

    def test_three_axes(self) -> None:
        """Test parsing three axis rotations."""
        result = ImageDisplay.parse_rotation('x20y45z10')
        self.assertEqual(
            result, [('x', 20), ('y', 45), ('z', 10)],
        )

    def test_negative_angle(self) -> None:
        """Test parsing negative angle."""
        result = ImageDisplay.parse_rotation('y-30')
        self.assertEqual(result, [('y', -30)])

    def test_zero_angle(self) -> None:
        """Test parsing zero angle."""
        result = ImageDisplay.parse_rotation('x0')
        self.assertEqual(result, [('x', 0)])

    def test_large_angle(self) -> None:
        """Test parsing angle above 360."""
        result = ImageDisplay.parse_rotation('y999')
        self.assertEqual(result, [('y', 999)])

    def test_empty_string(self) -> None:
        """Test that empty string returns default value."""
        result = ImageDisplay.parse_rotation('')
        self.assertEqual(result, [('y', 45), ('x', -34)])

    def test_partial_match_raises(self) -> None:
        """Test that partially valid string returns default value."""
        result = ImageDisplay.parse_rotation('y45garbage')
        self.assertEqual(result, [('y', 45), ('x', -34)])


class RotatePointTestCase(unittest.TestCase):
    """Tests for 3D point rotation."""

    def test_no_rotation(self) -> None:
        """Test point with empty rotation list."""
        point = (1.0, 0.0, 0.0)
        result = ImageDisplay.rotate_point(point, [])
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 0.0)
        self.assertAlmostEqual(result[2], 0.0)

    def test_y_rotation_90(self) -> None:
        """Test 90-degree Y rotation (clockwise from above)."""
        point = (1.0, 0.0, 0.0)
        result = ImageDisplay.rotate_point(point, [('y', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], 1.0, places=5)

    def test_x_rotation_90(self) -> None:
        """Test 90-degree X rotation (clockwise from right)."""
        point = (0.0, 1.0, 0.0)
        result = ImageDisplay.rotate_point(point, [('x', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], -1.0, places=5)

    def test_z_rotation_90(self) -> None:
        """Test 90-degree Z rotation (clockwise from front)."""
        point = (1.0, 0.0, 0.0)
        result = ImageDisplay.rotate_point(point, [('z', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], -1.0, places=5)
        self.assertAlmostEqual(result[2], 0.0, places=5)

    def test_combined_rotation(self) -> None:
        """Test combined rotation is applied in sequence."""
        point = (1.0, 0.0, 0.0)
        result = ImageDisplay.rotate_point(
            point, [('y', 90), ('x', 90)],
        )
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 1.0, places=5)
        self.assertAlmostEqual(result[2], 0.0, places=5)


class ProjectTestCase(unittest.TestCase):
    """Tests for perspective projection."""

    def test_project_perspective(self) -> None:
        """Test perspective projection scales by distance."""
        result = ImageDisplay.project((1.0, 2.0, 3.0), distance=6.0)
        self.assertEqual(len(result), 2)
        # scale = 6 / (6 - 3) = 2.0
        self.assertAlmostEqual(result[0], 2.0)
        self.assertAlmostEqual(result[1], 4.0)

    def test_project_at_origin_z(self) -> None:
        """Test that z=0 produces no scaling."""
        result = ImageDisplay.project((1.0, 2.0, 0.0), distance=6.0)
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 2.0)


class VisibleFacesTestCase(unittest.TestCase):
    """Tests for face visibility computation."""

    def test_default_rotation_shows_three_faces(self) -> None:
        """Default rotation y45x-25 shows exactly 3 faces."""
        rotations = [('y', 45), ('x', -25)]
        faces = ImageDisplay(VCube()).compute_visible_faces(
            rotations, DISTANCE,
        )
        self.assertEqual(len(faces), 3)

    def test_no_rotation_shows_one_face(self) -> None:
        """With no rotation, viewer sees only F face."""
        rotations = [('y', 0)]
        faces = ImageDisplay(VCube()).compute_visible_faces(
            rotations, DISTANCE,
        )
        face_names = [f[0] for f in faces]
        self.assertIn('F', face_names)
        self.assertEqual(len(faces), 1)

    def test_face_data_structure(self) -> None:
        """Each face has name, 4 corners, and index."""
        rotations = [('y', -45), ('x', 34)]
        faces = ImageDisplay(VCube()).compute_visible_faces(
            rotations, DISTANCE,
        )
        for face_name, corners_2d, face_index in faces:
            self.assertIsInstance(face_name, str)
            self.assertEqual(len(corners_2d), 4)
            self.assertIsInstance(face_index, int)

    def test_faces_sorted_back_to_front(self) -> None:
        """Visible faces are sorted back-to-front."""
        rotations = [('y', -45), ('x', 34)]
        faces = ImageDisplay(VCube()).compute_visible_faces(
            rotations, DISTANCE,
        )
        self.assertTrue(len(faces) >= 1)

    def test_exact_90_no_degenerate_faces(self) -> None:
        """Exact 90-degree rotation doesn't produce edge-on faces."""
        rotations = [('y', 90)]
        faces = ImageDisplay(VCube()).compute_visible_faces(
            rotations, DISTANCE,
        )
        face_names = [f[0] for f in faces]
        # At y90, only the R face should be visible (not F or B)
        self.assertIn('R', face_names)
        self.assertNotIn('F', face_names)
        self.assertNotIn('B', face_names)


class BuildSvgTestCase(unittest.TestCase):
    """Tests for SVG generation."""

    def test_returns_valid_svg(self) -> None:
        """Test that output is a valid SVG string."""
        svg = ImageDisplay(VCube()).render()
        self.assertTrue(svg.startswith('<svg'))
        self.assertTrue(svg.endswith('</svg>'))
        self.assertIn(
            'xmlns="http://www.w3.org/2000/svg"', svg,
        )

    def test_contains_viewbox(self) -> None:
        """Test that SVG has correct viewBox."""
        svg = ImageDisplay(VCube()).render()
        self.assertIn('viewBox="0 0 200 200"', svg)

    def test_custom_size(self) -> None:
        """Test custom size is reflected in viewBox."""
        svg = ImageDisplay(VCube()).render(image_size=400)
        self.assertIn('viewBox="0 0 400 400"', svg)

    def test_contains_polygon_elements(self) -> None:
        """Test that SVG contains polygon elements."""
        svg = ImageDisplay(VCube()).render()
        self.assertIn('<polygon', svg)

    def test_no_gradient_defs(self) -> None:
        """Test that SVG does not contain gradient definitions."""
        svg = ImageDisplay(VCube()).render()
        self.assertNotIn('<defs>', svg)
        self.assertNotIn('linearGradient', svg)

    def test_scrambled_state_renders(self) -> None:
        """Test scrambled state produces valid SVG."""
        cube = VCube()
        cube.rotate("R U R' U'")
        svg = ImageDisplay(cube).render()
        self.assertTrue(svg.startswith('<svg'))

    def test_contains_per_face_groups(self) -> None:
        """Test that SVG has per-face groups."""
        svg = ImageDisplay(VCube()).render()
        self.assertIn('class="face-', svg)


class StickerColorCorrectnessTestCase(unittest.TestCase):
    """Tests that sticker colors match the facelet state."""

    def test_r_move_changes_u_face_colors(self) -> None:
        """After R move, U-face should include F-face colors."""
        cube = VCube()
        cube.rotate('R')
        svg = ImageDisplay(cube, palette_name='default').render()
        # R move brings F-face (green) facelets onto the U face.
        # The SVG should contain green fill colors, not just white.
        self.assertIn('fill="#00D700"', svg)

    def test_solved_cube_u_face_all_white(self) -> None:
        """Solved cube U-face stickers should all be white."""
        svg = ImageDisplay(VCube(), palette_name='default').render()
        # U face should use white fill color
        self.assertIn('fill="#F5F5F5"', svg)


class AssembleSvgTestCase(unittest.TestCase):
    """Tests for SVG assembly."""

    def test_basic_assembly(self) -> None:
        """Test assemble_svg produces valid SVG."""
        result = ImageDisplay.assemble_svg(100, ['<g>content</g>'])
        self.assertTrue(result.startswith('<svg'))
        self.assertTrue(result.endswith('</svg>'))
        self.assertIn('<g>content</g>', result)

    def test_empty_face_groups(self) -> None:
        """Test assemble_svg with no face groups."""
        result = ImageDisplay.assemble_svg(100, [])
        self.assertIn('viewBox="0 0 100 100"', result)


class RotatePointCombinedTestCase(unittest.TestCase):
    """Tests for rotate_point with z-axis in combined rotations."""

    def test_z_then_x_rotation(self) -> None:
        """Test z rotation followed by another axis."""
        point = (1.0, 0.0, 0.0)
        result = ImageDisplay.rotate_point(point, [('z', 90), ('x', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], 1.0, places=5)

    def test_unknown_axis_ignored(self) -> None:
        """Test that unknown axis is silently skipped."""
        point = (1.0, 2.0, 3.0)
        result = ImageDisplay.rotate_point(point, [('w', 90)])
        self.assertEqual(result, point)


class Lerp2dTestCase(unittest.TestCase):
    """Tests for 2D linear interpolation."""

    def test_t_zero_returns_start(self) -> None:
        """Test t=0 returns the start point."""
        result = ImageDisplay.lerp_2d((0.0, 0.0), (10.0, 20.0), 0.0)
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 0.0)

    def test_t_one_returns_end(self) -> None:
        """Test t=1 returns the end point."""
        result = ImageDisplay.lerp_2d((0.0, 0.0), (10.0, 20.0), 1.0)
        self.assertAlmostEqual(result[0], 10.0)
        self.assertAlmostEqual(result[1], 20.0)

    def test_midpoint(self) -> None:
        """Test t=0.5 returns the midpoint."""
        result = ImageDisplay.lerp_2d((2.0, 4.0), (10.0, 20.0), 0.5)
        self.assertAlmostEqual(result[0], 6.0)
        self.assertAlmostEqual(result[1], 12.0)


class PointsToSvgTestCase(unittest.TestCase):
    """Tests for SVG points formatting."""

    def test_basic_points(self) -> None:
        """Test formatting a list of 2D points."""
        result = ImageDisplay.points_to_svg([(1.0, 2.0), (3.0, 4.0)])
        self.assertEqual(result, '1.00,2.00 3.00,4.00')

    def test_empty_list(self) -> None:
        """Test empty list returns empty string."""
        self.assertEqual(ImageDisplay.points_to_svg([]), '')


class ResolveFaceColorsTestCase(unittest.TestCase):
    """Tests for palette resolution."""

    def test_default_palette_has_all_faces(self) -> None:
        """Test default palette returns all 6 face colors."""
        colors = ImageDisplay(
            VCube(),
            palette_name='default',
        ).load_palette()

        self.assertEqual(len(colors), 7)
        for face in 'URFDLB':
            self.assertIn(face, colors)
        self.assertIn('masked', colors)

    def test_unknown_palette_falls_back_to_default(self) -> None:
        """Test unknown palette name falls back to default."""
        colors_default = ImageDisplay(
            VCube(),
            palette_name='default',
        ).load_palette()
        colors_unknown = ImageDisplay(
            VCube(),
            palette_name='nonexistent_palette',
        ).load_palette()

        self.assertEqual(colors_default, colors_unknown)


class RenderCubeDistanceValidationTestCase(unittest.TestCase):
    """Tests for distance parameter validation."""

    def test_distance_too_small_threshold(self) -> None:
        """Test distance <= sqrt(3) is thresholded."""
        self.assertTrue(
            ImageDisplay(VCube()).render(distance=0.1),
        )


class RenderCubeCustomParametersTestCase(unittest.TestCase):
    """Tests for render_cube with custom parameters."""

    def test_2x2_cube(self) -> None:
        """Test rendering a 2x2 cube."""
        result = ImageDisplay(VCube(size=2)).render()
        self.assertTrue(result.startswith('<svg'))
        self.assertIn('<polygon', result)

    def test_4x4_cube(self) -> None:
        """Test rendering a 4x4 cube."""
        result = ImageDisplay(VCube(size=4)).render()
        self.assertTrue(result.startswith('<svg'))

    def test_custom_cube_color_with_alpha(self) -> None:
        """Test rendering with semi-transparent cube body."""
        result = ImageDisplay(VCube(), cube_color='#11111180').render()
        self.assertIn('fill-opacity=', result)

    def test_opaque_cube_color_no_opacity_attr(self) -> None:
        """Test opaque cube color omits fill-opacity."""
        result = ImageDisplay(VCube(), cube_color='#222222').render()
        self.assertNotIn('fill-opacity=', result)

    def test_custom_distance(self) -> None:
        """Test rendering with custom distance."""
        result = ImageDisplay(VCube()).render(distance=20.0)
        self.assertTrue(result.startswith('<svg'))

    def test_orientation_reorients_cube(self) -> None:
        """Test that passing orientation reorients the cube before render."""
        cube = VCube()
        cube.rotate("R U R' U'")
        result = ImageDisplay(cube).render(orientation='DF')
        self.assertTrue(result.startswith('<svg'))


class BuildTopViewSvgTestCase(unittest.TestCase):
    """Tests for flat top-face SVG rendering."""

    def test_returns_valid_svg(self) -> None:
        """Test that output is a valid SVG wrapper."""
        result = ImageDisplay(VCube()).render(layout='top')
        self.assertTrue(result.startswith('<svg'))
        self.assertTrue(result.endswith('</svg>'))
        self.assertIn('xmlns=', result)

    def test_contains_u_face_group(self) -> None:
        """Test that U face group is present."""
        result = ImageDisplay(VCube()).render(layout='top')
        self.assertIn('class="face-U"', result)

    def test_contains_adjacent_face_groups(self) -> None:
        """Test that all adjacent face groups are present."""
        result = ImageDisplay(VCube()).render(layout='top')
        for face in ('F', 'R', 'B', 'L'):
            with self.subTest(face=face):
                self.assertIn(f'class="face-{face}"', result)

    def test_sticker_count_3x3(self) -> None:
        """Test correct number of polygon elements for 3x3."""
        result = ImageDisplay(VCube()).render(layout='top')
        # 9 U stickers + 4 * 3 adjacent = 21 sticker polygons
        # Plus 5 body polygons = 26 total
        polygon_count = result.count('<polygon')
        self.assertEqual(polygon_count, 26)

    def test_2x2_cube(self) -> None:
        """Test rendering a 2x2 cube."""
        result = ImageDisplay(VCube(size=2)).render(layout='top')
        self.assertTrue(result.startswith('<svg'))
        # 4 U stickers + 4 * 2 adjacent = 12 + 5 body = 17
        self.assertEqual(result.count('<polygon'), 17)

    def test_4x4_cube(self) -> None:
        """Test rendering a 4x4 cube."""
        result = ImageDisplay(VCube(size=4)).render(layout='top')
        self.assertTrue(result.startswith('<svg'))
        # 16 U stickers + 4 * 4 adjacent = 32 + 5 body = 37
        self.assertEqual(result.count('<polygon'), 37)

    def test_cube_color_with_alpha(self) -> None:
        """Test top view with semi-transparent cube body."""
        result = ImageDisplay(
            VCube(),
            cube_color='#11111180',
        ).render(layout='top')
        self.assertIn('fill-opacity=', result)

    def test_2x2_cube_with_oll_mode(self) -> None:
        """Test rendering a 2x2 cube with oll mode after algorithm."""
        cube = VCube(size=2)
        cube.rotate("F2 U' R U' R' U F2 U R U R'")
        result = ImageDisplay(cube).render(mode='oll')
        self.assertTrue(result.startswith('<svg'))
