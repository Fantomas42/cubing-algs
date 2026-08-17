"""
Tests for the glfw host of the interactive viewer.

Everything glfw of the backend is gathered here, and nowhere else: the
window, the loop, the frame rate in the title, and the translation of
the keyboard and the mouse into the vocabulary a viewer speaks. The
viewer itself is tested without any of it, in
``test_display_gl_viewer.py``.

The windows opened here are opened for real, and never shown.
"""
import math
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from cubing_algs.display.gl.constants import FPS_INTERVAL
from cubing_algs.display.gl.constants import GL_VERSION_REQUIRED
from cubing_algs.display.gl.constants import GLFW_MISSING
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import GLFWWindow
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.context import has_glfw
from cubing_algs.display.gl.context import select_glfw_variant
from cubing_algs.display.gl.host import GlfwHost
from cubing_algs.display.gl.host import fps_title
from cubing_algs.display.gl.host import key_letter
from cubing_algs.display.gl.viewer import Viewer
from cubing_algs.vcube import VCube

SCRAMBLE = "R U R' U' F' L F R"

WINDOW_SIZE = (128, 128)

# A window is drawn into for real, so the shortest antialiasing that
# still exercises the multisampled path is enough here.
WINDOW_LOOK = Look(samples=2)


def hidden_window(
        size: tuple[int, int],
        title: str = WINDOW_TITLE,
        *,
        samples: int = 0,
        require: int = GL_VERSION_REQUIRED,
) -> GLFWWindow:
    """
    Create the window of a host, without showing it.

    Args:
        size: Width and height of the window, in pixels.
        title: Title of the window.
        samples: Samples of its multisampled framebuffer.
        require: Minimum OpenGL version code.

    Returns:
        The glfw window handle, made current and left hidden.

    """
    return create_window(
        size, title, visible=False, samples=samples, require=require,
    )


def probe_window() -> bool:
    """
    Tell whether this machine can open a window holding a context.

    Returns:
        True when the host tests can run.

    """
    if not has_glfw():  # pragma: no cover
        return False

    select_glfw_variant()

    try:
        window = hidden_window(WINDOW_SIZE)
        context = create_window_context()
    except GLContextError:  # pragma: no cover
        return False

    context.release()
    destroy_window(window)

    return True


WINDOW_AVAILABLE = probe_window()

requires_window = unittest.skipUnless(
    WINDOW_AVAILABLE,
    'no OpenGL window available on this machine',
)

requires_glfw = unittest.skipUnless(
    has_glfw(),
    'glfw is not installed',
)


class TestKeyLetter(unittest.TestCase):
    """Tests for the key_letter function."""

    def test_a_letter_key_is_its_own_letter(self) -> None:
        """Test that glfw numbers a letter on its uppercase ASCII code."""
        self.assertEqual(key_letter(ord('R')), 'R')

    def test_the_key_glfw_could_not_name(self) -> None:
        """Test that the unknown key is turned into no letter at all."""
        self.assertEqual(key_letter(-1), '')


class TestFpsTitle(unittest.TestCase):
    """Tests for the fps_title function."""

    def test_rate_is_the_average_of_the_period(self) -> None:
        """Test that the rate is counted over the whole period."""
        self.assertEqual(fps_title(120, 2.0), f'{ WINDOW_TITLE } — 60 fps')

    def test_rate_is_rounded(self) -> None:
        """Test that a frame rate is shown whole."""
        self.assertEqual(fps_title(59, 1.02), f'{ WINDOW_TITLE } — 58 fps')

    def test_title_is_kept_ahead(self) -> None:
        """Test that the window keeps being named after what it shows."""
        self.assertEqual(fps_title(30, 1.0, 'cube'), 'cube — 30 fps')


class TestHostWithoutGlfw(unittest.TestCase):
    """Tests for a host on a machine the extra was never installed on."""

    def test_running_without_glfw_names_the_extra(self) -> None:
        """Test that a missing glfw is reported rather than stumbled upon."""
        viewer = Viewer(VCube(), window_size=WINDOW_SIZE)

        with (
                mock.patch.dict(sys.modules, {'glfw': None}),
                mock.patch(
                    'cubing_algs.display.gl.context.has_glfw',
                    return_value=False,
                ),
                self.assertRaises(GLContextError) as context,
        ):
            viewer.run()

        self.assertEqual(str(context.exception), GLFW_MISSING)

    def test_closing_a_host_that_opened_nothing(self) -> None:
        """Test that closing an unopened host is harmless."""
        host = GlfwHost(Viewer(VCube(), window_size=WINDOW_SIZE))

        host.close()

        self.assertIsNone(host.window)


@requires_window
class HiddenHostTestCase(unittest.TestCase):
    """A host whose window is opened for real, but never shown."""

    @classmethod
    def setUpClass(cls) -> None:
        """Choose the glfw variant before anything imports the library."""
        select_glfw_variant()

    def setUp(self) -> None:
        """Build a host on a scrambled cube, window kept hidden."""
        cube = VCube()
        cube.rotate(SCRAMBLE)

        self.viewer = Viewer(
            cube, window_size=WINDOW_SIZE, look=WINDOW_LOOK,
        )
        self.host = GlfwHost(self.viewer)

        self.hidden = mock.patch(
            'cubing_algs.display.gl.host.create_window',
            hidden_window,
        )
        self.hidden.start()

    def tearDown(self) -> None:
        """Close whatever the test left open."""
        self.host.close()
        self.hidden.stop()


class TestHostWindow(HiddenHostTestCase):
    """Tests for the window a host owns."""

    def test_open_attaches_the_viewer(self) -> None:
        """Test that the viewer draws into the stage the host opened."""
        stage = self.host.open()

        self.assertIs(self.viewer.stage, stage)
        self.assertEqual(stage.size, WINDOW_SIZE)
        self.assertIsNotNone(self.host.window)

    def test_a_window_draws_on_its_own_screen(self) -> None:
        """Test that a window needs no framebuffer of its own."""
        stage = self.host.open()

        self.assertIsNone(stage.target)

    def test_close_gives_everything_back(self) -> None:
        """Test that a host closed gives its window and context back."""
        self.host.open()

        self.host.close()

        self.assertIsNone(self.host.window)
        self.assertIsNone(self.host.context)
        self.assertIsNone(self.viewer.stage)

    def test_tick_lets_time_pass(self) -> None:
        """Test that a frame plays the move under way."""
        self.host.open()
        self.viewer.push('R')
        self.host.clock -= self.viewer.duration

        self.host.tick()

        self.assertIsNone(self.viewer.animation)

    def test_run_until_the_window_closes(self) -> None:
        """Test that the loop draws until the window is closed."""
        with mock.patch(
                'glfw.window_should_close',
                side_effect=[False, True],
        ) as should_close:
            self.host.run()

        self.assertEqual(should_close.call_count, 2)
        self.assertIsNone(self.viewer.stage)

    def test_run_gives_the_window_back_on_failure(self) -> None:
        """Test that a loop brought down closes its window anyway."""
        with mock.patch(
                'glfw.window_should_close',
                side_effect=RuntimeError('boom'),
        ), self.assertRaises(RuntimeError):
            self.host.run()

        self.assertIsNone(self.viewer.stage)

    def test_viewer_run_goes_through_a_host(self) -> None:
        """Test that the shortcut of the library opens a window of its own."""
        with mock.patch(
                'glfw.window_should_close',
                side_effect=[True],
        ):
            self.viewer.run()

        self.assertIsNone(self.viewer.stage)

    def test_resize_reaches_the_stage(self) -> None:
        """Test that the window and the framebuffer keep the same size."""
        stage = self.host.open()

        self.host.on_resize(None, 64, 32)

        self.assertEqual(stage.size, (64, 32))
        self.assertEqual(self.viewer.camera.aspect, 2.0)


@dataclass
class CountingHost(GlfwHost):
    """
    The host of a consumer, written as one is meant to be written.

    A plain ``@dataclass`` subclass adding a field of its own and
    overriding the one seam, ``frame()``, exactly as
    ``gl_effects_demo.py`` does with its effects.
    """

    drawn: int = 0

    def frame(self, delta: float) -> None:
        """
        Count the frame, then let the host draw it.

        Args:
            delta: Seconds gone by since the last frame.

        """
        self.drawn += 1

        super().frame(delta)


class TestHostExtension(HiddenHostTestCase):
    """Tests for what subclassing the reference host takes."""

    def setUp(self) -> None:
        """Build the host of a consumer, beside the plain one."""
        super().setUp()

        self.consumer = CountingHost(self.viewer)

    def tearDown(self) -> None:
        """Close the host of the consumer, window patch still in place."""
        self.consumer.close()

        super().tearDown()

    def test_a_subclass_inherits_the_state_of_a_host(self) -> None:
        """
        Test that the fields a host sets itself reach a subclass.

        The regression this holds: a host carrying ``slots=True`` keeps
        the defaults of its ``init=False`` fields out of the class, so a
        subclass generating an ``__init__`` of its own left them unset,
        and the first mouse move read a cursor nobody had written.
        """
        host = self.consumer

        self.assertEqual(host.cursor, (0.0, 0.0))
        self.assertEqual(host.clock, 0.0)
        self.assertEqual(host.period, 0.0)
        self.assertFalse(host.dragging)
        self.assertIsNone(host.window)
        self.assertEqual(host.drawn, 0)

    def test_a_subclass_keeps_the_events_of_a_host(self) -> None:
        """Test that a cursor moved over a subclass orbits the cube."""
        host = self.consumer
        host.open()
        yaw = self.viewer.camera.yaw

        host.on_mouse_button(host.window, 0, 1, 0)
        host.on_cursor(host.window, 24.0, 0.0)

        self.assertEqual(host.cursor, (24.0, 0.0))
        self.assertNotEqual(self.viewer.camera.yaw, yaw)

    def test_the_seam_replaces_the_drawing_and_nothing_else(self) -> None:
        """Test that a frame of a subclass is played by the loop as is."""
        with mock.patch('glfw.window_should_close', side_effect=[False, True]):
            self.consumer.run()

        self.assertEqual(self.consumer.drawn, 1)


class TestHostFrameRate(HiddenHostTestCase):
    """Tests for the frame rate a host writes in its title."""

    def test_tick_counts_no_frame_by_default(self) -> None:
        """Test that a host left alone keeps the title of its window."""
        self.host.open()

        self.host.tick()

        self.assertEqual(self.host.frames, 0)

    def test_tick_counts_a_frame_when_asked(self) -> None:
        """Test that a frame is counted once the rate is asked for."""
        self.viewer.show_fps = True
        self.host.open()

        self.host.tick()

        self.assertEqual(self.host.frames, 1)

    def test_ticking_for_a_whole_period_reaches_the_title(self) -> None:
        """
        Test that the rate a loop measures truly lands in the title.

        The regression this holds: the delta of a frame and the period
        the rate is averaged over were read off the same field, so
        ``tick()`` moved the start of the period to the moment it was
        measuring from, the elapsed time came out null, and no rate ever
        reached the title.
        """
        self.viewer.show_fps = True
        self.host.open()

        # A second and a half of frames, at a tenth of a second each, so
        # that a period is crossed whatever FPS_INTERVAL is set to.
        beat = FPS_INTERVAL / 10
        clock = self.host.clock
        times = [clock + beat * step for step in range(1, 16)]

        with (
                mock.patch('glfw.get_time', side_effect=times),
                mock.patch('glfw.set_window_title') as written,
        ):
            for _ in times:
                self.host.tick()

        self.assertEqual(written.call_count, 1)

    def test_frame_counter_holds_its_rate_for_a_second(self) -> None:
        """Test that the title is not rewritten on every frame."""
        self.host.open()
        self.host.frames = 0
        self.host.period = 0.0

        with mock.patch('glfw.set_window_title') as written:
            self.host.count_frame(FPS_INTERVAL / 2)

        self.assertEqual(self.host.frames, 1)
        written.assert_not_called()

    def test_frame_counter_writes_the_rate_in_the_title(self) -> None:
        """Test that a whole period of frames reaches the title."""
        self.host.open()
        self.host.frames = 59
        self.host.period = 0.0

        with mock.patch('glfw.set_window_title') as written:
            self.host.count_frame(FPS_INTERVAL)

        written.assert_called_once_with(
            self.host.window, f'{ WINDOW_TITLE } — 60 fps',
        )
        self.assertEqual(self.host.frames, 0)
        self.assertEqual(self.host.period, FPS_INTERVAL)

    def test_key_asks_for_the_frame_rate(self) -> None:
        """Test that F3 counts frames from the moment it is pressed."""
        import glfw

        self.host.open()
        self.host.frames = 42
        self.host.clock = 12.0

        with mock.patch('glfw.set_window_title') as written:
            self.host.on_key(None, glfw.KEY_F3, 0, glfw.PRESS, 0)

        self.assertTrue(self.viewer.show_fps)
        written.assert_called_once_with(self.host.window, WINDOW_TITLE)
        self.assertEqual(self.host.frames, 0)
        self.assertEqual(self.host.period, 12.0)

    def test_key_takes_the_frame_rate_out_of_the_title(self) -> None:
        """Test that F3 pressed again leaves the plain title behind."""
        import glfw

        self.viewer.show_fps = True
        self.host.open()
        self.host.count_frame(self.host.period + FPS_INTERVAL)

        with mock.patch('glfw.set_window_title') as written:
            self.host.on_key(None, glfw.KEY_F3, 0, glfw.PRESS, 0)

        self.assertFalse(self.viewer.show_fps)
        written.assert_called_once_with(self.host.window, WINDOW_TITLE)


@requires_glfw
class TestHostInput(unittest.TestCase):
    """
    Tests for the glfw events a host turns into viewer calls.

    None of these needs a window: what is tested is the translation, and
    the viewer on the other side of it.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """Choose the glfw variant before anything imports the library."""
        select_glfw_variant()

    def setUp(self) -> None:
        """Build a host on a solved cube, with no window at all."""
        self.viewer = Viewer(VCube(), window_size=WINDOW_SIZE)
        self.host = GlfwHost(self.viewer)

    def test_key_plays_a_move(self) -> None:
        """Test that a letter key queues the move it names."""
        import glfw

        self.host.on_key(None, ord('R'), 0, glfw.PRESS, glfw.MOD_SHIFT)

        self.assertEqual(list(self.viewer.pending), ["R'"])

    def test_key_modifiers_reach_the_notation(self) -> None:
        """Test that ctrl doubles a move and alt widens it."""
        import glfw

        self.host.on_key(
            None, ord('L'), 0, glfw.PRESS, glfw.MOD_CONTROL | glfw.MOD_ALT,
        )

        self.assertEqual(list(self.viewer.pending), ['Lw2'])

    def test_held_key_repeats_the_move(self) -> None:
        """Test that holding a key down keeps the cube turning."""
        import glfw

        self.host.on_key(None, ord('U'), 0, glfw.REPEAT, 0)

        self.assertEqual(list(self.viewer.pending), ['U'])

    def test_released_key_plays_nothing(self) -> None:
        """Test that letting a key go plays no second move."""
        import glfw

        self.host.on_key(None, ord('U'), 0, glfw.RELEASE, 0)

        self.assertEqual(len(self.viewer.pending), 0)

    def test_key_frames_the_cube_again(self) -> None:
        """Test that space puts the camera back where it started."""
        import glfw

        self.viewer.camera.orbit(1.0, 0.0)
        self.host.on_key(None, glfw.KEY_SPACE, 0, glfw.PRESS, 0)

        self.assertAlmostEqual(self.viewer.camera.yaw, math.radians(45))

    def test_key_resets_the_cube(self) -> None:
        """Test that backspace puts the cube back as it was."""
        import glfw

        self.viewer.push('R')
        self.viewer.advance(self.viewer.duration)
        self.host.on_key(None, glfw.KEY_BACKSPACE, 0, glfw.PRESS, 0)

        self.assertEqual(self.viewer.cube.state, VCube().state)

    def test_key_toggles_the_axes(self) -> None:
        """Test that F2 shows the axes, and hides them again."""
        import glfw

        self.host.on_key(None, glfw.KEY_F2, 0, glfw.PRESS, 0)

        self.assertTrue(self.viewer.show_axes)

        self.host.on_key(None, glfw.KEY_F2, 0, glfw.PRESS, 0)

        self.assertFalse(self.viewer.show_axes)

    def test_drag_orbits_the_camera(self) -> None:
        """Test that dragging the mouse turns the cube the way it goes."""
        self.host.dragging = True
        self.host.cursor = (100.0, 100.0)

        yaw, pitch = self.viewer.camera.yaw, self.viewer.camera.pitch
        self.host.on_cursor(None, 150.0, 120.0)

        self.assertLess(self.viewer.camera.yaw, yaw)
        self.assertGreater(self.viewer.camera.pitch, pitch)
        self.assertEqual(self.host.cursor, (150.0, 120.0))

    def test_moving_without_dragging(self) -> None:
        """Test that a mouse nobody holds down moves nothing."""
        yaw = self.viewer.camera.yaw

        self.host.on_cursor(None, 150.0, 120.0)

        self.assertEqual(self.viewer.camera.yaw, yaw)
        self.assertEqual(self.host.cursor, (150.0, 120.0))

    def test_wheel_zooms_in(self) -> None:
        """Test that scrolling forward brings the camera closer."""
        distance = self.viewer.camera.distance

        self.host.on_scroll(None, 0.0, 2.0)

        self.assertLess(self.viewer.camera.distance, distance)

    def test_wheel_zooms_out(self) -> None:
        """Test that scrolling backwards takes the camera away."""
        distance = self.viewer.camera.distance

        self.host.on_scroll(None, 0.0, -2.0)

        self.assertGreater(self.viewer.camera.distance, distance)


class TestHostWindowInput(HiddenHostTestCase):
    """Tests for the events only a real window can answer."""

    def test_escape_closes_the_window(self) -> None:
        """Test that escape asks the loop to stop."""
        import glfw

        self.host.open()
        self.host.on_key(
            self.host.window, glfw.KEY_ESCAPE, 0, glfw.PRESS, 0,
        )

        self.assertTrue(glfw.window_should_close(self.host.window))

    def test_mouse_button_starts_a_drag(self) -> None:
        """Test that holding the left button down starts an orbit."""
        import glfw

        self.host.open()

        self.host.on_mouse_button(
            self.host.window, glfw.MOUSE_BUTTON_LEFT, glfw.PRESS, 0,
        )
        self.assertTrue(self.host.dragging)

        self.host.on_mouse_button(
            self.host.window, glfw.MOUSE_BUTTON_LEFT, glfw.RELEASE, 0,
        )
        self.assertFalse(self.host.dragging)

    def test_other_mouse_button_does_nothing(self) -> None:
        """Test that only the left button drags the cube around."""
        import glfw

        self.host.open()

        self.host.on_mouse_button(
            self.host.window, glfw.MOUSE_BUTTON_RIGHT, glfw.PRESS, 0,
        )

        self.assertFalse(self.host.dragging)

    def test_screenshot_key(self) -> None:
        """Test that F12 writes a screenshot of its own."""
        import glfw

        self.host.open()

        with mock.patch(
                'cubing_algs.display.gl.viewer.screenshot_path',
        ) as destination, TemporaryDirectory() as directory:
            path = Path(directory) / 'shot.png'
            destination.return_value = path

            self.host.on_key(
                self.host.window, glfw.KEY_F12, 0, glfw.PRESS, 0,
            )

            self.assertTrue(path.exists())
