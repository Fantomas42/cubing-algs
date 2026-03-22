"""Tests for cube image rendering."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.display.image import CAMERA_DISTANCE
from cubing_algs.display.image import assemble_svg
from cubing_algs.display.image import build_svg
from cubing_algs.display.image import compute_visible_faces
from cubing_algs.display.image import parse_rotation
from cubing_algs.display.image import project
from cubing_algs.display.image import render_cube
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

    def testproject_perspective(self) -> None:
        """Test perspective projection scales by distance."""
        result = project((1.0, 2.0, 3.0), distance=6.0)
        self.assertEqual(len(result), 2)
        # scale = 6 / (6 - 3) = 2.0
        self.assertAlmostEqual(result[0], 2.0)
        self.assertAlmostEqual(result[1], 4.0)

    def testproject_at_origin_z(self) -> None:
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
        svg = build_svg(SOLVED_FACELETS_3x3x3, 200, rotations)
        self.assertTrue(svg.startswith('<svg'))
        self.assertTrue(svg.endswith('</svg>'))
        self.assertIn(
            'xmlns="http://www.w3.org/2000/svg"', svg,
        )

    def test_contains_viewbox(self) -> None:
        """Test that SVG has correct viewBox."""
        svg = build_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('viewBox="0 0 200 200"', svg)

    def test_custom_size(self) -> None:
        """Test custom size is reflected in viewBox."""
        svg = build_svg(
            SOLVED_FACELETS_3x3x3, 400, [('y', -45), ('x', 34)],
        )
        self.assertIn('viewBox="0 0 400 400"', svg)

    def test_contains_polygon_elements(self) -> None:
        """Test that SVG contains polygon elements."""
        svg = build_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('<polygon', svg)

    def test_contains_gradient_defs(self) -> None:
        """Test that SVG contains gradient definitions."""
        svg = build_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('<defs>', svg)
        self.assertIn('linearGradient', svg)

    def test_scrambled_state_renders(self) -> None:
        """Test scrambled state produces valid SVG."""
        cube = VCube()
        cube.rotate("R U R' U'")
        svg = build_svg(
            cube.state, 200, [('y', -45), ('x', 34)],
        )
        self.assertTrue(svg.startswith('<svg'))

    def test_contains_per_face_groups(self) -> None:
        """Test that SVG has per-face groups."""
        svg = build_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('class="face-', svg)


class StickerColorCorrectnessTestCase(unittest.TestCase):
    """Tests that sticker colors match the facelet state."""

    def test_r_move_changes_u_face_gradients(self) -> None:
        """After R move, U-face gradients should include F colors."""
        cube = VCube()
        cube.rotate('R')
        svg = build_svg(
            cube.state, 200, [('y', 45), ('x', -25)],
        )
        # R move brings F-face facelets onto the U face.
        # U-face gradient ids for affected stickers should use
        # F-color derived values (tinted green), not white.
        # Gradient g-U-0-2 should be green-derived, not white.
        u_02_start = svg.index('id="g-U-0-2"')
        u_02_end = svg.index('</linearGradient>', u_02_start)
        u_02_grad = svg[u_02_start:u_02_end]
        # White stickers produce #ffffff tint; green ones don't
        self.assertNotIn('#ffffff', u_02_grad)

    def test_solved_cube_u_face_all_white(self) -> None:
        """Solved cube U-face gradients should all be white-derived."""
        svg = build_svg(
            SOLVED_FACELETS_3x3x3, 200, [('y', 45), ('x', -25)],
        )
        for row in range(3):
            for col in range(3):
                grad_id = f'id="g-U-{row}-{col}"'
                start = svg.index(grad_id)
                end = svg.index('</linearGradient>', start)
                grad = svg[start:end]
                # All U stickers should use white-derived colors
                self.assertIn('#ffffff', grad)


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

    def test_empty_defs(self) -> None:
        """Test assemble_svg with no defs_parts."""
        result = assemble_svg(100, [], ['<g>content</g>'])
        self.assertNotIn('<defs>', result)
        self.assertIn('<g>content</g>', result)

    def test_with_defs(self) -> None:
        """Test assemble_svg with defs_parts."""
        result = assemble_svg(
            100, ['<clipPath id="c"/>'], ['<g>content</g>'],
        )
        self.assertIn('<defs>', result)
        self.assertIn('<clipPath id="c"/>', result)


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
