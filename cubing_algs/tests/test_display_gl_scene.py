"""Tests for the scene of the GPU rendering backend."""
import struct
import unittest

from cubing_algs.constants import FACE_ORDER
from cubing_algs.display.gl.geometry import FACE_BASES
from cubing_algs.display.gl.geometry import Cubie
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.scene import FACE_LAYOUTS
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.scene import MASKED_KEY
from cubing_algs.display.gl.scene import ORIENTED_KEY
from cubing_algs.display.gl.scene import PLASTIC_KEY
from cubing_algs.display.gl.scene import SIDE_NUMBER
from cubing_algs.display.gl.scene import CubieInstance
from cubing_algs.display.gl.scene import axis_direction
from cubing_algs.display.gl.scene import build_color
from cubing_algs.display.gl.scene import build_colors
from cubing_algs.display.gl.scene import build_face_layout
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.display.gl.scene import cubie_colors
from cubing_algs.display.gl.scene import cubie_hidden
from cubing_algs.display.gl.scene import dim_color
from cubing_algs.display.gl.scene import facelet_index
from cubing_algs.display.gl.scene import grid_position
from cubing_algs.display.gl.scene import resolve_display
from cubing_algs.display.gl.scene import sticker_color
from cubing_algs.display.gl.transforms import AXIS_X
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import AXIS_Z
from cubing_algs.display.gl.transforms import ORIGIN
from cubing_algs.display.gl.transforms import Mat4
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import ImageDisplay
from cubing_algs.display.mode import MODE_CONFIGS
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

# A mask showing every facelet of a 3x3x3.
VISIBLE = '1' * 54


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


class TestDimColor(unittest.TestCase):
    """Tests for dim_color function."""

    def test_darkens_without_shifting_the_hue(self) -> None:
        """Test that a dimmed color keeps its hue and loses lightness."""
        dimmed = dim_color(build_color('#ff0000'))

        self.assertEqual(dimmed[1], dimmed[2])
        self.assertLess(dimmed[0], 1.0)
        self.assertGreater(dimmed[0], 0.0)

    def test_black_stays_black(self) -> None:
        """Test that dimming what has no lightness changes nothing."""
        self.assertEqual(dim_color((0.0, 0.0, 0.0)), (0.0, 0.0, 0.0))

    def test_matches_the_svg_backend(self) -> None:
        """Test that both backends dim a facelet to the same color."""
        display = ImageDisplay(cube_of())

        for face in FACE_ORDER:
            with self.subTest(face=face):
                self.assertEqual(
                    dim_color(build_color(display.palette[face])),
                    build_color(display.get_sticker_fill(face, '0')),
                )


class TestStickerColor(unittest.TestCase):
    """Tests for sticker_color function."""

    def setUp(self) -> None:
        """Load the colors of the default palette."""
        self.colors = build_colors(ImageDisplay(cube_of()).palette)

    def test_every_code(self) -> None:
        """Test that each mask code picks the color it stands for."""
        cases = (
            ('1', self.colors['U']),
            ('0', dim_color(self.colors['U'])),
            ('2', self.colors[MASKED_KEY]),
            ('3', self.colors[PLASTIC_KEY]),
            ('4', self.colors[ORIENTED_KEY]),
        )

        for code, expected in cases:
            with self.subTest(code=code):
                self.assertEqual(
                    sticker_color('U', code, self.colors),
                    expected,
                )

    def test_matches_the_svg_backend(self) -> None:
        """Test that both backends resolve every code the same way."""
        display = ImageDisplay(cube_of())

        for face in FACE_ORDER:
            for code in '01234':
                with self.subTest(face=face, code=code):
                    self.assertEqual(
                        sticker_color(face, code, self.colors),
                        build_color(display.get_sticker_fill(face, code)),
                    )


class TestCubieHidden(unittest.TestCase):
    """Tests for cubie_hidden function."""

    def test_a_shown_cubie_stays(self) -> None:
        """Test that a cubie of a plain mask is kept."""
        self.assertFalse(cubie_hidden(Cubie(2, 2, 2, ORIGIN), VISIBLE, 3))

    def test_a_wholly_hidden_cubie_goes(self) -> None:
        """Test that a cubie hidden on every side is dropped."""
        self.assertTrue(cubie_hidden(Cubie(2, 2, 2, ORIGIN), '3' * 54, 3))

    def test_a_partly_hidden_cubie_stays(self) -> None:
        """Test that one hidden sticker does not remove the whole piece."""
        # Only the up facelet of the up right front corner is hidden.
        mask = VISIBLE[:8] + '3' + VISIBLE[9:]

        self.assertFalse(cubie_hidden(Cubie(2, 2, 2, ORIGIN), mask, 3))

    def test_the_buried_sides_are_ignored(self) -> None:
        """Test that a center is judged on the only facelet it shows."""
        mask = VISIBLE[:4] + '3' + VISIBLE[5:]

        self.assertTrue(cubie_hidden(Cubie(1, 2, 1, ORIGIN), mask, 3))
        self.assertFalse(cubie_hidden(Cubie(1, 0, 1, ORIGIN), mask, 3))


class TestCubieColors(unittest.TestCase):
    """Tests for cubie_colors function."""

    def test_corner_shows_three_stickers(self) -> None:
        """Test that a corner is colored on three sides only."""
        cube = cube_of()
        colors = build_colors(ImageDisplay(cube).palette)

        sides = cubie_colors(
            Cubie(2, 2, 2, ORIGIN),
            cube.state,
            VISIBLE,
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
                    len(cubie_colors(cubie, cube.state, VISIBLE, colors, 3)),
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
                    cubie_colors(
                        instance.cubie, cube.state, VISIBLE, colors, 3,
                    ),
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


class TestBuildSceneMasks(unittest.TestCase):
    """Tests for the modes and the masks of a scene."""

    def assert_matches_svg(
            self,
            cube: VCube,
            mode: str = '',
            mask: str = '',
    ) -> None:
        """Check a scene facelet by facelet against the SVG backend."""
        display = ImageDisplay(cube)
        mode_mask, _, orientation = display.resolve_mode(mode)

        shown = cube

        if orientation:
            shown = cube.oriented_copy(orientation, full=True)

        codes = display.map_mask(shown, mask or mode_mask)
        size = cube.size

        for instance in build_scene(cube, mode=mode, mask=mask).instances:
            for face in range(SIDE_NUMBER):
                index = facelet_index(face, instance.cubie, size)

                if index is None:
                    continue

                with self.subTest(cubie=instance.cubie, face=FACE_ORDER[face]):
                    self.assertEqual(
                        instance.colors[face],
                        build_color(
                            display.get_sticker_fill(
                                shown.state[index],
                                codes[index],
                            ),
                        ),
                    )

    def test_every_mode_shows_what_the_svg_shows(self) -> None:
        """Test that both backends mask exactly the same pieces."""
        cube = cube_of("R U R' U' F R U R' U' F'")

        for mode in MODE_CONFIGS:
            with self.subTest(mode=mode):
                self.assert_matches_svg(cube, mode)

    def test_an_explicit_mask_is_followed(self) -> None:
        """Test that a mask given by hand reaches the stickers."""
        self.assert_matches_svg(cube_of(), mask='0' * 54)

    def test_a_mask_overrides_the_mode(self) -> None:
        """Test that a mask given by hand wins over the one of a mode."""
        cube = cube_of()

        self.assertEqual(
            build_scene(cube, mode='oll', mask='2' * 54).instances,
            build_scene(cube, mask='2' * 54).instances,
        )

    def test_an_unknown_mode_shows_the_whole_cube(self) -> None:
        """Test that a mode nobody knows masks nothing."""
        cube = cube_of()

        self.assertEqual(
            build_scene(cube, mode='nope').instances,
            build_scene(cube).instances,
        )

    def test_the_mode_is_case_insensitive(self) -> None:
        """Test that a mode is resolved whatever its case."""
        cube = cube_of()

        self.assertEqual(
            build_scene(cube, mode='OLL').instances,
            build_scene(cube, mode='oll').instances,
        )

    def test_a_mode_reorients_the_cube(self) -> None:
        """Test that the orientation of a mode reaches the scene."""
        cube = cube_of("L U L' U'")
        orientation = ImageDisplay(cube).resolve_mode('f2l')[2]

        self.assertEqual(orientation, 'UB')

        oriented = cube.oriented_copy(orientation, full=True)
        colors = build_colors(ImageDisplay(cube).palette)
        scene = build_scene(cube, mode='f2l')

        center = next(
            instance
            for instance in scene.instances
            if instance.cubie[:3] == (2, 1, 1)
        )

        self.assertNotEqual(oriented.state[13], cube.state[13])
        self.assertEqual(center.colors[1], colors[oriented.state[13]])

    def test_a_dimmed_mode_darkens_the_stickers(self) -> None:
        """Test that the dimmed code comes out darker than the palette."""
        colors = build_colors(ImageDisplay(cube_of()).palette)
        scene = build_scene(cube_of(), mode='dimmed')

        for instance in scene.instances:
            for face in range(SIDE_NUMBER):
                if facelet_index(face, instance.cubie, 3) is None:
                    continue

                with self.subTest(cubie=instance.cubie, face=face):
                    self.assertEqual(
                        instance.colors[face],
                        dim_color(colors[FACE_ORDER[face]]),
                    )

    def test_the_hidden_mode_empties_the_cube(self) -> None:
        """Test that hiding every piece leaves nothing to draw."""
        self.assertEqual(build_scene(cube_of(), mode='hidden').instances, ())

    def test_a_hidden_piece_leaves_a_hole(self) -> None:
        """Test that one hidden piece is the only one dropped."""
        mask = VISIBLE[:4] + '3' + VISIBLE[5:]
        scene = build_scene(cube_of(), mask=mask)

        self.assertEqual(len(scene.instances), 25)
        self.assertNotIn(
            (1, 2, 1),
            [instance.cubie[:3] for instance in scene.instances],
        )

    def test_a_mode_on_a_bigger_cube(self) -> None:
        """Test that a mode is scaled to the size of the cube."""
        for size in (2, 5):
            with self.subTest(size=size):
                self.assert_matches_svg(cube_of(size=size), 'oll')


class TestResolveDisplay(unittest.TestCase):
    """Tests for the settling of a display mode."""

    def test_no_mode_leaves_everything_alone(self) -> None:
        """Test that a plain cube is neither turned nor masked."""
        cube = cube_of("R U R' U'")
        shown, mask = resolve_display(cube)

        self.assertIs(shown, cube)
        self.assertEqual(mask, '')

    def test_a_mode_hands_its_mask_over(self) -> None:
        """Test that the mask of a mode comes out unreplayed."""
        cube = cube_of()
        _, mask = resolve_display(cube, mode='oll')

        self.assertEqual(mask, ImageDisplay(cube).resolve_mode('oll')[0])

    def test_a_mode_reorients_the_cube(self) -> None:
        """Test that a mode may hand back another cube than it was given."""
        cube = cube_of("L U L' U'")
        shown, _ = resolve_display(cube, mode='f2l')

        self.assertIsNot(shown, cube)
        self.assertEqual(
            shown.state,
            cube.oriented_copy('UB', full=True).state,
        )

    def test_a_mask_wins_over_the_mode(self) -> None:
        """Test that a mask given by hand replaces the one of the mode."""
        self.assertEqual(
            resolve_display(cube_of(), mode='oll', mask=VISIBLE)[1],
            VISIBLE,
        )
