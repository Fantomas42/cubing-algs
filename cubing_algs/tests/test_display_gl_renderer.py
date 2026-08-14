"""
Tests for the renderer of the GPU rendering backend.

Every test here needs a real OpenGL context, and is skipped when none
can be created, as on a machine without any GPU driver.
"""
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar

from cubing_algs.constants import FACE_ORDER
from cubing_algs.display.gl import render
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.context import describe
from cubing_algs.display.gl.doctor import main as doctor_main
from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.geometry import FACE_BASES
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.renderer import COLOR_CHANNELS
from cubing_algs.display.gl.renderer import SHADOW_GROUND
from cubing_algs.display.gl.renderer import OffscreenTarget
from cubing_algs.display.gl.renderer import Renderer
from cubing_algs.display.gl.renderer import render_scene
from cubing_algs.display.gl.scene import build_color
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.image import ImageDisplay
from cubing_algs.vcube import VCube

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

IMAGE_SIZE = 128

# The GPU rounds a color channel to a byte; two units of tolerance
# absorb that, and nothing more.
COLOR_TOLERANCE = 2

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
    sticker_grain=0.0,
    shadow_opacity=0.0,
)


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
            image_size=IMAGE_SIZE,
            look=FLAT_LOOK,
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
            image_size=IMAGE_SIZE,
            look=replace(FLAT_LOOK, samples=0),
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

        The up center is dropped, and the camera sees through where it
        stood: the plastic of the pieces lining the inside of the cube.
        """
        mask = '1' * 4 + '3' + '1' * 49
        pixels = render_scene(
            build_scene(VCube(), mask=mask),
            OrbitCamera.from_rotation(),
            image_size=IMAGE_SIZE,
            look=FLAT_LOOK,
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

    def test_a_scrambled_cube_differs(self) -> None:
        """Test that the state of the cube reaches the pixels."""
        cube = VCube()
        cube.rotate("R U R' U'")

        self.assertNotEqual(
            render_scene(
                build_scene(cube),
                OrbitCamera.from_rotation(),
                image_size=IMAGE_SIZE,
                look=FLAT_LOOK,
                context=self.context,
            ),
            self.pixels,
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
            image_size=IMAGE_SIZE,
            look=look,
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

    def test_the_shadow_falls_beside_the_cube(self) -> None:
        """
        Test that the contact shadow darkens the ground, and only it.

        A point of the ground plane just outside the cube must gain some
        opacity, while the corners of the image stay empty.
        """
        pixels = self.render(replace(FLAT_LOOK, shadow_opacity=0.5))

        beside = OrbitCamera.from_rotation().view_projection().transform_point(
            Vec3(0.0, SHADOW_GROUND, 1.4),
        )

        self.assertEqual(pixel_at(self.flat, IMAGE_SIZE, beside)[3], 0)
        self.assertGreater(pixel_at(pixels, IMAGE_SIZE, beside)[3], 0)
        self.assertEqual(pixels[3], 0)

    def test_the_default_look_is_the_one_a_render_gets(self) -> None:
        """Test that a render left alone is shaded by the default look."""
        self.assertEqual(
            self.render(DEFAULT_LOOK),
            render_scene(
                build_scene(VCube()),
                OrbitCamera.from_rotation(),
                image_size=IMAGE_SIZE,
                context=self.context,
            ),
        )


@requires_gpu
class TestRender(unittest.TestCase):
    """Tests for the public rendering API."""

    def test_a_png_comes_out(self) -> None:
        """Test that a cube is rendered as a PNG of the asked size."""
        data = render(VCube(), image_size=64)

        self.assertTrue(data.startswith(PNG_SIGNATURE))
        self.assertEqual(data[16:24], (64).to_bytes(4) + (64).to_bytes(4))

    def test_palette_changes_the_image(self) -> None:
        """Test that the palette reaches the rendering."""
        self.assertNotEqual(
            render(VCube(), image_size=64, palette='pastel'),
            render(VCube(), image_size=64),
        )

    def test_rotation_changes_the_image(self) -> None:
        """Test that the framing reaches the rendering."""
        self.assertNotEqual(
            render(VCube(), image_size=64, rotation='y120x-25'),
            render(VCube(), image_size=64),
        )


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
