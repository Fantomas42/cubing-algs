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

from cubing_algs.display.gl.constants import DEFAULT_BUDGET
from cubing_algs.display.gl.constants import GL_VERSION_REQUIRED
from cubing_algs.display.gl.constants import GLFW_MISSING
from cubing_algs.display.gl.constants import MONITOR_INTERVAL
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
from cubing_algs.display.gl.host import key_letter
from cubing_algs.display.gl.host import screen_refresh
from cubing_algs.display.gl.metrics import debug_title
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
        self.assertEqual(host.refresh, 0.0)
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


class TestHostMonitoring(HiddenHostTestCase):
    """Tests for the performance a host measures and writes in its title."""

    def test_a_window_opens_on_the_budget_of_its_screen(self) -> None:
        """Test that a frame is given what the screen leaves it."""
        with mock.patch(
                'cubing_algs.display.gl.host.screen_refresh',
                return_value=100.0,
        ):
            self.host.open()

        self.assertEqual(self.host.refresh, 100.0)
        self.assertAlmostEqual(self.viewer.monitor.budget, 0.01)

    def test_a_window_without_a_screen_keeps_the_default_budget(self) -> None:
        """Test that an unknown refresh rate changes nothing."""
        with mock.patch(
                'cubing_algs.display.gl.host.screen_refresh',
                return_value=0.0,
        ):
            self.host.open()

        self.assertEqual(self.viewer.monitor.budget, DEFAULT_BUDGET)

    def test_tick_measures_every_frame(self) -> None:
        """Test that a frame is measured whether it is watched or not."""
        self.host.open()

        self.host.tick()

        monitor = self.viewer.monitor
        self.assertEqual(monitor.frames, 1)
        self.assertEqual(monitor.frame.count, 1)
        self.assertEqual(monitor.swap.count, 1)
        self.assertEqual(monitor.advance.count, 1)
        self.assertEqual(monitor.draw.count, 1)

    def test_tick_leaves_the_title_alone_by_default(self) -> None:
        """Test that a host left alone keeps the title of its window."""
        self.host.open()

        with mock.patch('glfw.set_window_title') as written:
            self.host.tick()

        written.assert_not_called()

    def test_the_gpu_is_only_timed_when_it_is_asked_for(self) -> None:
        """Test that the one measure that costs is the one turned on."""
        self.host.open()

        self.host.tick()
        self.assertEqual(self.viewer.monitor.gpu.count, 0)

        self.viewer.debug = True
        self.host.tick()
        self.host.tick()

        self.assertGreater(self.viewer.monitor.gpu.count, 0)

    def test_monitoring_waits_for_the_gpu_after_the_swap(self) -> None:
        """
        Test that the wait for the screen is put where it is measured.

        A driver does not block in the swap: it queues the frame and
        makes the next call pay for it, so the wait for the screen used
        to land in the draw of the frame after — fifteen milliseconds of
        processor time the processor never spent. Monitoring waits right
        after the swap instead, and only while it is monitoring.
        """
        import moderngl

        self.host.open()

        with mock.patch.object(moderngl.Context, 'finish') as finished:
            self.host.tick()
            finished.assert_not_called()

            self.viewer.debug = True
            self.host.tick()

            finished.assert_called_once_with()

    def test_a_free_running_window_is_never_made_to_wait(self) -> None:
        """
        Test that nothing waits for the GPU once the vsync is off.

        There is no wait to move then, and asking for one anyway
        divided the rate by fifty — which is the very measure F5 is
        pressed to take.
        """
        import moderngl

        self.viewer.debug = True
        self.host.open()
        self.host.set_vsync(enabled=False)

        with mock.patch.object(moderngl.Context, 'finish') as finished:
            self.host.tick()

        finished.assert_not_called()

    def test_ticking_for_a_whole_period_reaches_the_title(self) -> None:
        """
        Test that the rate a loop measures truly lands in the title.

        The regression this holds: the delta of a frame and the period
        the rate is averaged over were read off the same field, so
        ``tick()`` moved the start of the period to the moment it was
        measuring from, the elapsed time came out null, and no rate ever
        reached the title.
        """
        self.viewer.debug = True
        self.host.open()

        # A second and a half of frames, so that a period is crossed
        # once and only once, whatever MONITOR_INTERVAL is set to. Each
        # tick reads the clock three times: before the frame, before the
        # swap and after it.
        beat = MONITOR_INTERVAL / 10
        clock = self.host.clock
        readings = 3
        ticks = 5
        times = [
            clock + beat * step
            for step in range(1, ticks * readings + 1)
        ]

        with (
                mock.patch('glfw.get_time', side_effect=times),
                mock.patch('glfw.set_window_title') as written,
        ):
            for _ in range(ticks):
                self.host.tick()

        self.assertEqual(written.call_count, 1)

    def test_the_title_holds_its_numbers_for_a_period(self) -> None:
        """Test that the title is not rewritten on every frame."""
        self.host.open()
        monitor = self.viewer.monitor
        monitor.restart(0.0)

        with mock.patch('glfw.set_window_title') as written:
            self.host.update_title(MONITOR_INTERVAL / 2)

        written.assert_not_called()

    def test_the_title_says_what_a_frame_costs(self) -> None:
        """Test that a whole period of frames reaches the title."""
        self.host.open()
        monitor = self.viewer.monitor
        monitor.restart(0.0)

        for _ in range(60):
            monitor.count_frame(0.01)

        expected = debug_title(monitor, MONITOR_INTERVAL, WINDOW_TITLE)

        with mock.patch('glfw.set_window_title') as written:
            self.host.update_title(MONITOR_INTERVAL)

        written.assert_called_once_with(self.host.window, expected)
        self.assertIn('60 fps', expected)
        self.assertEqual(monitor.frames, 0)
        self.assertEqual(monitor.period, MONITOR_INTERVAL)

    def test_key_asks_for_the_monitoring(self) -> None:
        """Test that F3 counts frames from the moment it is pressed."""
        import glfw

        self.host.open()
        self.viewer.monitor.frames = 42
        self.host.clock = 12.0

        with mock.patch('glfw.set_window_title') as written:
            self.host.on_key(None, glfw.KEY_F3, 0, glfw.PRESS, 0)

        self.assertTrue(self.viewer.debug)
        written.assert_called_once_with(self.host.window, WINDOW_TITLE)
        self.assertEqual(self.viewer.monitor.frames, 0)
        self.assertEqual(self.viewer.monitor.period, 12.0)

    def test_key_takes_the_monitoring_out_of_the_title(self) -> None:
        """Test that F3 pressed again leaves the plain title behind."""
        import glfw

        self.viewer.debug = True
        self.host.open()
        self.host.update_title(self.host.clock + MONITOR_INTERVAL)

        with mock.patch('glfw.set_window_title') as written:
            self.host.on_key(None, glfw.KEY_F3, 0, glfw.PRESS, 0)

        self.assertFalse(self.viewer.debug)
        written.assert_called_once_with(self.host.window, WINDOW_TITLE)

    def test_key_writes_a_report(self) -> None:
        """Test that F4 sends everything the monitor knows to stdout."""
        import glfw

        self.host.open()
        self.host.tick()

        with mock.patch('sys.stdout.write') as written:
            self.host.on_key(None, glfw.KEY_F4, 0, glfw.PRESS, 0)

        report = written.call_args[0][0]
        self.assertIn(f'{ WINDOW_TITLE } debug —', report)
        self.assertIn('instances', report)
        self.assertIn('vsync on', report)

    def test_key_frees_the_frames_from_the_screen(self) -> None:
        """Test that F5 turns the vsync off, then on again."""
        import glfw

        self.host.open()

        with mock.patch('glfw.swap_interval') as interval:
            self.host.on_key(None, glfw.KEY_F5, 0, glfw.PRESS, 0)

            self.assertFalse(self.host.vsync)
            interval.assert_called_once_with(0)

            interval.reset_mock()
            self.host.on_key(None, glfw.KEY_F5, 0, glfw.PRESS, 0)

            self.assertTrue(self.host.vsync)
            interval.assert_called_once_with(1)

    def test_a_host_can_open_without_the_vsync(self) -> None:
        """Test that a host built free running opens free running."""
        host = GlfwHost(self.viewer, vsync=False)

        with mock.patch('glfw.swap_interval') as interval:
            host.open()

        try:
            interval.assert_called_once_with(0)
        finally:
            host.close()

    def test_the_profile_carries_what_the_window_knows(self) -> None:
        """Test that a host completes the profile of its viewer."""
        with mock.patch(
                'cubing_algs.display.gl.host.screen_refresh',
                return_value=100.0,
        ):
            self.host.open()

        profile = self.host.profile()

        self.assertEqual(profile.refresh, 100.0)
        self.assertTrue(profile.vsync)
        self.assertEqual(profile.size, WINDOW_SIZE)


@requires_window
class TestScreenRefresh(unittest.TestCase):
    """Tests for the refresh rate a window reads off its screen."""

    @classmethod
    def setUpClass(cls) -> None:
        """Choose the glfw variant before anything imports the library."""
        select_glfw_variant()

    def test_a_screen_says_how_fast_it_refreshes(self) -> None:
        """Test that a real screen answers with a plausible rate."""
        import glfw

        glfw.init()

        self.assertGreater(screen_refresh(), 0.0)

    def test_no_screen_at_all(self) -> None:
        """Test that a machine without a monitor holds no budget."""
        with mock.patch('glfw.get_primary_monitor', return_value=None):
            self.assertEqual(screen_refresh(), 0.0)

    def test_a_screen_with_no_video_mode(self) -> None:
        """Test that a screen refusing its mode holds no budget either."""
        with (
                mock.patch('glfw.get_primary_monitor', return_value=object()),
                mock.patch('glfw.get_video_mode', return_value=None),
        ):
            self.assertEqual(screen_refresh(), 0.0)


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
