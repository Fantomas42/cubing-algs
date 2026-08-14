"""Tests for the scene of the GPU rendering backend."""
import struct
import unittest

from cubing_algs.constants import FACE_ORDER
from cubing_algs.display.gl.geometry import FACE_BASES
from cubing_algs.display.gl.geometry import Cubie
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.scene import FACE_LAYOUTS
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.scene import PLASTIC_KEY
from cubing_algs.display.gl.scene import SIDE_NUMBER
from cubing_algs.display.gl.scene import CubieInstance
from cubing_algs.display.gl.scene import axis_direction
from cubing_algs.display.gl.scene import build_color
from cubing_algs.display.gl.scene import build_colors
from cubing_algs.display.gl.scene import build_face_layout
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.display.gl.scene import cubie_colors
from cubing_algs.display.gl.scene import facelet_index
from cubing_algs.display.gl.scene import grid_position
from cubing_algs.display.gl.transforms import AXIS_X
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import AXIS_Z
from cubing_algs.display.gl.transforms import ORIGIN
from cubing_algs.display.gl.transforms import Mat4
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import ImageDisplay
from cubing_algs.vcube import VCube

# Center cubie of each face of a 3x3x3, and the facelet it shows.
FACE_CENTERS = (
    ('U', (1, 2, 1), 4),
    ('R', (2, 1, 1), 13),
    ('F', (1, 1, 2), 22),
    ('D', (1, 0, 1), 31),
    ('L', (0, 1, 1), 40),
    ('B', (1, 1, 0), 49),
)

# The three facelets of the URF corner cubie of a 3x3x3.
CORNER_FACELETS = (
    ('U', 0, 8),
    ('R', 1, 9),
    ('F', 2, 20),
)


def cube_of(moves: str = '', size: int = 3) -> VCube:
    """
    Build the cube of a test.

    Returns:
        The cube, the moves applied.

    """
    cube = VCube(size=size)

    if moves:
        cube.rotate(moves)

    return cube


class TestAxisDirection(unittest.TestCase):
    """Tests for axis_direction function."""

    def test_every_axis(self) -> None:
        """Test that every axis and direction is named."""
        cases = (
            (AXIS_X, (0, 1)),
            (-AXIS_X, (0, -1)),
            (AXIS_Y, (1, 1)),
            (-AXIS_Y, (1, -1)),
            (AXIS_Z, (2, 1)),
            (-AXIS_Z, (2, -1)),
        )

        for vector, expected in cases:
            with self.subTest(vector=vector):
                self.assertEqual(axis_direction(vector), expected)

    def test_scaled_vector(self) -> None:
        """Test that the length of the vector does not matter."""
        self.assertEqual(axis_direction(Vec3(0.0, -4.0, 0.0)), (1, -1))

    def test_null_vector(self) -> None:
        """Test that a vector along no axis is rejected."""
        with self.assertRaises(ValueError) as context:
            axis_direction(ORIGIN)

        self.assertIn('runs along no axis', str(context.exception))


class TestFaceLayouts(unittest.TestCase):
    """Tests for the layout of the faces on the grid of cubies."""

    def test_one_layout_per_face(self) -> None:
        """Test that every face of the geometry has a layout."""
        self.assertEqual(len(FACE_LAYOUTS), len(FACE_ORDER))
        self.assertEqual(SIDE_NUMBER, len(FACE_ORDER))

    def test_layout_of_the_up_face(self) -> None:
        """Test that the up face is read from its back left corner."""
        layout = build_face_layout(FACE_BASES[0])

        self.assertEqual(layout.axis, 1)
        self.assertEqual(layout.sign, 1)
        self.assertEqual((layout.row_axis, layout.row_sign), (2, 1))
        self.assertEqual((layout.col_axis, layout.col_sign), (0, 1))

    def test_layout_of_the_right_face(self) -> None:
        """Test that the right face is read from its up front corner."""
        layout = build_face_layout(FACE_BASES[1])

        self.assertEqual(layout.axis, 0)
        self.assertEqual(layout.sign, 1)
        self.assertEqual((layout.row_axis, layout.row_sign), (1, -1))
        self.assertEqual((layout.col_axis, layout.col_sign), (2, -1))

    def test_every_layout_uses_three_axes(self) -> None:
        """Test that a face and its rows and columns are orthogonal."""
        for face, layout in zip(FACE_ORDER, FACE_LAYOUTS, strict=True):
            with self.subTest(face=face):
                self.assertEqual(
                    {layout.axis, layout.row_axis, layout.col_axis},
                    {0, 1, 2},
                )


class TestGridPosition(unittest.TestCase):
    """Tests for grid_position function."""

    def test_forward(self) -> None:
        """Test that a forward axis keeps the index."""
        self.assertEqual(grid_position(0, 1, 3), 0)
        self.assertEqual(grid_position(2, 1, 3), 2)

    def test_backward(self) -> None:
        """Test that a backward axis mirrors the index."""
        self.assertEqual(grid_position(0, -1, 3), 2)
        self.assertEqual(grid_position(2, -1, 3), 0)


class TestFaceletIndex(unittest.TestCase):
    """Tests for facelet_index function."""

    def test_face_centers(self) -> None:
        """Test that the center cubies show the center facelets."""
        for name, (x, y, z), expected in FACE_CENTERS:
            with self.subTest(face=name):
                face = FACE_ORDER.index(name)
                cubie = Cubie(x, y, z, ORIGIN)

                self.assertEqual(facelet_index(face, cubie, 3), expected)

    def test_corner_cubie(self) -> None:
        """Test the three facelets of the up right front corner."""
        cubie = Cubie(2, 2, 2, ORIGIN)

        for name, face, expected in CORNER_FACELETS:
            with self.subTest(face=name):
                self.assertEqual(facelet_index(face, cubie, 3), expected)

    def test_buried_sides(self) -> None:
        """Test that a side inside the cube shows no facelet."""
        cubie = Cubie(0, 2, 0, ORIGIN)

        # Up, left and back are on the surface, the others are not.
        self.assertIsNotNone(facelet_index(0, cubie, 3))
        self.assertIsNone(facelet_index(1, cubie, 3))
        self.assertIsNone(facelet_index(2, cubie, 3))
        self.assertIsNone(facelet_index(3, cubie, 3))
        self.assertIsNotNone(facelet_index(4, cubie, 3))
        self.assertIsNotNone(facelet_index(5, cubie, 3))

    def test_every_facelet_is_shown_once(self) -> None:
        """Test that the cubies cover the whole state string, once."""
        for size in range(2, 8):
            with self.subTest(size=size):
                geometry = build_cube_geometry(size)

                indexes = [
                    index
                    for cubie in geometry.cubies
                    for face in range(SIDE_NUMBER)
                    if (index := facelet_index(face, cubie, size)) is not None
                ]

                self.assertEqual(len(indexes), len(set(indexes)))
                self.assertEqual(
                    sorted(indexes),
                    list(range(SIDE_NUMBER * size * size)),
                )

    def test_matches_the_state_of_a_solved_cube(self) -> None:
        """Test that a solved cube shows its own face letter everywhere."""
        for size in (2, 3, 5):
            with self.subTest(size=size):
                cube = cube_of(size=size)
                geometry = build_cube_geometry(size)

                for cubie in geometry.cubies:
                    for face, letter in enumerate(FACE_ORDER):
                        index = facelet_index(face, cubie, size)

                        if index is not None:
                            self.assertEqual(cube.state[index], letter)


class TestColors(unittest.TestCase):
    """Tests for the conversion of a palette into colors."""

    def test_hexadecimal(self) -> None:
        """Test that a hex color becomes three channels."""
        self.assertEqual(build_color('#ff0000'), (1.0, 0.0, 0.0))
        self.assertEqual(build_color('#000000'), (0.0, 0.0, 0.0))

    def test_short_hexadecimal(self) -> None:
        """Test that a three digits color is expanded."""
        self.assertEqual(build_color('#0f0'), (0.0, 1.0, 0.0))

    def test_alpha_is_dropped(self) -> None:
        """Test that the cube stays opaque whatever the palette says."""
        self.assertEqual(build_color('#ff000080'), (1.0, 0.0, 0.0))

    def test_whole_palette(self) -> None:
        """Test that every entry of a palette is converted."""
        colors = build_colors({'U': '#ffffff', PLASTIC_KEY: '#000000'})

        self.assertEqual(
            colors,
            {'U': (1.0, 1.0, 1.0), PLASTIC_KEY: (0.0, 0.0, 0.0)},
        )


class TestCubieColors(unittest.TestCase):
    """Tests for cubie_colors function."""

    def test_corner_shows_three_stickers(self) -> None:
        """Test that a corner is colored on three sides only."""
        cube = cube_of()
        colors = build_colors(ImageDisplay(cube).palette)

        sides = cubie_colors(
            Cubie(2, 2, 2, ORIGIN),
            cube.state,
            colors,
            3,
        )

        self.assertEqual(sides[0], colors['U'])
        self.assertEqual(sides[1], colors['R'])
        self.assertEqual(sides[2], colors['F'])
        self.assertEqual(sides[3], colors[PLASTIC_KEY])
        self.assertEqual(sides[4], colors[PLASTIC_KEY])
        self.assertEqual(sides[5], colors[PLASTIC_KEY])

    def test_every_cubie_has_six_colors(self) -> None:
        """Test that a cubie always carries six colors."""
        cube = cube_of()
        colors = build_colors(ImageDisplay(cube).palette)

        for cubie in build_cube_geometry(3).cubies:
            with self.subTest(cubie=(cubie.x, cubie.y, cubie.z)):
                self.assertEqual(
                    len(cubie_colors(cubie, cube.state, colors, 3)),
                    SIDE_NUMBER,
                )


class TestCubieInstance(unittest.TestCase):
    """Tests for CubieInstance class."""

    def test_packing(self) -> None:
        """Test that an instance is serialized as the format says."""
        instance = CubieInstance(
            cubie=Cubie(0, 0, 0, ORIGIN),
            model=Mat4.translation(Vec3(1.0, 2.0, 3.0)),
            colors=tuple((0.5, 0.25, 0.125) for _ in range(SIDE_NUMBER)),
        )

        packed = instance.pack()

        self.assertEqual(len(packed), INSTANCE_SIZE)

        values = struct.unpack('<34f', packed)

        self.assertEqual(values[:16], tuple(instance.model.values))
        self.assertEqual(values[16:19], (0.5, 0.25, 0.125))
        self.assertEqual(values[31:], (0.5, 0.25, 0.125))


class TestBuildScene(unittest.TestCase):
    """Tests for build_scene function."""

    def test_one_instance_per_visible_cubie(self) -> None:
        """Test that the scene draws every visible cubie, and only them."""
        for size in (2, 3, 5):
            with self.subTest(size=size):
                scene = build_scene(cube_of(size=size))

                self.assertEqual(scene.size, size)
                self.assertEqual(
                    len(scene.instances),
                    size ** 3 - max(size - 2, 0) ** 3,
                )

    def test_model_places_the_cubie(self) -> None:
        """Test that an instance is translated to the center of its cubie."""
        scene = build_scene(cube_of())

        for instance in scene.instances:
            with self.subTest(cubie=instance.cubie):
                self.assertEqual(
                    instance.model,
                    Mat4.translation(instance.cubie.center),
                )

    def test_colors_follow_the_state(self) -> None:
        """Test that a scrambled cube colors its stickers accordingly."""
        cube = cube_of("R U R' U'")
        scene = build_scene(cube)
        colors = build_colors(ImageDisplay(cube).palette)

        for instance in scene.instances:
            with self.subTest(cubie=instance.cubie):
                self.assertEqual(
                    instance.colors,
                    cubie_colors(instance.cubie, cube.state, colors, 3),
                )

    def test_palette_is_the_one_of_the_svg_backend(self) -> None:
        """Test that both backends resolve the colors the same way."""
        cube = cube_of()
        scene = build_scene(cube, 'pastel')
        expected = build_color(ImageDisplay(cube, 'pastel').palette['U'])

        self.assertEqual(scene.instances[-1].colors[0], expected)
        self.assertEqual(
            scene.plastic,
            build_color(ImageDisplay(cube, 'pastel').palette[PLASTIC_KEY]),
        )

    def test_palettes_differ(self) -> None:
        """Test that changing the palette changes the scene."""
        cube = cube_of()

        self.assertNotEqual(
            build_scene(cube, 'pastel').instances[-1].colors,
            build_scene(cube).instances[-1].colors,
        )

    def test_geometry_can_be_given(self) -> None:
        """Test that a geometry built once can be reused."""
        geometry = build_cube_geometry(3)
        scene = build_scene(cube_of(), geometry=geometry)

        self.assertIs(scene.geometry, geometry)

    def test_packing_every_instance(self) -> None:
        """Test that the instance buffer holds them all, in order."""
        scene = build_scene(cube_of())
        packed = scene.pack_instances()

        self.assertEqual(len(packed), len(scene.instances) * INSTANCE_SIZE)
        self.assertTrue(packed.startswith(scene.instances[0].pack()))
