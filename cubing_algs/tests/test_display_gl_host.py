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
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from cubing_algs.display.gl.constants import DEFAULT_BUDGET
from cubing_algs.display.gl.constants import GL_VERSION_REQUIRED
from cubing_algs.display.gl.constants import GLFW_MISSING
from cubing_algs.display.gl.constants import IDLE_INTERVAL
from cubing_algs.display.gl.constants import MONITOR_INTERVAL
from cubing_algs.display.gl.constants import TRANSPARENCY_REFUSED
from cubing_algs.display.gl.constants import VIEWER_BACKGROUND
from cubing_algs.display.gl.constants import VIEWER_HELP
from cubing_algs.display.gl.constants import VIEWER_TRANSPARENT
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

# Two screens of a desk, as glfw describes them: the fast one is the
# primary, and the slow one sits to its left. A screen is opaque to the
# backend, so a name stands for one as well as a handle does.
SLOW = 'HDMI-1'
FAST = 'HDMI-2'


@dataclass(frozen=True)
class FakeSize:
    """The size of a video mode, as glfw nests it in one."""

    width: int
    height: int


@dataclass(frozen=True)
class FakeMode:
    """What a screen answers about itself."""

    size: FakeSize
    refresh_rate: int


SCREENS = {
    SLOW: ((0, 0), FakeMode(FakeSize(1080, 1920), 60)),
    FAST: ((1080, 480), FakeMode(FakeSize(3440, 1440), 100)),
}


@contextmanager
def screens(position: tuple[int, int]) -> Iterator[None]:
    """
    Lay the two screens of a desk out, and put a window on them.

    Args:
        position: Upper left corner of the window, in the coordinates
            the two screens share.

    Yields:
        Nothing; glfw answers for that desk while the block runs.

    """
    with (
            mock.patch('glfw.get_monitors', return_value=tuple(SCREENS)),
            mock.patch(
                'glfw.get_monitor_pos',
                side_effect=lambda screen: SCREENS[screen][0],
            ),
            mock.patch(
                'glfw.get_video_mode',
                side_effect=lambda screen: SCREENS[screen][1],
            ),
            mock.patch('glfw.get_primary_monitor', return_value=FAST),
            mock.patch('glfw.get_window_pos', return_value=position),
            mock.patch('glfw.get_window_size', return_value=(720, 720)),
    ):
        yield


def hidden_window(  # noqa: PLR0913
        size: tuple[int, int],
        title: str = WINDOW_TITLE,
        *,
        visible: bool = True,
        samples: int = 0,
        transparent: bool = False,
        require: int = GL_VERSION_REQUIRED,
) -> GLFWWindow:
    """
    Create the window of a host, without showing it.

    What the host asked for is dropped rather than honored: a suite is
    run where nothing is looked at, and a window shown by it is a
    window landing over whatever the machine was doing. What a host
    means to show is asserted on ``visible`` and on the glfw calls it
    makes, never on a window truly on a screen.

    Args:
        size: Width and height of the window, in pixels.
        title: Title of the window.
        visible: What the host asked for, unused.
        samples: Samples of its multisampled framebuffer.
        transparent: Whether the desktop is asked to show through.
        require: Minimum OpenGL version code.

    Returns:
        The glfw window handle, made current and left hidden.

    """
    del visible

    return create_window(
        size,
        title,
        visible=False,
        samples=samples,
        transparent=transparent,
        require=require,
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


class TestViewerHelp(unittest.TestCase):
    """Tests for the one place the shortcuts of the viewer are written."""

    README = Path(__file__).parents[2] / 'README.md'

    @unittest.skipUnless(README.exists(), 'the README is not installed')
    def test_the_readme_quotes_the_shortcuts_verbatim(self) -> None:
        """Test that the documented shortcuts are the ones a window shows."""
        self.assertIn(VIEWER_HELP, self.README.read_text())


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

        # A move starts when it arrives, so a first frame sets it
        # turning and the next one lands it.
        for _frame in range(2):
            self.host.clock -= self.viewer.duration
            self.host.tick()

        self.assertTrue(self.viewer.animation.finished)

    def test_run_until_the_window_closes(self) -> None:
        """Test that the loop draws until the window is closed."""
        with mock.patch(
                'glfw.window_should_close',
                side_effect=[False, True],
        ) as should_close:
            self.host.run()

        self.assertEqual(should_close.call_count, 2)
        self.assertIsNone(self.viewer.stage)

    def test_run_writes_the_shortcuts_of_the_host(self) -> None:
        """Test that a host holding keys back writes its own list."""
        self.host.shortcuts = 'nothing but the mouse'

        with mock.patch(
                'glfw.window_should_close',
                side_effect=[True],
        ), mock.patch(
            'cubing_algs.display.gl.host.output',
        ) as output:
            self.host.run()

        output.assert_called_once_with('nothing but the mouse')

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


class TestHostHidden(HiddenHostTestCase):
    """Tests for a window taken off the screen without being closed."""

    def test_a_window_opens_where_it_was_asked_to(self) -> None:
        """Test that a host opened hidden asks glfw for a hidden window."""
        self.host.visible = False

        with mock.patch(
                'cubing_algs.display.gl.host.create_window',
                side_effect=hidden_window,
        ) as opening:
            self.host.open()

        self.assertFalse(opening.call_args.kwargs['visible'])

    def test_hiding_takes_the_window_off_the_screen(self) -> None:
        """Test that a window hidden is a window nobody is shown."""
        self.host.open()

        with mock.patch('glfw.hide_window') as hiding:
            self.host.hide()

        hiding.assert_called_once_with(self.host.window)
        self.assertFalse(self.host.visible)

    def test_showing_puts_the_window_back(self) -> None:
        """Test that a window shown again is the very same window."""
        self.host.open()
        window = self.host.window
        self.host.hide()

        with mock.patch('glfw.show_window') as showing:
            self.host.show()

        showing.assert_called_once_with(window)
        self.assertTrue(self.host.visible)
        self.assertIs(self.host.window, window)

    def test_hiding_a_host_that_opened_nothing(self) -> None:
        """Test that a host hidden before it opens opens hidden."""
        self.host.hide()

        self.assertFalse(self.host.visible)
        self.assertIsNone(self.host.window)

    def test_the_loop_draws_nothing_behind_a_hidden_window(self) -> None:
        """Test that a hidden window costs no frame and no swap."""
        self.host.visible = False

        with (
                mock.patch(
                    'glfw.window_should_close', side_effect=[False, True],
                ),
                mock.patch('cubing_algs.display.gl.host.time.sleep') as wait,
                mock.patch('glfw.swap_buffers') as swap,
                mock.patch.object(self.host, 'frame') as framed,
        ):
            self.host.run()

        swap.assert_not_called()
        framed.assert_not_called()
        wait.assert_called_once_with(IDLE_INTERVAL)

    def test_the_loop_draws_again_the_moment_it_is_shown(self) -> None:
        """Test that showing a window is what puts the frames back."""
        self.host.open()

        with (
                mock.patch('cubing_algs.display.gl.host.time.sleep'),
                mock.patch.object(self.host, 'frame') as framed,
        ):
            self.host.hide()
            self.host.idle()

            self.host.show()
            self.host.tick()

        framed.assert_called_once()

    def test_a_hidden_window_keeps_the_cube_up_to_date(self) -> None:
        """
        Test that the moves of a hidden window are played all the same.

        The whole point of hiding a window rather than closing it: the
        cube is fed while nobody looks at it, so what is shown again is
        where the cube truly stands.
        """
        self.host.open()
        self.host.hide()
        self.viewer.push('R')

        with mock.patch('cubing_algs.display.gl.host.time.sleep'):
            # A move starts when it arrives, so a first turn sets it
            # turning and the next one lands it.
            for _turn in range(2):
                self.host.clock -= self.viewer.duration
                self.host.idle()

        self.assertTrue(self.viewer.animation.finished)

    def test_a_window_shown_again_is_one_turn_old(self) -> None:
        """Test that a hiding is not replayed in front of whoever ends it."""
        import glfw

        self.host.open()
        self.host.hide()

        with mock.patch('cubing_algs.display.gl.host.time.sleep'):
            self.host.clock -= 60.0
            self.host.idle()

            self.host.show()
            elapsed = glfw.get_time() - self.host.clock

        self.assertLess(elapsed, 1.0)

    def test_settling_lets_the_time_pass_and_draws_nothing(self) -> None:
        """Test that the cheap half of a frame is the half that is played."""
        self.host.open()

        # Patched on the class and not on the instance: a viewer is a
        # slotted dataclass, and there is nowhere on one to hang a
        # method that is not its own.
        with (
                mock.patch.object(Viewer, 'advance') as advanced,
                mock.patch.object(Viewer, 'draw') as drawn,
        ):
            self.host.settle(0.016)

        advanced.assert_called_once_with(0.016)
        drawn.assert_not_called()

    def test_the_closing_keys_go_through_the_seam(self) -> None:
        """Test that a host is free to answer them otherwise."""
        import glfw

        self.host.open()

        with mock.patch.object(self.host, 'on_close') as closing:
            self.host.on_key(
                self.host.window, glfw.KEY_Q, 0, glfw.PRESS, 0,
            )

        closing.assert_called_once_with()


class TestHostTitle(HiddenHostTestCase):
    """Tests for renaming a window after it has opened."""

    def test_a_window_is_renamed(self) -> None:
        """Test that a new name reaches the bar of the window."""
        self.host.open()

        with mock.patch('glfw.set_window_title') as written:
            self.host.set_title('Cubecast')

        self.assertEqual(self.host.title, 'Cubecast')
        written.assert_called_once_with(self.host.window, 'Cubecast')

    def test_the_same_name_is_not_written_again(self) -> None:
        """Test that a title pushed on every frame costs one call."""
        self.host.open()
        self.host.set_title('Cubecast')

        with mock.patch('glfw.set_window_title') as written:
            self.host.set_title('Cubecast')

        written.assert_not_called()

    def test_the_debug_numbers_follow_the_new_name(self) -> None:
        """Test that what is renamed is the base the counter appends to."""
        self.host.open()
        self.host.set_title('Cubecast')

        monitor = self.viewer.monitor
        monitor.restart(0.0)
        monitor.count_frame(0.01)

        with mock.patch('glfw.set_window_title') as written:
            self.host.update_title(MONITOR_INTERVAL)

        self.assertIn('Cubecast', written.call_args.args[1])

    def test_a_window_that_is_not_open_is_only_named(self) -> None:
        """Test that a host renamed before it opens costs no glfw call."""
        with mock.patch('glfw.set_window_title') as written:
            self.host.set_title('Cubecast')

        self.assertEqual(self.host.title, 'Cubecast')
        written.assert_not_called()

    def test_the_name_is_the_one_the_window_opens_with(self) -> None:
        """Test that a title set beforehand is what create_window is given."""
        self.host.set_title('Cubecast')
        self.host.open()

        self.assertEqual(self.host.title, 'Cubecast')


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
        to land in the draw of the frame after - fifteen milliseconds of
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
        divided the rate by fifty - which is the very measure F5 is
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
        self.assertIn(f'{ WINDOW_TITLE } debug -', report)
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

        window = hidden_window(WINDOW_SIZE)

        try:
            self.assertGreater(screen_refresh(window), 0.0)
        finally:
            destroy_window(window)

    def test_a_window_reads_the_screen_it_sits_on(self) -> None:
        """
        Test that the budget comes from the screen showing the window.

        The regression this holds: the rate used to be read off the
        primary screen, so a window opened on the sixty hertz screen of
        a desk whose primary runs at a hundred was given ten
        milliseconds a frame instead of sixteen - and every frame it
        held perfectly read as a frame past its budget.
        """
        with screens((200, 300)):
            self.assertEqual(screen_refresh(object()), 60.0)

    def test_a_window_on_the_other_screen_reads_that_one(self) -> None:
        """Test that moving the window across the desk changes the rate."""
        with screens((1600, 800)):
            self.assertEqual(screen_refresh(object()), 100.0)

    def test_a_window_the_screens_do_not_hold_falls_back(self) -> None:
        """Test that a window nobody shows is given the primary screen."""
        with screens((-4000, -4000)):
            self.assertEqual(screen_refresh(object()), 100.0)

    def test_a_screen_refusing_its_mode_is_skipped(self) -> None:
        """Test that a screen saying nothing never holds the window."""
        with (
                screens((200, 300)),
                mock.patch('glfw.get_video_mode', return_value=None),
        ):
            self.assertEqual(screen_refresh(object()), 0.0)

    def test_no_screen_at_all(self) -> None:
        """Test that a machine without a monitor holds no budget."""
        with (
                mock.patch('glfw.get_monitors', return_value=()),
                mock.patch('glfw.get_primary_monitor', return_value=None),
                mock.patch('glfw.get_window_pos', return_value=(0, 0)),
                mock.patch('glfw.get_window_size', return_value=(720, 720)),
        ):
            self.assertEqual(screen_refresh(object()), 0.0)


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

    def queued(self) -> list[str]:
        """
        Read the notations the viewer has queued.

        Returns:
            The moves waiting to be played, the moment each of them
            arrived left out.

        """
        return [notation for notation, _arrival in self.viewer.pending]

    def test_key_plays_a_move(self) -> None:
        """Test that a letter key queues the move it names."""
        import glfw

        self.host.on_key(None, ord('R'), 0, glfw.PRESS, glfw.MOD_SHIFT)

        self.assertEqual(self.queued(), ["R'"])

    def test_key_modifiers_reach_the_notation(self) -> None:
        """Test that ctrl doubles a move and alt widens it."""
        import glfw

        self.host.on_key(
            None, ord('L'), 0, glfw.PRESS, glfw.MOD_CONTROL | glfw.MOD_ALT,
        )

        self.assertEqual(self.queued(), ['Lw2'])

    def test_held_key_repeats_the_move(self) -> None:
        """Test that holding a key down keeps the cube turning."""
        import glfw

        self.host.on_key(None, ord('U'), 0, glfw.REPEAT, 0)

        self.assertEqual(self.queued(), ['U'])

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

    def test_key_opens_the_cube_up(self) -> None:
        """Test that TAB explodes the cube, and puts it back together."""
        import glfw

        self.host.on_key(None, glfw.KEY_TAB, 0, glfw.PRESS, 0)

        self.assertTrue(self.viewer.exploded)

        self.host.on_key(None, glfw.KEY_TAB, 0, glfw.PRESS, 0)

        self.assertFalse(self.viewer.exploded)

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


class TestHostWithoutMoves(unittest.TestCase):
    """Tests for a window showing a cube it is not the one turning."""

    @classmethod
    def setUpClass(cls) -> None:
        """Choose the glfw variant before anything imports the library."""
        select_glfw_variant()

    def setUp(self) -> None:
        """Build a host refusing the keyboard the cube."""
        self.viewer = Viewer(VCube(), window_size=WINDOW_SIZE)
        self.host = GlfwHost(self.viewer, moves=False)

    def test_a_face_key_plays_nothing(self) -> None:
        """Test that the stream is the only thing entitled to turn it."""
        import glfw

        self.host.on_key(None, ord('R'), 0, glfw.PRESS, 0)

        self.assertEqual(len(self.viewer.pending), 0)

    def test_backspace_puts_nothing_back(self) -> None:
        """Test that a state the source never published is never shown."""
        import glfw

        self.viewer.push('R')
        self.viewer.advance(self.viewer.duration)
        turned = self.viewer.cube.state

        self.host.on_key(None, glfw.KEY_BACKSPACE, 0, glfw.PRESS, 0)

        self.assertEqual(self.viewer.cube.state, turned)

    def test_what_only_looks_at_the_cube_is_still_answered(self) -> None:
        """Test that holding the moves back holds nothing else back."""
        import glfw

        self.host.on_key(None, glfw.KEY_TAB, 0, glfw.PRESS, 0)

        self.assertTrue(self.viewer.exploded)

    def test_the_list_it_prints_offers_no_move(self) -> None:
        """Test that a window describes the keys it truly answers."""
        for keys in ('R U F L D B', 'Backspace'):
            with self.subTest(keys=keys):
                self.assertIn(keys, VIEWER_HELP)
                self.assertNotIn(keys, self.host.help)

    def test_a_window_turning_the_cube_prints_the_whole_list(self) -> None:
        """Test that nothing changes for a host that plays its own moves."""
        self.assertEqual(GlfwHost(self.viewer).help, VIEWER_HELP)

    def test_a_list_of_its_own_is_what_is_printed(self) -> None:
        """Test that a host adding shortcuts says so and is believed."""
        host = GlfwHost(self.viewer, shortcuts='a window\n  K  do a thing')

        self.assertEqual(host.help, 'a window\n  K  do a thing')


class TestHostCarry(HiddenHostTestCase):
    """Tests for carrying the window a Ctrl drag takes hold of."""

    def press(self, mods: int) -> None:
        """
        Press the left button with the modifiers held down.

        Args:
            mods: The modifier keys held at the moment of the press.

        """
        import glfw

        self.host.on_mouse_button(
            self.host.window, glfw.MOUSE_BUTTON_LEFT, glfw.PRESS, mods,
        )

    def test_ctrl_takes_hold_of_the_window(self) -> None:
        """Test that Ctrl held at the press carries instead of orbiting."""
        import glfw

        self.host.open()

        self.press(glfw.MOD_CONTROL)

        self.assertTrue(self.host.carrying)
        self.assertFalse(self.host.dragging)

    def test_a_plain_press_orbits_the_cube(self) -> None:
        """Test that the drag stays the one gesture the viewer is made of."""
        self.host.open()

        self.press(0)

        self.assertTrue(self.host.dragging)
        self.assertFalse(self.host.carrying)

    def test_the_carry_ends_with_the_button(self) -> None:
        """Test that letting go stops carrying without starting a drag."""
        import glfw

        self.host.open()
        self.press(glfw.MOD_CONTROL)

        self.host.on_mouse_button(
            self.host.window, glfw.MOUSE_BUTTON_LEFT, glfw.RELEASE, 0,
        )

        self.assertFalse(self.host.carrying)
        self.assertFalse(self.host.dragging)

    def test_the_window_moves_by_what_the_cursor_gained(self) -> None:
        """Test that a carried window follows the cursor exactly."""
        self.host.open()
        self.host.anchor = (10.0, 20.0)

        with (
                mock.patch(
                    'glfw.get_window_pos', return_value=(100, 200),
                ),
                mock.patch('glfw.set_window_pos') as placed,
        ):
            self.host.carry(30.0, 50.0)

        placed.assert_called_once_with(self.host.window, 120, 230)

    def test_a_carried_window_does_not_orbit(self) -> None:
        """Test that the cube stands still while the window is carried."""
        import glfw

        self.host.open()
        self.press(glfw.MOD_CONTROL)

        camera = replace(self.viewer.camera)

        with mock.patch.object(self.host, 'carry') as carried:
            self.host.on_cursor(self.host.window, 30.0, 50.0)

        carried.assert_called_once_with(30.0, 50.0)
        self.assertEqual(self.viewer.camera.yaw, camera.yaw)
        self.assertEqual(self.viewer.camera.pitch, camera.pitch)

    def test_the_cursor_is_followed_while_the_window_moves(self) -> None:
        """Test that an orbit started after a carry reads no jump."""
        import glfw

        self.host.open()
        self.press(glfw.MOD_CONTROL)

        with mock.patch('glfw.set_window_pos'), mock.patch(
                'glfw.get_window_pos', return_value=(0, 0),
        ):
            self.host.on_cursor(self.host.window, 30.0, 50.0)

        self.assertEqual(self.host.cursor, (30.0, 50.0))


class TestHostTransparent(HiddenHostTestCase):
    """Tests for a window the desktop is asked to show through."""

    def test_an_opaque_window_keeps_the_ground_of_the_viewer(self) -> None:
        """Test that nothing is asked for, and nothing is changed."""
        stage = self.host.open()

        self.assertEqual(stage.background, VIEWER_BACKGROUND)
        self.assertIsNone(self.host.target)

    def test_a_granted_transparency_clears_to_nothing(self) -> None:
        """Test that the desktop showing through leaves no ground at all."""
        self.host.transparent = True

        with mock.patch(
                'cubing_algs.display.gl.host.transparency_granted',
                return_value=True,
        ):
            stage = self.host.open()

        self.assertEqual(stage.background, VIEWER_TRANSPARENT)

    def test_a_refused_transparency_falls_back_on_the_ground(self) -> None:
        """Test that a compositor saying no leaves an ordinary window."""
        self.host.transparent = True

        with (
                mock.patch(
                    'cubing_algs.display.gl.host.transparency_granted',
                    return_value=False,
                ),
                self.assertLogs(
                    'cubing_algs.display.gl.host', level='WARNING',
                ) as logged,
        ):
            stage = self.host.open()

        self.assertEqual(stage.background, VIEWER_BACKGROUND)
        self.assertIn(TRANSPARENCY_REFUSED, logged.output[0])

    def test_a_transparent_window_is_asked_for_no_samples(self) -> None:
        """Test that the two being exclusive is answered by the offscreen."""
        self.host.transparent = True

        self.assertEqual(self.host.samples, 0)
        self.assertTrue(self.host.offscreen)

    def test_an_opaque_window_holds_its_own_samples(self) -> None:
        """Test that a plain window is antialiased by the window itself."""
        self.assertEqual(self.host.samples, self.viewer.look.samples)
        self.assertFalse(self.host.offscreen)

    def test_no_antialiasing_asks_for_none_anywhere(self) -> None:
        """Test that msaa off gives the offscreen detour up as well."""
        self.host.transparent = True
        self.host.msaa = False

        self.assertEqual(self.host.samples, 0)
        self.assertFalse(self.host.offscreen)

    def test_the_target_is_built_and_kept(self) -> None:
        """Test that a target the size of the window is built once."""
        self.host.transparent = True

        with mock.patch(
                'cubing_algs.display.gl.host.transparency_granted',
                return_value=True,
        ):
            self.host.open()

        self.host.refresh_target()
        target = self.host.target

        self.assertIsNotNone(target)
        self.assertEqual(
            target.size,  # type: ignore[union-attr]
            self.viewer.require_stage().size,
        )

        self.host.refresh_target()

        self.assertIs(self.host.target, target)

    def test_the_target_follows_the_window(self) -> None:
        """Test that a resized window is given a target of its new size."""
        self.host.transparent = True

        with mock.patch(
                'cubing_algs.display.gl.host.transparency_granted',
                return_value=True,
        ):
            self.host.open()

        self.host.refresh_target()
        first = self.host.target

        self.viewer.resize((320, 240))
        self.host.refresh_target()

        self.assertIsNot(self.host.target, first)
        self.assertEqual(
            self.host.target.size,  # type: ignore[union-attr]
            (320, 240),
        )

    def test_nothing_is_resolved_without_a_target(self) -> None:
        """Test that a window drawn into directly has nothing to copy."""
        self.host.open()

        self.host.resolve()

        self.assertIsNone(self.host.target)

    def test_the_frame_is_copied_to_the_window(self) -> None:
        """Test that both halves of the resolve reach the context."""
        self.host.transparent = True

        with mock.patch(
                'cubing_algs.display.gl.host.transparency_granted',
                return_value=True,
        ):
            self.host.open()

        self.host.refresh_target()
        target = self.host.target
        context = self.viewer.require_stage().context

        with mock.patch.object(context, 'copy_framebuffer') as copied:
            self.host.resolve()

        self.assertEqual(copied.call_count, 2)
        self.assertEqual(
            copied.call_args_list[0].args,
            (target.resolved, target.framebuffer),  # type: ignore[union-attr]
        )
        self.assertEqual(
            copied.call_args_list[1].args,
            (context.screen, target.resolved),  # type: ignore[union-attr]
        )

    def test_the_target_is_given_back_with_the_window(self) -> None:
        """Test that the target is released while the context is alive."""
        self.host.transparent = True

        with mock.patch(
                'cubing_algs.display.gl.host.transparency_granted',
                return_value=True,
        ):
            self.host.open()

        self.host.refresh_target()

        self.host.close()

        self.assertIsNone(self.host.target)

    def test_the_loop_takes_the_detour(self) -> None:
        """Test that the offscreen detour belongs to the loop, not the seam."""
        self.host.open()

        with (
                mock.patch.object(self.host, 'refresh_target') as refreshed,
                mock.patch.object(self.host, 'resolve') as resolved,
                mock.patch.object(self.host, 'frame') as framed,
        ):
            self.host.tick()

        refreshed.assert_called_once_with()
        resolved.assert_called_once_with()
        framed.assert_called_once()


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
