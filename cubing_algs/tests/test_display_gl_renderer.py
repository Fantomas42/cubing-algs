"""
Tests for the renderer of the GPU rendering backend.

Every test here needs a real OpenGL context, and is skipped when none
can be created, as on a machine without any GPU driver.
"""
import math
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar
from unittest import mock

from cubing_algs.constants import FACE_ORDER
from cubing_algs.display.gl import animate
from cubing_algs.display.gl import render
from cubing_algs.display.gl.animation import Animation
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import AXES_COLORS
from cubing_algs.display.gl.constants import AXES_REACH
from cubing_algs.display.gl.constants import CORE_COLOR
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.context import describe
from cubing_algs.display.gl.doctor import main as doctor_main
from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.encode import encode_png
from cubing_algs.display.gl.encode import has_pillow
from cubing_algs.display.gl.geometry import AXES
from cubing_algs.display.gl.geometry import CUBE_EXTENT
from cubing_algs.display.gl.geometry import FACE_BASES
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.geometry import core_radius
from cubing_algs.display.gl.presentation import Playback
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.renderer import COLOR_CHANNELS
from cubing_algs.display.gl.renderer import AxesRenderer
from cubing_algs.display.gl.renderer import OffscreenTarget
from cubing_algs.display.gl.renderer import Renderer
from cubing_algs.display.gl.renderer import render_frames
from cubing_algs.display.gl.renderer import render_scene
from cubing_algs.display.gl.scene import build_color
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import ORIGIN
from cubing_algs.display.gl.transforms import Quat
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import ImageDisplay
from cubing_algs.vcube import VCube

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

IMAGE_SIZE = 128

# The camera every render of this module looks through.
CAMERA = OrbitCamera.from_rotation()

# Where an axis is looked at, as a share of its length: well past the
# face it comes out of for the first one, deep inside the cube for the
# second, which the depth test must hide.
AXIS_TIP = 0.9
AXIS_INSIDE = 0.3

# The GPU rounds a color channel to a byte; two units of tolerance
# absorb that, and nothing more.
COLOR_TOLERANCE = 2

# Sizes of cube the framing is checked on, and the image it is measured
# in: wide enough for a percent of the silhouette to be a few pixels.
FRAMING_SIZES = (2, 3, 4, 5, 6, 7)
FRAMING_SIZE = 256

# How much the silhouettes of two sizes may differ. Framing the box
# rather than the cube left three and a half percents between a 2x2x2
# and a 7x7x7, so this holds the property and not the noise.
FRAMING_TOLERANCE = 0.02

# Share of the image the silhouette of a cube must cover, in each
# direction: a badly framed cube would sit small in the middle.
FRAMING_COVERAGE = 0.8

# Center cubie of each face visible at the default framing, by index in
# FACE_ORDER.
VISIBLE_CENTERS = ((0, (1, 2, 1)), (1, (2, 1, 1)), (2, (1, 1, 2)))

# A look stripped of everything the light does beyond telling the faces
# apart, so that the color of a facelet can be predicted exactly. What
# each of those knobs does is checked one by one further down.
FLAT_LOOK = Look(
    ambient=0.72,
    gamma=1.0,
    groove_occlusion=0.0,
    rim_strength=0.0,
    specular_strength=0.0,
    core_specular_strength=0.0,
    core_rim_strength=0.0,
    sticker_grain=0.0,
)

# The picture most renders of this module are made through: that flat
# look, at the size the pixel probes are written for.
FLAT = Presentation(image_size=IMAGE_SIZE, look=FLAT_LOOK)

# Smaller pictures, for the tests comparing whole images rather than
# reading a pixel of them, and the pace their animations run at.
SMALL = Presentation(image_size=64)
TINY = Presentation(image_size=32, look=FLAT_LOOK)
QUICK = Playback(frame_rate=10.0, duration=0.2)


def probe_gpu() -> bool:
    """
    Tell whether this machine can create an OpenGL context.

    Returns:
        True when the GPU tests can run.

    """
    try:
        context = create_standalone_context()
    except GLContextError:  # pragma: no cover
        return False

    context.release()

    return True


GPU_AVAILABLE = probe_gpu()

requires_gpu = unittest.skipUnless(
    GPU_AVAILABLE,
    'no OpenGL context available on this machine',
)


def pixel_at(pixels: bytes, image_size: int, point: Vec3) -> tuple[int, ...]:
    """
    Read the pixel a projected point falls on.

    Args:
        pixels: The framebuffer, bottom row first.
        image_size: Width and height of the image, in pixels.
        point: The point, in normalized device coordinates.

    Returns:
        The four channels of the pixel.

    """
    col = int((point.x + 1) / 2 * image_size)
    row = int((point.y + 1) / 2 * image_size)
    offset = (row * image_size + col) * COLOR_CHANNELS

    return tuple(pixels[offset:offset + COLOR_CHANNELS])


def silhouette(pixels: bytes, image_size: int) -> tuple[int, int]:
    """
    Measure the box everything drawn in a framebuffer fits in.

    Args:
        pixels: The framebuffer, bottom row first.
        image_size: Width and height of the image, in pixels.

    Returns:
        The width and the height of the box, in pixels.

    """
    columns: set[int] = set()
    rows: set[int] = set()

    for row in range(image_size):
        for column in range(image_size):
            if pixels[(row * image_size + column) * COLOR_CHANNELS + 3]:
                columns.add(column)
                rows.add(row)

    return (
        max(columns) - min(columns) + 1,
        max(rows) - min(rows) + 1,
    )


def shaded(color: tuple[float, float, float], normal: Vec3) -> tuple[int, ...]:
    """
    Compute the color a face of the given orientation is drawn with.

    Only holds under ``FLAT_LOOK``, where nothing but the ambient and
    the diffuse terms is left.

    Args:
        color: The color of the sticker, as the palette gives it.
        normal: The direction the sticker faces, in world coordinates.

    Returns:
        The three channels of the shaded color, as bytes.

    """
    light = max(normal.dot(Vec3(*FLAT_LOOK.light_direction).normalized()), 0.0)
    factor = FLAT_LOOK.ambient + (1 - FLAT_LOOK.ambient) * light

    return tuple(round(channel * factor * 255) for channel in color)


def facelet_pixel(
        pixels: bytes,
        face: int,
        position: tuple[int, int, int],
) -> tuple[int, ...]:
    """
    Read the pixel the center of a facelet is projected onto.

    Args:
        pixels: The framebuffer, bottom row first.
        face: Index of the face, in the order of ``FACE_ORDER``.
        position: Grid indices of the cubie showing the facelet.

    Returns:
        The four channels of the pixel.

    """
    geometry = build_cube_geometry(3)
    center = next(
        cubie.center
        for cubie in geometry.cubies
        if (cubie.x, cubie.y, cubie.z) == position
    )

    return pixel_at(
        pixels,
        IMAGE_SIZE,
        OrbitCamera.from_rotation().view_projection().transform_point(
            center + FACE_BASES[face].normal.scaled(geometry.half),
        ),
    )


@requires_gpu
class TestRenderScene(unittest.TestCase):
    """Tests for the offscreen rendering of a scene."""

    context: ClassVar['moderngl.Context']
    pixels: ClassVar[bytes]

    @classmethod
    def setUpClass(cls) -> None:
        """Render a solved cube once for the whole class."""
        cls.context = create_standalone_context()
        cls.pixels = render_scene(
            build_scene(VCube()),
            OrbitCamera.from_rotation(),
            FLAT,
            context=cls.context,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the context back."""
        cls.context.release()

    def test_size_of_the_framebuffer(self) -> None:
        """Test that the whole framebuffer is read back."""
        self.assertEqual(
            len(self.pixels),
            IMAGE_SIZE * IMAGE_SIZE * COLOR_CHANNELS,
        )

    def test_background_stays_transparent(self) -> None:
        """Test that the corners of the image are left empty."""
        corners = (
            0,
            (IMAGE_SIZE - 1) * COLOR_CHANNELS,
            (IMAGE_SIZE * (IMAGE_SIZE - 1)) * COLOR_CHANNELS,
            (IMAGE_SIZE * IMAGE_SIZE - 1) * COLOR_CHANNELS,
        )

        for offset in corners:
            with self.subTest(offset=offset):
                self.assertEqual(self.pixels[offset + 3], 0)

    def test_nothing_is_drawn_on_the_ground(self) -> None:
        """
        Test that the cube stands on nothing at all.

        A contact shadow used to be laid on a ground plane at the foot
        of the cube, which read wrong as soon as the camera went below
        the horizon. Nothing is drawn there any more, so the point of
        that plane just in front of the cube must stay empty.
        """
        ground = OrbitCamera.from_rotation().view_projection().transform_point(
            Vec3(0.0, -CUBE_EXTENT, 1.4),
        )

        self.assertEqual(pixel_at(self.pixels, IMAGE_SIZE, ground)[3], 0)

    def test_the_cube_is_drawn(self) -> None:
        """Test that the middle of the image is covered by the cube."""
        middle = (IMAGE_SIZE * IMAGE_SIZE // 2 + IMAGE_SIZE // 2)

        self.assertEqual(self.pixels[middle * COLOR_CHANNELS + 3], 255)

    def test_facelets_land_where_the_camera_says(self) -> None:
        """
        Test that the visible centers show the color of their face.

        This is the whole point of the backend: the color of the palette
        must end up on the pixels the camera projects the facelet onto.
        """
        palette = ImageDisplay(VCube()).palette

        for face, position in VISIBLE_CENTERS:
            with self.subTest(face=FACE_ORDER[face]):
                pixel = facelet_pixel(self.pixels, face, position)
                expected = shaded(
                    build_color(palette[FACE_ORDER[face]]),
                    FACE_BASES[face].normal,
                )

                self.assertEqual(pixel[3], 255)

                for channel, value in enumerate(expected):
                    self.assertAlmostEqual(
                        pixel[channel],
                        value,
                        delta=COLOR_TOLERANCE,
                    )

    def test_without_antialiasing(self) -> None:
        """Test that a render with no multisampling gives the same shape."""
        pixels = render_scene(
            build_scene(VCube()),
            OrbitCamera.from_rotation(),
            replace(FLAT, look=replace(FLAT_LOOK, samples=0)),
            context=self.context,
        )

        self.assertEqual(len(pixels), len(self.pixels))

    def test_target_without_samples_is_its_own_resolve(self) -> None:
        """Test that a plain target keeps a single framebuffer."""
        target = OffscreenTarget.create(self.context, (16, 16), samples=0)

        self.assertIs(target.framebuffer, target.resolved)

        target.release()

    def test_renderer_reserves_one_instance_per_cubie(self) -> None:
        """Test that the instance buffer holds the whole cube."""
        geometry = build_cube_geometry(3)
        renderer = Renderer.create(self.context, geometry)

        self.assertEqual(
            renderer.instance_buffer.size,
            len(build_scene(VCube()).pack_instances()),
        )

        renderer.release()

    def test_a_hidden_piece_digs_a_hole(self) -> None:
        """
        Test that a hidden cubie is really gone from the image.

        The up center is dropped, and the camera sees into the shaft it
        leaves: the plastic walls of its neighbours, and the ball core at
        the bottom of them.
        """
        mask = '1' * 4 + '3' + '1' * 49
        pixels = render_scene(
            build_scene(VCube(), mask=mask),
            OrbitCamera.from_rotation(),
            FLAT,
            context=self.context,
        )

        expected = shaded(
            build_color(ImageDisplay(VCube()).palette['U']),
            FACE_BASES[0].normal,
        )
        drilled = facelet_pixel(pixels, 0, (1, 2, 1))
        intact = facelet_pixel(self.pixels, 0, (1, 2, 1))

        for channel, value in enumerate(expected):
            with self.subTest(channel=channel):
                self.assertAlmostEqual(
                    intact[channel],
                    value,
                    delta=COLOR_TOLERANCE,
                )

        self.assertGreater(
            max(
                abs(drilled[channel] - value)
                for channel, value in enumerate(expected)
            ),
            COLOR_TOLERANCE,
        )

    def test_a_hidden_piece_shows_the_core(self) -> None:
        """
        Test that a hole dug by the mask opens onto the ball core.

        The top of the core sits inside the shaft the up center leaves,
        high enough for the camera to catch it over the wall, and it is
        the only thing that can be seen there.
        """
        pixels = render_scene(
            build_scene(VCube(), mask='1' * 4 + '3' + '1' * 49),
            CAMERA,
            FLAT,
            context=self.context,
        )

        summit = pixel_at(
            pixels,
            IMAGE_SIZE,
            CAMERA.view_projection().transform_point(
                AXIS_Y.scaled(core_radius(3)),
            ),
        )

        for channel, value in enumerate(shaded(CORE_COLOR, AXIS_Y)):
            with self.subTest(channel=channel):
                self.assertAlmostEqual(
                    summit[channel],
                    value,
                    delta=COLOR_TOLERANCE,
                )

    def test_the_core_hides_under_the_pieces(self) -> None:
        """
        Test that the ball core shows nowhere on an intact cube.

        It is the inside of the cube: sunk into the plastic of the outer
        layer, it must stay behind it as long as every piece is there.
        """
        rendered = {
            tuple(self.pixels[offset:offset + COLOR_CHANNELS - 1])
            for offset in range(0, len(self.pixels), COLOR_CHANNELS)
        }

        self.assertNotIn(shaded(CORE_COLOR, AXIS_Y), rendered)

    def test_the_hidden_mode_leaves_the_core_alone(self) -> None:
        """
        Test that a cube with no piece left is still a cube.

        Every facelet masked drops every cubie, and what stays is the
        inside: a sphere, framed as the cube it sits in was.
        """
        pixels = render_scene(
            build_scene(VCube(), mode='hidden'),
            CAMERA,
            FLAT,
            context=self.context,
        )

        middle = pixel_at(
            pixels,
            IMAGE_SIZE,
            CAMERA.view_projection().transform_point(ORIGIN),
        )

        for channel, value in enumerate(
                shaded(CORE_COLOR, CAMERA.position.normalized()),
        ):
            with self.subTest(channel=channel):
                self.assertAlmostEqual(
                    middle[channel],
                    value,
                    delta=COLOR_TOLERANCE,
                )

        width, height = silhouette(pixels, IMAGE_SIZE)
        cube_width, cube_height = silhouette(self.pixels, IMAGE_SIZE)

        self.assertLess(width, cube_width)
        self.assertLess(height, cube_height)

    def test_the_core_takes_a_highlight_of_its_own(self) -> None:
        """
        Test that the gloss of the core reaches the core, and nothing else.

        A ball seen at the bottom of a hole reads as a sphere by the
        light sliding on it, so the highlight is measured where it lands:
        the point whose normal is the half vector of the light and the
        eye must come out brighter than the very same point lit by the
        ambient and the diffuse alone. The pieces take a gloss of their
        own, so a cube with every piece in place must be untouched by it.
        """
        glossy = replace(
            FLAT_LOOK,
            core_specular_strength=0.6,
            core_specular_power=18.0,
        )

        light = Vec3(*FLAT_LOOK.light_direction).normalized()
        view = CAMERA.position.normalized()
        summit = CAMERA.view_projection().transform_point(
            (light + view).normalized().scaled(core_radius(3)),
        )

        ball = build_scene(VCube(), mode='hidden')

        matte = pixel_at(
            render_scene(ball, CAMERA, FLAT, context=self.context),
            IMAGE_SIZE,
            summit,
        )
        lit = pixel_at(
            render_scene(
                ball, CAMERA, replace(FLAT, look=glossy), context=self.context,
            ),
            IMAGE_SIZE,
            summit,
        )

        self.assertEqual(matte[3], 255)

        for channel in range(COLOR_CHANNELS - 1):
            with self.subTest(channel=channel):
                self.assertGreater(lit[channel], matte[channel])

        self.assertEqual(
            render_scene(
                build_scene(VCube()),
                OrbitCamera.from_rotation(),
                replace(FLAT, look=glossy),
                context=self.context,
            ),
            self.pixels,
        )

    def test_a_scrambled_cube_differs(self) -> None:
        """Test that the state of the cube reaches the pixels."""
        cube = VCube()
        cube.rotate("R U R' U'")

        self.assertNotEqual(
            render_scene(
                build_scene(cube),
                OrbitCamera.from_rotation(),
                FLAT,
                context=self.context,
            ),
            self.pixels,
        )


@requires_gpu
class TestInstanceUpload(unittest.TestCase):
    """Tests for what a renderer hands the GPU, and how often."""

    context: ClassVar['moderngl.Context']

    @classmethod
    def setUpClass(cls) -> None:
        """Open one context for the whole class."""
        cls.context = create_standalone_context()

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the context back."""
        cls.context.release()

    def setUp(self) -> None:
        """Build a renderer and a target to draw a solved cube into."""
        self.renderer = Renderer.create(self.context, build_cube_geometry(3))
        self.target = OffscreenTarget.create(
            self.context, (IMAGE_SIZE, IMAGE_SIZE), samples=0,
        )
        self.camera = OrbitCamera.from_rotation()
        self.scene = build_scene(VCube())

        self.target.use()

    def tearDown(self) -> None:
        """Give the GPU resources of the test back."""
        self.renderer.release()
        self.target.release()

    def test_a_still_scene_is_uploaded_once(self) -> None:
        """
        Test that redrawing the same scene rewrites no instance buffer.

        A viewer only rebuilds its scene when a move lands, so a still
        cube hands the very same one over frame after frame. Packing
        twenty-six instances in Python and uploading them is the bulk of
        what such a frame costs on the processor, and none of it buys
        anything: what is already on the GPU is what is to be drawn.
        """
        with mock.patch.object(
                self.renderer.instance_buffer, 'write',
        ) as write:
            for _ in range(10):
                self.renderer.draw(self.scene, self.camera)

        write.assert_called_once()

    def test_a_scene_that_changed_is_uploaded_again(self) -> None:
        """Test that a cube whose pieces moved reaches the GPU."""
        cube = VCube()
        cube.rotate('R')

        turned = build_scene(cube)

        with mock.patch.object(
                self.renderer.instance_buffer, 'write',
        ) as write:
            self.renderer.draw(self.scene, self.camera)
            self.renderer.draw(turned, self.camera)
            self.renderer.draw(self.scene, self.camera)

        self.assertEqual(write.call_count, 3)

    def test_the_pixels_are_the_same_either_way(self) -> None:
        """
        Test that a scene drawn twice draws the same picture twice.

        The whole safety of holding an upload back: the second frame
        must not come out of a stale buffer.
        """
        self.renderer.draw(self.scene, self.camera)
        first = self.target.read()

        self.renderer.draw(self.scene, self.camera)
        second = self.target.read()

        self.assertEqual(first, second)


@requires_gpu
class TestOrientedRender(unittest.TestCase):
    """
    Tests for the orientation an outside hand holds the cube with.

    The cube turns, the light does not: a lamp stays where it is when a
    cube is turned under it, so a face brought around must come out with
    the shade of the place it arrives at, not with the one it left.
    """

    context: ClassVar['moderngl.Context']

    @classmethod
    def setUpClass(cls) -> None:
        """Build the context every render of the class shares."""
        cls.context = create_standalone_context()

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the context back."""
        cls.context.release()

    def render_held(self, orientation: Quat) -> bytes:
        """
        Render a solved cube held in a given orientation.

        Args:
            orientation: How the whole cube is turned.

        Returns:
            The rows of RGBA pixels, bottom row first.

        """
        scene = build_scene(VCube())
        target = OffscreenTarget.create(
            self.context, (IMAGE_SIZE, IMAGE_SIZE), FLAT_LOOK.samples,
        )
        renderer = Renderer.create(self.context, scene.geometry)

        try:
            target.use()
            renderer.draw(
                scene, OrbitCamera.from_rotation(), FLAT_LOOK, orientation,
            )

            return target.read()
        finally:
            renderer.release()
            target.release()

    def assert_facelet(
            self,
            pixels: bytes,
            landing: tuple[int, tuple[int, int, int]],
            face: str,
    ) -> None:
        """
        Assert which facelet is drawn where a face center is projected.

        Args:
            pixels: The framebuffer to read.
            landing: Face index and cubie of the place looked at.
            face: Name of the face whose color must have landed there.

        """
        index, position = landing
        expected = shaded(
            build_color(ImageDisplay(VCube()).palette[face]),
            FACE_BASES[index].normal,
        )
        pixel = facelet_pixel(pixels, index, position)

        for channel, value in enumerate(expected):
            with self.subTest(channel=channel):
                self.assertAlmostEqual(
                    pixel[channel],
                    value,
                    delta=COLOR_TOLERANCE,
                )

    def test_the_identity_holds_nothing(self) -> None:
        """Test that a cube nobody holds is drawn where it stands."""
        self.assertEqual(
            self.render_held(IDENTITY),
            render_scene(
                build_scene(VCube()),
                OrbitCamera.from_rotation(),
                FLAT,
                context=self.context,
            ),
        )

    def test_a_presentation_carries_the_orientation_to_the_draw_call(
            self,
    ) -> None:
        """
        Test that an offscreen render holds the cube as a hand would.

        The orientation used to stop at ``Renderer.draw()``: nothing
        above it could ask for a PNG of the cube as a sensor holds it.
        The picture must now come out pixel for pixel identical to the
        one drawing it by hand.
        """
        held = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        self.assertEqual(
            self.render_held(held),
            render_scene(
                build_scene(VCube()),
                OrbitCamera.from_rotation(),
                replace(FLAT, orientation=held),
                context=self.context,
            ),
        )

    def test_a_quarter_turn_brings_the_front_face_around(self) -> None:
        """
        Test that turning the cube moves the faces, and only them.

        A quarter turn around Y takes the front face to where the right
        one stood, and the left one to the front. Both must come out
        shaded for where they arrive, which is what tells a normal
        turned along with the cube from one left behind.
        """
        pixels = self.render_held(Quat.from_axis_angle(AXIS_Y, math.pi / 2))

        with self.subTest(landing='right'):
            self.assert_facelet(pixels, VISIBLE_CENTERS[1], 'F')

        with self.subTest(landing='front'):
            self.assert_facelet(pixels, VISIBLE_CENTERS[2], 'L')

    def test_a_full_turn_comes_back(self) -> None:
        """Test that a cube turned all the way round is drawn as it was."""
        self.assertEqual(
            self.render_held(Quat.from_axis_angle(AXIS_Y, 2 * math.pi)),
            self.render_held(IDENTITY),
        )


@requires_gpu
class TestAxesRender(unittest.TestCase):
    """
    Tests for the three axes the viewer draws on demand.

    Nothing names them but their color, so the color reaching the pixels
    of an axis is the whole contract: red on X, green on Y, blue on Z.
    """

    context: ClassVar['moderngl.Context']
    pixels: ClassVar[bytes]
    length: ClassVar[float]

    @classmethod
    def setUpClass(cls) -> None:
        """Draw a solved cube and its axes once for the whole class."""
        cls.context = create_standalone_context()

        scene = build_scene(VCube())
        cls.length = scene.geometry.radius * AXES_REACH

        target = OffscreenTarget.create(
            cls.context, (IMAGE_SIZE, IMAGE_SIZE), 0,
        )
        renderer = Renderer.create(cls.context, scene.geometry)
        axes = AxesRenderer.create(cls.context, cls.length)

        try:
            target.use()
            renderer.draw(scene, CAMERA, FLAT_LOOK)
            axes.draw(CAMERA)

            cls.pixels = target.read()
        finally:
            axes.release()
            renderer.release()
            target.release()

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the context back."""
        cls.context.release()

    def colors_around(self, point: Vec3) -> set[tuple[int, ...]]:
        """
        Read the colors drawn around a point of an axis.

        A segment is one pixel wide, and which pixel of the two it
        straddles a rasterizer keeps is its own business: the
        neighbourhood is looked at rather than the single pixel the
        projection lands on.

        Args:
            point: The point of the axis, in world coordinates.

        Returns:
            The colors of the pixels around it, alpha included.

        """
        landing = CAMERA.view_projection().transform_point(point)

        return {
            pixel_at(
                self.pixels,
                IMAGE_SIZE,
                Vec3(
                    landing.x + column * 2 / IMAGE_SIZE,
                    landing.y + row * 2 / IMAGE_SIZE,
                    landing.z,
                ),
            )
            for row in (-1, 0, 1)
            for column in (-1, 0, 1)
        }

    def test_every_axis_carries_its_own_color(self) -> None:
        """Test that an axis is drawn where the camera projects it."""
        for index, axis in enumerate(AXES):
            with self.subTest(axis=index):
                color = tuple(
                    round(channel * 255) for channel in AXES_COLORS[index]
                )

                self.assertIn(
                    (*color, 255),
                    self.colors_around(axis.scaled(self.length * AXIS_TIP)),
                )

    def test_an_axis_stays_behind_the_cube(self) -> None:
        """
        Test that the half of an axis inside the cube stays hidden.

        The depth test is what tells which way an axis points: drawn on
        top of everything, the three of them would cross the cube and
        say nothing about the side they come out of.
        """
        for index, axis in enumerate(AXES):
            with self.subTest(axis=index):
                color = tuple(
                    round(channel * 255) for channel in AXES_COLORS[index]
                )

                self.assertNotIn(
                    (*color, 255),
                    self.colors_around(axis.scaled(self.length * AXIS_INSIDE)),
                )


@requires_gpu
class TestLook(unittest.TestCase):
    """
    Tests for the knobs shaping how the light falls on the cube.

    Each one is turned on alone, over the flat look of the other tests,
    and checked on the pixels it is meant to change: a look is a matter
    of taste, but every one of its knobs must do what it says.
    """

    context: ClassVar['moderngl.Context']
    flat: ClassVar[bytes]

    @classmethod
    def setUpClass(cls) -> None:
        """Render the flat reference the variants are compared to."""
        cls.context = create_standalone_context()
        cls.flat = cls.render(FLAT_LOOK)

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the context back."""
        cls.context.release()

    @classmethod
    def render(cls, look: Look) -> bytes:
        """
        Render the solved cube under a look.

        Args:
            look: How the light falls on the cube.

        Returns:
            The rows of RGBA pixels, bottom row first.

        """
        return render_scene(
            build_scene(VCube()),
            OrbitCamera.from_rotation(),
            replace(FLAT, look=look),
            context=cls.context,
        )

    def test_grooves_darken_the_border_of_a_sticker(self) -> None:
        """
        Test that the occlusion sinks the edges of a piece into shadow.

        The center of a facelet lies as far from any groove as a point
        can, so it must come out untouched while the corner of the very
        same sticker darkens.
        """
        pixels = self.render(replace(FLAT_LOOK, groove_occlusion=0.55))

        middle = facelet_pixel(pixels, 0, (1, 2, 1))
        reference = facelet_pixel(self.flat, 0, (1, 2, 1))

        for channel in range(3):
            with self.subTest(channel=channel):
                self.assertAlmostEqual(
                    middle[channel],
                    reference[channel],
                    delta=COLOR_TOLERANCE,
                )

        geometry = build_cube_geometry(3)
        cubie = next(
            piece for piece in geometry.cubies
            if (piece.x, piece.y, piece.z) == (1, 2, 1)
        )
        basis = FACE_BASES[0]
        corner = OrbitCamera.from_rotation().view_projection().transform_point(
            cubie.center
            + basis.normal.scaled(geometry.half)
            + basis.right.scaled(geometry.half * 0.75)
            + basis.up.scaled(geometry.half * 0.75),
        )

        self.assertLess(
            sum(pixel_at(pixels, IMAGE_SIZE, corner)[:3]),
            sum(pixel_at(self.flat, IMAGE_SIZE, corner)[:3]),
        )

    def test_the_rim_light_brightens_the_silhouette(self) -> None:
        """Test that the rim light lifts the faces grazed by the eye."""
        pixels = self.render(replace(FLAT_LOOK, rim_strength=0.5))

        self.assertGreater(
            sum(facelet_pixel(pixels, 1, (2, 1, 1))[:3]),
            sum(facelet_pixel(self.flat, 1, (2, 1, 1))[:3]),
        )

    def test_the_specular_lifts_the_lit_faces(self) -> None:
        """Test that the highlight shows on the face facing the light."""
        pixels = self.render(
            replace(FLAT_LOOK, specular_strength=0.5, specular_power=1.0),
        )

        self.assertGreater(
            sum(facelet_pixel(pixels, 0, (1, 2, 1))[:3]),
            sum(facelet_pixel(self.flat, 0, (1, 2, 1))[:3]),
        )

    def test_the_grain_breaks_the_flatness_of_a_sticker(self) -> None:
        """
        Test that the grain scatters the pixels of a single facelet.

        A flat sticker holds one and only one color; a grained one holds
        several, and the same ones from one render to the next.
        """
        look = replace(FLAT_LOOK, sticker_grain=0.2)
        pixels = self.render(look)

        self.assertNotEqual(
            facelet_pixel(pixels, 0, (1, 2, 1)),
            facelet_pixel(self.flat, 0, (1, 2, 1)),
        )
        self.assertEqual(pixels, self.render(look))

    def test_a_gamma_of_one_shades_the_color_as_it_comes(self) -> None:
        """Test that the neutral gamma really is a no-op."""
        self.assertEqual(self.render(replace(FLAT_LOOK, gamma=1.0)), self.flat)

    def test_shading_in_linear_space_changes_the_midtones(self) -> None:
        """Test that the gamma reaches the shading."""
        self.assertNotEqual(
            self.render(replace(FLAT_LOOK, gamma=2.2)),
            self.flat,
        )

    def test_the_default_look_is_the_one_a_render_gets(self) -> None:
        """Test that a render left alone is shaded by the default look."""
        self.assertEqual(
            self.render(DEFAULT_LOOK),
            render_scene(
                build_scene(VCube()),
                OrbitCamera.from_rotation(),
                Presentation(image_size=IMAGE_SIZE),
                context=self.context,
            ),
        )


@requires_gpu
class TestRender(unittest.TestCase):
    """Tests for the public rendering API."""

    def test_a_png_comes_out(self) -> None:
        """Test that a cube is rendered as a PNG of the asked size."""
        data = render(VCube(), SMALL)

        self.assertTrue(data.startswith(PNG_SIGNATURE))
        self.assertEqual(data[16:24], (64).to_bytes(4) + (64).to_bytes(4))

    def test_palette_changes_the_image(self) -> None:
        """Test that the palette reaches the rendering."""
        self.assertNotEqual(
            render(VCube(), Presentation(image_size=64, palette='pastel')),
            render(VCube(), SMALL),
        )

    def test_rotation_changes_the_image(self) -> None:
        """Test that the framing reaches the rendering."""
        self.assertNotEqual(
            render(VCube(), Presentation(image_size=64, rotation='y120x-25')),
            render(VCube(), SMALL),
        )

    def test_an_orientation_reaches_the_png(self) -> None:
        """Test that the way a cube is held changes the image written."""
        held = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        self.assertNotEqual(
            render(VCube(), replace(SMALL, orientation=held)),
            render(VCube(), SMALL),
        )

    def test_frames_on_the_radius_of_the_cube(self) -> None:
        """Test that a render frames the sphere the cube fills."""
        scene = build_scene(VCube(size=4))

        self.assertEqual(
            render(VCube(size=4), SMALL),
            encode_png(
                render_scene(
                    scene,
                    OrbitCamera.from_rotation('', 0.0, scene.geometry.radius),
                    SMALL,
                ),
                (64, 64),
            ),
        )


@requires_gpu
class TestRenderFrames(unittest.TestCase):
    """Tests for the rendering of a whole series of scenes."""

    context: ClassVar['moderngl.Context']

    @classmethod
    def setUpClass(cls) -> None:
        """Create the context shared by the whole class."""
        cls.context = create_standalone_context()

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the context back."""
        cls.context.release()

    def test_one_frame_per_scene(self) -> None:
        """Test that every scene handed over comes back as pixels."""
        animation = Animation(VCube(), "R U'", duration=0.5)
        frames = render_frames(
            animation.play(4.0),
            OrbitCamera.from_rotation(),
            TINY,
            context=self.context,
        )

        self.assertEqual(len(frames), 5)

        for frame in frames:
            self.assertEqual(len(frame), 32 * 32 * COLOR_CHANNELS)

    def test_nothing_to_draw_draws_nothing(self) -> None:
        """Test that an empty series creates no context at all."""
        self.assertEqual(
            render_frames([], OrbitCamera.from_rotation()),
            [],
        )

    def test_a_single_scene_matches_a_plain_render(self) -> None:
        """Test that the two entry points agree pixel for pixel."""
        scene = build_scene(VCube())
        camera = OrbitCamera.from_rotation()

        self.assertEqual(
            render_frames(
                [scene], camera, TINY, context=self.context,
            ),
            [
                render_scene(
                    scene, camera, TINY, context=self.context,
                ),
            ],
        )

    def test_the_frames_of_a_turn_differ(self) -> None:
        """Test that a move really moves something on screen."""
        animation = Animation(VCube(), 'R', duration=1.0)
        frames = render_frames(
            animation.play(4.0),
            OrbitCamera.from_rotation(),
            TINY,
            context=self.context,
        )

        self.assertEqual(len(set(frames)), len(frames))

    def test_a_frame_is_not_painted_over_the_last_one(self) -> None:
        """Test that the framebuffer is cleared between two frames."""
        solved = build_scene(VCube())
        turned = build_scene(VCube(), mask='3' * 54)

        first, second = render_frames(
            [turned, solved], OrbitCamera.from_rotation(), TINY,
            context=self.context,
        )
        alone, = render_frames(
            [solved], OrbitCamera.from_rotation(), TINY,
            context=self.context,
        )

        self.assertNotEqual(first, second)
        self.assertEqual(second, alone)


@requires_gpu
class TestAnimate(unittest.TestCase):
    """Tests for the public animation API."""

    def test_a_gif_comes_out(self) -> None:
        """Test that an algorithm is written as a single animation."""
        if not has_pillow():
            self.skipTest('Pillow is not installed')

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'out.gif'
            written = animate(
                VCube(), "R U'", destination,
                Presentation(image_size=32), QUICK,
            )

            self.assertEqual(written, [destination])
            self.assertTrue(destination.read_bytes().startswith(b'GIF89a'))

    def test_the_gif_holds_the_states_it_starts_and_ends_on(self) -> None:
        """Test that the two resting states are given time to be read."""
        if not has_pillow():
            self.skipTest('Pillow is not installed')

        from PIL import Image
        from PIL import ImageSequence

        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'out.gif'
            animate(
                VCube(), "R U'", destination,
                Presentation(image_size=32),
                replace(QUICK, hold_start=0.8, hold_end=1.2),
            )

            with Image.open(destination) as animation:
                delays = [
                    frame.info['duration']
                    for frame in ImageSequence.Iterator(animation)
                ]

        self.assertEqual(delays[0], 800)
        self.assertEqual(delays[-1], 1200)
        self.assertEqual(set(delays[1:-1]), {100})

    def test_frames_come_out_without_pillow(self) -> None:
        """Test that a missing Pillow costs frames, not a failure."""
        with (
                tempfile.TemporaryDirectory() as directory,
                mock.patch(
                    'cubing_algs.display.gl.api.has_pillow',
                    return_value=False,
                ),
        ):
            written = animate(
                VCube(), 'R', Path(directory) / 'out.gif',
                Presentation(image_size=32), QUICK,
            )

            self.assertEqual(len(written), 3)
            self.assertTrue(
                all(
                    path.read_bytes().startswith(PNG_SIGNATURE)
                    for path in written
                ),
            )

    def test_the_mode_reaches_the_animation(self) -> None:
        """Test that a mode changes what an animation shows."""
        with (
                tempfile.TemporaryDirectory() as directory,
                mock.patch(
                    'cubing_algs.display.gl.api.has_pillow',
                    return_value=False,
                ),
        ):
            plain = animate(
                VCube(), 'R', Path(directory) / 'plain.gif',
                Presentation(image_size=32), QUICK,
            )
            masked = animate(
                VCube(), 'R', Path(directory) / 'masked.gif',
                Presentation(image_size=32, mode='oll'), QUICK,
            )

            self.assertNotEqual(
                plain[0].read_bytes(),
                masked[0].read_bytes(),
            )

    def test_the_orientation_reaches_the_animation(self) -> None:
        """Test that an animation plays on the cube as it is held."""
        held = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        with (
                tempfile.TemporaryDirectory() as directory,
                mock.patch(
                    'cubing_algs.display.gl.api.has_pillow',
                    return_value=False,
                ),
        ):
            plain = animate(
                VCube(), 'R', Path(directory) / 'plain.gif',
                Presentation(image_size=32), QUICK,
            )
            turned = animate(
                VCube(), 'R', Path(directory) / 'turned.gif',
                Presentation(image_size=32, orientation=held), QUICK,
            )

            self.assertNotEqual(
                plain[0].read_bytes(),
                turned[0].read_bytes(),
            )

    def test_the_final_frame_is_the_final_state(self) -> None:
        """Test that an animation ends on the render of the cube it lands on."""
        with (
                tempfile.TemporaryDirectory() as directory,
                mock.patch(
                    'cubing_algs.display.gl.api.has_pillow',
                    return_value=False,
                ),
        ):
            written = animate(
                VCube(), "R U'", Path(directory) / 'out.gif',
                Presentation(image_size=32, look=FLAT_LOOK), QUICK,
            )

            landed = VCube()
            landed.rotate("R U'")

            self.assertEqual(
                written[-1].read_bytes(),
                render(landed, Presentation(image_size=32, look=FLAT_LOOK)),
            )


@requires_gpu
class TestSizeFraming(unittest.TestCase):
    """
    Tests that every size of cube comes out framed alike.

    This is the acceptance criterion of the NxN rendering: a 2x2x2 and a
    7x7x7 must cover the image the same way, which only happens once the
    camera frames the sphere the cube fills rather than the box it is
    laid out in, both being eaten by the gap and the chamfer.
    """

    context: ClassVar['moderngl.Context']
    boxes: ClassVar[dict[int, tuple[int, int]]]

    @classmethod
    def setUpClass(cls) -> None:
        """Render every size once for the whole class."""
        cls.context = create_standalone_context()
        cls.boxes = {
            size: cls.silhouette_of(size)
            for size in FRAMING_SIZES
        }

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the context back."""
        cls.context.release()

    @classmethod
    def silhouette_of(cls, size: int) -> tuple[int, int]:
        """
        Measure the silhouette a cube of a given size draws.

        Returns:
            The width and the height of the silhouette, in pixels.

        """
        scene = build_scene(VCube(size=size))

        return silhouette(
            render_scene(
                scene,
                OrbitCamera.from_rotation('', 0.0, scene.geometry.radius),
                Presentation(image_size=FRAMING_SIZE, look=FLAT_LOOK),
                context=cls.context,
            ),
            FRAMING_SIZE,
        )

    def test_every_size_covers_the_same_area(self) -> None:
        """Test that the silhouettes agree from a 2x2x2 to a 7x7x7."""
        for axis, name in enumerate(('width', 'height')):
            extents = [box[axis] for box in self.boxes.values()]

            with self.subTest(axis=name):
                self.assertLess(
                    max(extents) / min(extents) - 1,
                    FRAMING_TOLERANCE,
                )

    def test_every_size_fills_the_frame(self) -> None:
        """Test that no size is drawn small in the middle of the image."""
        for size, box in self.boxes.items():
            with self.subTest(size=size):
                self.assertGreater(min(box), FRAMING_SIZE * FRAMING_COVERAGE)

    def test_no_size_is_clipped(self) -> None:
        """Test that the borders of the image are left empty."""
        for size, box in self.boxes.items():
            with self.subTest(size=size):
                self.assertLess(max(box), FRAMING_SIZE)


@requires_gpu
class TestContextOnGpu(unittest.TestCase):
    """Tests for the context creation, against a real driver."""

    def test_standalone_context_is_recent_enough(self) -> None:
        """Test that the headless context honours the required version."""
        context = create_standalone_context()

        try:
            self.assertGreaterEqual(context.version_code, 330)

            capabilities = describe(context)

            self.assertNotEqual(capabilities['renderer'], 'unknown')
            self.assertNotEqual(capabilities['max_samples'], '0')
        finally:
            context.release()


@requires_gpu
class TestDoctorOnGpu(unittest.TestCase):
    """Tests for the diagnostic command, against a real driver."""

    def test_the_gradient_is_written(self) -> None:
        """Test that the doctor renders and writes its gradient."""
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'gradient.png'

            self.assertEqual(
                doctor_main(['--out', str(destination), '--image-size', '32']),
                0,
            )
            self.assertTrue(
                destination.read_bytes().startswith(PNG_SIGNATURE),
            )
