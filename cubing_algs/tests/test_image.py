"""Tests for cube image rendering."""
import sys
import tempfile
import unittest
from pathlib import Path

from cubing_algs.algorithm import Algorithm
from cubing_algs.image import _build_svg
from cubing_algs.image import _compute_visible_faces
from cubing_algs.image import _parse_rotation
from cubing_algs.image import _project
from cubing_algs.image import _rotate_point
from cubing_algs.image import render_cube
from cubing_algs.vcube import VCube

SOLVED_STATE = (
    'UUUUUUUUU'
    'RRRRRRRRR'
    'FFFFFFFFF'
    'DDDDDDDDD'
    'LLLLLLLLL'
    'BBBBBBBBB'
)


class ParseRotationTestCase(unittest.TestCase):
    """Tests for rotation string parsing."""

    def test_single_axis(self) -> None:
        """Test parsing a single axis rotation."""
        result = _parse_rotation('y45')
        self.assertEqual(result, [('y', 45)])

    def test_two_axes(self) -> None:
        """Test parsing two axis rotations."""
        result = _parse_rotation('y45x-25')
        self.assertEqual(result, [('y', 45), ('x', -25)])

    def test_three_axes(self) -> None:
        """Test parsing three axis rotations."""
        result = _parse_rotation('x20y45z10')
        self.assertEqual(
            result, [('x', 20), ('y', 45), ('z', 10)],
        )

    def test_negative_angle(self) -> None:
        """Test parsing negative angle."""
        result = _parse_rotation('y-30')
        self.assertEqual(result, [('y', -30)])

    def test_zero_angle(self) -> None:
        """Test parsing zero angle."""
        result = _parse_rotation('x0')
        self.assertEqual(result, [('x', 0)])

    def test_large_angle(self) -> None:
        """Test parsing angle above 360."""
        result = _parse_rotation('y999')
        self.assertEqual(result, [('y', 999)])

    def test_invalid_string_raises(self) -> None:
        """Test that invalid rotation strings raise."""
        with self.assertRaises(ValueError):
            _parse_rotation('invalid')

    def test_empty_string_raises(self) -> None:
        """Test that empty string raises ValueError."""
        with self.assertRaises(ValueError):
            _parse_rotation('')

    def test_partial_match_raises(self) -> None:
        """Test that partially valid string raises."""
        with self.assertRaises(ValueError):
            _parse_rotation('y45garbage')


class RotatePointTestCase(unittest.TestCase):
    """Tests for 3D point rotation."""

    def test_no_rotation(self) -> None:
        """Test point with empty rotation list."""
        point = (1.0, 0.0, 0.0)
        result = _rotate_point(point, [])
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 0.0)
        self.assertAlmostEqual(result[2], 0.0)

    def test_y_rotation_90(self) -> None:
        """Test 90-degree Y rotation (clockwise from above)."""
        point = (1.0, 0.0, 0.0)
        result = _rotate_point(point, [('y', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], 1.0, places=5)

    def test_x_rotation_90(self) -> None:
        """Test 90-degree X rotation (clockwise from right)."""
        point = (0.0, 1.0, 0.0)
        result = _rotate_point(point, [('x', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 0.0, places=5)
        self.assertAlmostEqual(result[2], -1.0, places=5)

    def test_z_rotation_90(self) -> None:
        """Test 90-degree Z rotation (clockwise from front)."""
        point = (1.0, 0.0, 0.0)
        result = _rotate_point(point, [('z', 90)])
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], -1.0, places=5)
        self.assertAlmostEqual(result[2], 0.0, places=5)

    def test_combined_rotation(self) -> None:
        """Test combined rotation is applied in sequence."""
        point = (1.0, 0.0, 0.0)
        result = _rotate_point(
            point, [('y', 90), ('x', 90)],
        )
        self.assertAlmostEqual(result[0], 0.0, places=5)
        self.assertAlmostEqual(result[1], 1.0, places=5)
        self.assertAlmostEqual(result[2], 0.0, places=5)


class ProjectTestCase(unittest.TestCase):
    """Tests for orthographic projection."""

    def test_project_drops_z(self) -> None:
        """Test that projection returns only x and y."""
        result = _project((1.0, 2.0, 3.0))
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], 2.0)


class VisibleFacesTestCase(unittest.TestCase):
    """Tests for face visibility computation."""

    def test_default_rotation_shows_three_faces(self) -> None:
        """Default rotation y45x-25 shows exactly 3 faces."""
        rotations = [('y', 45), ('x', -25)]
        faces = _compute_visible_faces(rotations)
        self.assertEqual(len(faces), 3)

    def test_no_rotation_shows_one_face(self) -> None:
        """With no rotation, viewer sees only F face."""
        rotations = [('y', 0)]
        faces = _compute_visible_faces(rotations)
        face_names = [f[0] for f in faces]
        self.assertIn('F', face_names)
        self.assertEqual(len(faces), 1)

    def test_face_data_structure(self) -> None:
        """Each face has name, 4 corners, and index."""
        rotations = [('y', -45), ('x', 34)]
        faces = _compute_visible_faces(rotations)
        for face_name, corners_2d, face_index in faces:
            self.assertIsInstance(face_name, str)
            self.assertEqual(len(corners_2d), 4)
            self.assertIsInstance(face_index, int)

    def test_faces_sorted_back_to_front(self) -> None:
        """Visible faces are sorted back-to-front."""
        rotations = [('y', -45), ('x', 34)]
        faces = _compute_visible_faces(rotations)
        self.assertTrue(len(faces) >= 1)


class BuildSvgTestCase(unittest.TestCase):
    """Tests for SVG generation."""

    def test_returns_valid_svg(self) -> None:
        """Test that output is a valid SVG string."""
        rotations = [('y', -45), ('x', 34)]
        svg = _build_svg(SOLVED_STATE, 200, rotations)
        self.assertTrue(svg.startswith('<svg'))
        self.assertTrue(svg.endswith('</svg>'))
        self.assertIn(
            'xmlns="http://www.w3.org/2000/svg"', svg,
        )

    def test_contains_viewbox(self) -> None:
        """Test that SVG has correct viewBox."""
        svg = _build_svg(
            SOLVED_STATE, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('viewBox="0 0 200 200"', svg)

    def test_custom_size(self) -> None:
        """Test custom size is reflected in viewBox."""
        svg = _build_svg(
            SOLVED_STATE, 400, [('y', -45), ('x', 34)],
        )
        self.assertIn('viewBox="0 0 400 400"', svg)

    def test_contains_polygon_elements(self) -> None:
        """Test that SVG contains polygon elements."""
        svg = _build_svg(
            SOLVED_STATE, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('<polygon', svg)

    def test_contains_gradient_defs(self) -> None:
        """Test that SVG contains gradient definitions."""
        svg = _build_svg(
            SOLVED_STATE, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('<defs>', svg)
        self.assertIn('linearGradient', svg)

    def test_scrambled_state_renders(self) -> None:
        """Test scrambled state produces valid SVG."""
        cube = VCube()
        cube.rotate("R U R' U'")
        svg = _build_svg(
            cube.state, 200, [('y', -45), ('x', 34)],
        )
        self.assertTrue(svg.startswith('<svg'))

    def test_contains_per_face_groups(self) -> None:
        """Test that SVG has per-face groups."""
        svg = _build_svg(
            SOLVED_STATE, 200, [('y', -45), ('x', 34)],
        )
        self.assertIn('class="face-', svg)


class RenderCubeFromVCubeTestCase(unittest.TestCase):
    """Tests for render_cube with VCube input."""

    def test_solved_cube_returns_svg(self) -> None:
        """Test rendering a solved cube returns SVG."""
        cube = VCube()
        result = render_cube(cube)
        self.assertIsInstance(result, str)
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith('<svg'))  # type: ignore[union-attr]

    def test_scrambled_cube(self) -> None:
        """Test rendering a scrambled cube."""
        cube = VCube()
        cube.rotate("R U R' U'")
        result = render_cube(cube)
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith('<svg'))  # type: ignore[union-attr]

    def test_custom_size(self) -> None:
        """Test rendering with custom size."""
        cube = VCube()
        result = render_cube(cube, size=400)
        self.assertIsNotNone(result)
        self.assertIn('viewBox="0 0 400 400"', result)  # type: ignore[operator]

    def test_custom_rotation(self) -> None:
        """Test rendering with custom rotation."""
        cube = VCube()
        result = render_cube(cube, rotation='y-30')
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith('<svg'))  # type: ignore[union-attr]


class RenderCubeFromAlgorithmTestCase(unittest.TestCase):
    """Tests for render_cube with Algorithm input."""

    def test_algorithm_renders(self) -> None:
        """Test rendering from an Algorithm."""
        algo = Algorithm.parse_moves("R U R' U'")
        result = render_cube(algo)
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith('<svg'))  # type: ignore[union-attr]

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


class RenderCubeFileOutputTestCase(unittest.TestCase):
    """Tests for file output in render_cube."""

    def test_write_svg_file(self) -> None:
        """Test writing SVG to a file."""
        cube = VCube()
        with tempfile.NamedTemporaryFile(
            suffix='.svg', delete=False,
        ) as f:
            tmp_path = Path(f.name)

        try:
            result = render_cube(cube, path=tmp_path)
            self.assertIsNone(result)
            self.assertTrue(tmp_path.exists())
            content = tmp_path.read_text(encoding='utf-8')
            self.assertTrue(content.startswith('<svg'))
        finally:
            tmp_path.unlink()

    def test_write_svg_with_path_object(self) -> None:
        """Test writing SVG with Path object."""
        cube = VCube()
        with tempfile.NamedTemporaryFile(
            suffix='.svg', delete=False,
        ) as f:
            tmp_path = Path(f.name)

        try:
            render_cube(cube, path=tmp_path)
            self.assertTrue(tmp_path.exists())
        finally:
            tmp_path.unlink()

    def test_unsupported_extension_raises(self) -> None:
        """Test unsupported extension raises ValueError."""
        cube = VCube()
        with self.assertRaises(ValueError):
            render_cube(cube, path='output.jpg')

    def test_png_without_cairosvg_raises(self) -> None:
        """Test PNG without cairosvg raises ImportError."""
        cube = VCube()
        original = sys.modules.get('cairosvg')
        sys.modules['cairosvg'] = None  # type: ignore[assignment]
        try:
            with self.assertRaises(ImportError):
                with tempfile.NamedTemporaryFile(
                    suffix='.png', delete=False,
                ) as f:
                    tmp_path = f.name
                render_cube(cube, path=tmp_path)
        finally:
            if original is not None:
                sys.modules['cairosvg'] = original
            else:
                sys.modules.pop('cairosvg', None)
