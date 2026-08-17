"""
Tests for the public API of the GPU rendering backend.

What is checked here is the wiring: ``VCube`` and ``Algorithm`` hand
their state and their display options over to the backend, and give
back what it produces. Everything the backend does with them is tested
where it happens, so a single render is enough to tell that a method
reaches it.

The tests that draw need a real OpenGL context and are skipped when
none can be created. The ones watching a window only build a viewer,
whose ``run()`` is mocked away: no display server is involved.
"""
import struct
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.constants import VIEWER_SIZE
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.viewer import Viewer
from cubing_algs.exceptions import InvalidCubeSizeError
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

SEXY = "R U R' U'"

SCRAMBLE = "R U R' U' F' L F R"

IMAGE_SIZE = 96

# Offset of the width and height fields in a PNG file: the signature,
# then the length and the type of the IHDR chunk.
PNG_DIMENSIONS_OFFSET = len(PNG_SIGNATURE) + 8


def gif_duration(path: Path) -> int:
    """
    Add up how long an animated GIF plays.

    The frames are counted through their delay rather than one by one:
    Pillow merges the frames a rest holds still and sums their delay,
    so what a wait weighs is time, not images.

    Args:
        path: The animation to read.

    Returns:
        How long the animation lasts, in milliseconds.

    """
    from PIL import Image
    from PIL import ImageSequence

    with Image.open(path) as animation:
        return sum(
            frame.info['duration']
            for frame in ImageSequence.Iterator(animation)
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


def png_dimensions(data: bytes) -> tuple[int, int]:
    """
    Read the size a PNG file announces in its header.

    Args:
        data: The bytes of the file.

    Returns:
        Width and height, in pixels.

    """
    width, height = struct.unpack(
        '>II',
        data[PNG_DIMENSIONS_OFFSET:PNG_DIMENSIONS_OFFSET + 8],
    )

    return (width, height)


def viewer_of(call: mock.Mock) -> Viewer:
    """
    Read the viewer a mocked ``run()`` was called on.

    Args:
        call: The mock standing in for ``Viewer.run``.

    Returns:
        The viewer that would have been run.

    """
    return call.call_args[0][0]  # type: ignore[no-any-return]


@requires_gpu
class VCubeRenderTestCase(unittest.TestCase):
    """Tests for VCube.render()."""

    def test_a_png_comes_out(self) -> None:
        """A render is a PNG file, framed at the default size."""
        data = VCube().render()

        self.assertEqual(data[:len(PNG_SIGNATURE)], PNG_SIGNATURE)
        self.assertEqual(png_dimensions(data), (RENDER_SIZE, RENDER_SIZE))

    def test_image_size_is_honored(self) -> None:
        """The image comes out at the size asked for."""
        data = VCube().render(image_size=IMAGE_SIZE)

        self.assertEqual(png_dimensions(data), (IMAGE_SIZE, IMAGE_SIZE))

    def test_the_state_reaches_the_image(self) -> None:
        """Two different cubes render differently."""
        solved = VCube()
        scrambled = VCube()
        scrambled.rotate(SCRAMBLE)

        self.assertNotEqual(
            solved.render(image_size=IMAGE_SIZE),
            scrambled.render(image_size=IMAGE_SIZE),
        )

    def test_the_display_options_reach_the_image(self) -> None:
        """A mode, a palette and a framing all change the rendering."""
        cube = VCube()
        cube.rotate(SCRAMBLE)

        plain = cube.render(image_size=IMAGE_SIZE)

        for option, rendered in (
                ('mode', cube.render(image_size=IMAGE_SIZE, mode='oll')),
                ('palette', cube.render(image_size=IMAGE_SIZE, palette='neon')),
                (
                    'rotation',
                    cube.render(image_size=IMAGE_SIZE, rotation='y90x-20'),
                ),
                ('distance', cube.render(image_size=IMAGE_SIZE, distance=20.0)),
                (
                    'orientation',
                    cube.render(image_size=IMAGE_SIZE, orientation='DF'),
                ),
                (
                    'mask',
                    cube.render(
                        image_size=IMAGE_SIZE, mask='1' * 27 + '0' * 27,
                    ),
                ),
        ):
            with self.subTest(option=option):
                self.assertNotEqual(plain, rendered)

    def test_the_cube_is_left_alone(self) -> None:
        """Rendering an oriented copy never turns the cube itself."""
        cube = VCube()
        cube.rotate(SCRAMBLE)
        state = cube.state

        cube.render(image_size=IMAGE_SIZE, orientation='DF')

        self.assertEqual(cube.state, state)


@requires_gpu
class VCubeAnimateTestCase(unittest.TestCase):
    """Tests for VCube.animate()."""

    def test_an_animation_is_written(self) -> None:
        """An animation lands where it was asked to."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'sexy.gif'
            written = VCube().animate(SEXY, path, image_size=IMAGE_SIZE)

            self.assertEqual(written, [path])
            self.assertTrue(path.exists())
            self.assertTrue(path.stat().st_size)

    def test_the_cube_is_left_alone(self) -> None:
        """Playing an algorithm never touches the cube it is played on."""
        cube = VCube()
        cube.rotate(SCRAMBLE)
        state = cube.state

        with TemporaryDirectory() as directory:
            cube.animate(
                SEXY, Path(directory) / 'sexy.gif', image_size=IMAGE_SIZE,
            )

        self.assertEqual(cube.state, state)

    def test_a_timed_algorithm_plays_at_its_own_speed(self) -> None:
        """A timed algorithm is a solve, pauses of the cuber included."""
        with TemporaryDirectory() as directory:
            timed = Path(directory) / 'timed.gif'
            tight = Path(directory) / 'tight.gif'

            VCube().animate('R@0 U@1200', timed, image_size=IMAGE_SIZE)
            VCube().animate('R U', tight, image_size=IMAGE_SIZE)

            # The stamps leave 1.2 s between the two moves, of which the
            # turn of the R takes its beat: the rest is what is left,
            # and it is what the untimed animation does not hold.
            self.assertGreater(
                gif_duration(timed) - gif_duration(tight), 800,
            )

    def test_the_starting_state_reaches_the_animation(self) -> None:
        """The animation starts from the cube it is given."""
        scrambled = VCube()
        scrambled.rotate(SCRAMBLE)

        with TemporaryDirectory() as directory:
            solved_gif = Path(directory) / 'solved.gif'
            scrambled_gif = Path(directory) / 'scrambled.gif'

            VCube().animate(SEXY, solved_gif, image_size=IMAGE_SIZE)
            scrambled.animate(SEXY, scrambled_gif, image_size=IMAGE_SIZE)

            self.assertNotEqual(
                solved_gif.read_bytes(),
                scrambled_gif.read_bytes(),
            )


class VCubeViewTestCase(unittest.TestCase):
    """Tests for VCube.view(), whose window is never opened."""

    def test_the_viewer_shows_this_cube(self) -> None:
        """The cube of the viewer is the cube it was asked for."""
        cube = VCube()
        cube.rotate(SCRAMBLE)

        with mock.patch.object(Viewer, 'run', autospec=True) as run:
            cube.view()

        self.assertEqual(viewer_of(run).cube.state, cube.state)

    def test_the_display_options_reach_the_viewer(self) -> None:
        """Every option given is the one the viewer holds."""
        with mock.patch.object(Viewer, 'run', autospec=True) as run:
            VCube().view(
                mode='oll',
                palette='neon',
                rotation='y90x-20',
                distance=20.0,
                window_size=(320, 240),
                debug=True,
                show_axes=True,
            )

        viewer = viewer_of(run)

        self.assertEqual(viewer.palette, 'neon')
        self.assertEqual(viewer.mode, 'oll')
        self.assertEqual(viewer.rotation, 'y90x-20')
        self.assertEqual(viewer.distance, 20.0)
        self.assertEqual(viewer.window_size, (320, 240))
        self.assertTrue(viewer.debug)
        self.assertTrue(viewer.show_axes)

    def test_the_window_opens_at_its_default_size(self) -> None:
        """No size asked for leaves the default one alone."""
        with mock.patch.object(Viewer, 'run', autospec=True) as run:
            VCube().view()

        self.assertEqual(viewer_of(run).window_size, VIEWER_SIZE)

    def test_the_orientation_turns_the_cube(self) -> None:
        """An orientation reaches the viewer as a turned cube."""
        cube = VCube()
        cube.rotate(SCRAMBLE)

        with mock.patch.object(Viewer, 'run', autospec=True) as run:
            cube.view(orientation='DF')

        self.assertEqual(
            viewer_of(run).cube.state,
            cube.oriented_copy('DF', full=True).state,
        )


@requires_gpu
class AlgorithmRenderTestCase(unittest.TestCase):
    """Tests for Algorithm.render()."""

    def test_the_final_state_is_rendered(self) -> None:
        """An algorithm renders the cube it leads to."""
        algo = parse_moves(SEXY)

        cube = VCube()
        cube.rotate(algo)

        self.assertEqual(
            algo.render(image_size=IMAGE_SIZE, impact_mask=False),
            cube.render(image_size=IMAGE_SIZE),
        )

    def test_the_impact_mask_shows(self) -> None:
        """The facelets an algorithm moves are highlighted by default."""
        algo = parse_moves(SEXY)

        self.assertNotEqual(
            algo.render(image_size=IMAGE_SIZE),
            algo.render(image_size=IMAGE_SIZE, impact_mask=False),
        )

    def test_the_cube_size_reaches_the_image(self) -> None:
        """An algorithm renders on the size of cube it is given."""
        algo = parse_moves(SEXY)

        self.assertNotEqual(
            algo.render(image_size=IMAGE_SIZE),
            algo.render(5, image_size=IMAGE_SIZE),
        )


@requires_gpu
class AlgorithmAnimateTestCase(unittest.TestCase):
    """Tests for Algorithm.animate()."""

    def test_an_animation_is_written(self) -> None:
        """An algorithm writes the animation of itself being played."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'sexy.gif'
            written = parse_moves(SEXY).animate(path, image_size=IMAGE_SIZE)

            self.assertEqual(written, [path])
            self.assertTrue(path.stat().st_size)

    def test_the_algorithm_plays_from_a_solved_cube(self) -> None:
        """The cube starts solved, the algorithm being played on it."""
        with TemporaryDirectory() as directory:
            algorithm = Path(directory) / 'algorithm.gif'
            cube = Path(directory) / 'cube.gif'

            parse_moves(SEXY).animate(algorithm, image_size=IMAGE_SIZE)
            VCube().animate(SEXY, cube, image_size=IMAGE_SIZE)

            self.assertEqual(algorithm.read_bytes(), cube.read_bytes())

    def test_the_impact_mask_is_off_by_default(self) -> None:
        """Nothing is dimmed unless the impact mask is asked for."""
        with TemporaryDirectory() as directory:
            plain = Path(directory) / 'plain.gif'
            masked = Path(directory) / 'masked.gif'

            parse_moves(SEXY).animate(plain, image_size=IMAGE_SIZE)
            parse_moves(SEXY).animate(
                masked, image_size=IMAGE_SIZE, impact_mask=True,
            )

            self.assertNotEqual(plain.read_bytes(), masked.read_bytes())

    def test_an_algorithm_too_wide_for_the_cube_is_refused(self) -> None:
        """A cube too small for the algorithm is caught before any drawing."""
        with (
                TemporaryDirectory() as directory,
                self.assertRaises(InvalidCubeSizeError),
        ):
            parse_moves('3Rw').animate(
                Path(directory) / 'nope.gif', 2, image_size=IMAGE_SIZE,
            )


class AlgorithmViewTestCase(unittest.TestCase):
    """Tests for Algorithm.view(), whose window is never opened."""

    def test_the_cube_of_the_algorithm_is_shown(self) -> None:
        """The viewer shows the cube the algorithm leads to."""
        algo = parse_moves(SEXY)

        cube = VCube()
        cube.rotate(algo)

        with mock.patch.object(Viewer, 'run', autospec=True) as run:
            shown = algo.view()

        self.assertEqual(shown.state, cube.state)
        self.assertEqual(viewer_of(run).cube.state, cube.state)

    def test_the_impact_mask_reaches_the_viewer(self) -> None:
        """The facelets the algorithm moves are masked as show() masks them."""
        with mock.patch.object(Viewer, 'run', autospec=True) as run:
            parse_moves(SEXY).view()

        self.assertIn('0', viewer_of(run).mask)

    def test_the_display_options_reach_the_viewer(self) -> None:
        """Every option given is the one the viewer holds."""
        with mock.patch.object(Viewer, 'run', autospec=True) as run:
            parse_moves(SEXY).view(
                mode='oll',
                palette='neon',
                rotation='y90x-20',
                distance=20.0,
                window_size=(320, 240),
                debug=True,
                show_axes=True,
                impact_mask=False,
            )

        viewer = viewer_of(run)

        self.assertEqual(viewer.palette, 'neon')
        self.assertEqual(viewer.mode, 'oll')
        self.assertEqual(viewer.rotation, 'y90x-20')
        self.assertEqual(viewer.distance, 20.0)
        self.assertEqual(viewer.window_size, (320, 240))
        self.assertTrue(viewer.debug)
        self.assertTrue(viewer.show_axes)
