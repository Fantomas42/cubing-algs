"""
Tests for the interactive viewer of the GPU rendering backend.

Most of what a viewer does needs neither a window nor a GPU: the cube,
the camera and the queue of moves are plain Python, and that is what
the split between ``Viewer`` and ``Stage`` buys. The few tests that do
open a window open it hidden, and are skipped where none can be.
"""
import math
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.gl.constants import FPS_INTERVAL
from cubing_algs.display.gl.constants import GL_VERSION_REQUIRED
from cubing_algs.display.gl.constants import GLFW_MISSING
from cubing_algs.display.gl.constants import SCREENSHOT_NAME
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import GLFWWindow
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.context import has_glfw
from cubing_algs.display.gl.context import select_glfw_variant
from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.renderer import Renderer
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import OrientationTracker
from cubing_algs.display.gl.transforms import Quat
from cubing_algs.display.gl.viewer import Stage
from cubing_algs.display.gl.viewer import Viewer
from cubing_algs.display.gl.viewer import fps_title
from cubing_algs.display.gl.viewer import key_notation
from cubing_algs.display.gl.viewer import resolve_orientation
from cubing_algs.display.gl.viewer import screenshot_path
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
    Create the window of a viewer, without showing it.

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
        True when the viewer tests can run.

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


class TestKeyNotation(unittest.TestCase):
    """Tests for the key_notation function."""

    def test_face_key(self) -> None:
        """Test that a letter key turns the face it names."""
        self.assertEqual(key_notation(ord('R')), 'R')

    def test_prime(self) -> None:
        """Test that shift turns a face the other way."""
        self.assertEqual(key_notation(ord('U'), prime=True), "U'")

    def test_double(self) -> None:
        """Test that ctrl turns a face twice."""
        self.assertEqual(key_notation(ord('F'), double=True), 'F2')

    def test_double_wins_over_prime(self) -> None:
        """Test that a half turn has no direction to be primed in."""
        self.assertEqual(
            key_notation(ord('B'), prime=True, double=True),
            'B2',
        )

    def test_wide_face(self) -> None:
        """Test that alt takes the layer behind a face along."""
        self.assertEqual(key_notation(ord('L'), wide=True), 'Lw')

    def test_wide_prime_face(self) -> None:
        """Test that a wide move is primed like any other."""
        self.assertEqual(
            key_notation(ord('D'), prime=True, wide=True),
            "Dw'",
        )

    def test_slice_key(self) -> None:
        """Test that a slice key turns the middle layer."""
        self.assertEqual(key_notation(ord('M')), 'M')

    def test_slice_is_never_wide(self) -> None:
        """Test that widening a slice means nothing, and does nothing."""
        self.assertEqual(key_notation(ord('S'), wide=True), 'S')

    def test_rotation_key(self) -> None:
        """Test that a rotation key turns the whole cube, in lowercase."""
        self.assertEqual(key_notation(ord('Y')), 'y')

    def test_rotation_is_never_wide(self) -> None:
        """Test that widening a rotation means nothing, and does nothing."""
        self.assertEqual(key_notation(ord('X'), wide=True, prime=True), "x'")

    def test_unknown_key(self) -> None:
        """Test that a key playing no move is turned into nothing."""
        self.assertEqual(key_notation(ord('K')), '')

    def test_unknown_key_code(self) -> None:
        """Test that the key glfw could not name is turned into nothing."""
        self.assertEqual(key_notation(-1), '')


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


class TestResolveOrientation(unittest.TestCase):
    """Tests for the resolve_orientation function."""

    def test_nothing_holds_the_cube(self) -> None:
        """Test that a viewer left alone draws the cube where it is."""
        self.assertEqual(resolve_orientation(None), IDENTITY)

    def test_a_quaternion_is_taken_as_it_comes(self) -> None:
        """Test that an orientation given directly is the one drawn."""
        quarter = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        self.assertEqual(resolve_orientation(quarter), quarter)

    def test_a_tracker_is_read_at_every_call(self) -> None:
        """Test that a tracker is followed, and not read once."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())

        self.assertEqual(resolve_orientation(tracker), IDENTITY)

        quarter = Quat.from_axis_angle(AXIS_Y, math.pi / 2)
        tracker.update(*quarter)

        self.assertEqual(resolve_orientation(tracker), quarter)


class TestScreenshotPath(unittest.TestCase):
    """Tests for the screenshot_path function."""

    def test_name_is_a_png(self) -> None:
        """Test that a screenshot is named after the moment it was taken."""
        path = screenshot_path()

        self.assertEqual(path.suffix, '.png')
        self.assertTrue(path.name.startswith(SCREENSHOT_NAME[:12]))


class TestViewer(unittest.TestCase):
    """Tests for the state a viewer keeps, without any window."""

    def setUp(self) -> None:
        """Build a viewer on a scrambled cube."""
        self.cube = VCube()
        self.cube.rotate(SCRAMBLE)

        self.viewer = Viewer(self.cube, window_size=WINDOW_SIZE)

    def test_the_given_cube_is_left_alone(self) -> None:
        """Test that a viewer plays on a copy of the cube."""
        self.viewer.push('R')
        self.viewer.advance(self.viewer.duration)

        self.assertNotEqual(self.viewer.cube.state, self.cube.state)

    def test_scene_is_built(self) -> None:
        """Test that the cube is ready to be drawn straight away."""
        self.assertEqual(self.viewer.scene.size, 3)
        self.assertEqual(self.viewer.geometry.size, 3)

    def test_mode_is_resolved_once(self) -> None:
        """Test that a display mode settles the mask of the viewer."""
        viewer = Viewer(self.cube, mode='oll')

        self.assertTrue(viewer.mask)

    def test_push_queues_a_move(self) -> None:
        """Test that a move waits its turn."""
        self.assertTrue(self.viewer.push('R'))
        self.assertEqual(list(self.viewer.pending), ['R'])

    def test_push_nothing(self) -> None:
        """Test that a key playing no move queues nothing."""
        self.assertFalse(self.viewer.push(''))
        self.assertEqual(len(self.viewer.pending), 0)

    def test_push_a_move_the_cube_refuses(self) -> None:
        """Test that a move an even cube cannot take is dropped."""
        viewer = Viewer(VCube(size=2))

        self.assertFalse(viewer.push('M'))
        self.assertEqual(len(viewer.pending), 0)

    def test_advance_plays_the_move(self) -> None:
        """Test that a queued move lands on the cube."""
        expected = self.cube.copy()
        expected.rotate('R')

        self.viewer.push('R')
        self.viewer.advance(self.viewer.duration)

        self.assertEqual(self.viewer.cube.state, expected.state)
        self.assertIsNone(self.viewer.animation)

    def test_advance_turns_before_landing(self) -> None:
        """Test that a move under way is drawn part of the way round."""
        resting = self.viewer.scene

        self.viewer.push('R')
        turning = self.viewer.advance(self.viewer.duration / 2)

        self.assertIsNotNone(self.viewer.animation)
        self.assertNotEqual(turning.instances, resting.instances)
        self.assertEqual(self.viewer.cube.state, self.cube.state)

    def test_advance_plays_the_moves_in_order(self) -> None:
        """Test that a queue of moves is played one move at a time."""
        expected = self.cube.copy()
        expected.rotate("R U'")

        self.viewer.push('R')
        self.viewer.push("U'")

        for _step in range(2):
            self.viewer.advance(self.viewer.duration)

        self.assertEqual(self.viewer.cube.state, expected.state)
        self.assertEqual(len(self.viewer.pending), 0)

    def test_advance_without_anything_to_play(self) -> None:
        """Test that an idle viewer keeps drawing the cube at rest."""
        self.assertIs(self.viewer.advance(1.0), self.viewer.scene)

    def test_reset_cube(self) -> None:
        """Test that the cube goes back to the state it was opened on."""
        self.viewer.push('R')
        self.viewer.advance(self.viewer.duration)
        self.viewer.push('U')

        self.viewer.reset_cube()

        self.assertEqual(self.viewer.cube.state, self.cube.state)
        self.assertEqual(len(self.viewer.pending), 0)
        self.assertIsNone(self.viewer.animation)

    def test_drawing_without_a_window(self) -> None:
        """Test that a closed viewer says so rather than crashing."""
        with self.assertRaises(GLContextError):
            self.viewer.draw()

    def test_screenshot_without_a_window(self) -> None:
        """Test that a closed viewer has nothing to capture."""
        with self.assertRaises(GLContextError):
            self.viewer.screenshot()

    def test_closing_a_closed_viewer(self) -> None:
        """Test that closing a viewer twice is harmless."""
        self.viewer.close()

        self.assertIsNone(self.viewer.stage)

    def test_opening_without_glfw_names_the_extra(self) -> None:
        """Test that a missing glfw is reported rather than stumbled upon."""
        with (
                mock.patch.dict(sys.modules, {'glfw': None}),
                mock.patch(
                    'cubing_algs.display.gl.context.has_glfw',
                    return_value=False,
                ),
                self.assertRaises(GLContextError) as context,
        ):
            self.viewer.run()

        self.assertEqual(str(context.exception), GLFW_MISSING)


class TestViewerFraming(unittest.TestCase):
    """Tests for the way a viewer frames the cube in its window."""

    def setUp(self) -> None:
        """Build a viewer on a solved cube."""
        self.viewer = Viewer(VCube(), window_size=WINDOW_SIZE)

    def test_camera_frames_the_cube(self) -> None:
        """Test that the camera is the one the SVG backend would use."""
        self.assertAlmostEqual(self.viewer.camera.fov, self.viewer.framing_fov)

    def test_reset_camera(self) -> None:
        """Test that the camera goes back to its opening framing."""
        self.viewer.camera.orbit(1.0, 0.5)
        self.viewer.camera.zoom(0.5)

        self.viewer.reset_camera()

        self.assertAlmostEqual(
            self.viewer.camera.fov,
            self.viewer.framing_fov,
        )
        self.assertEqual(self.viewer.camera.distance, DISTANCE)

    def test_resize_follows_the_window(self) -> None:
        """Test that the camera takes the shape of the viewport."""
        self.viewer.resize((800, 400))

        self.assertEqual(self.viewer.camera.aspect, 2.0)
        self.assertAlmostEqual(self.viewer.camera.fov, self.viewer.framing_fov)

    def test_resize_to_a_portrait_window(self) -> None:
        """Test that a window taller than wide does not cut the cube."""
        self.viewer.resize((400, 800))

        self.assertGreater(self.viewer.camera.fov, self.viewer.framing_fov)

    def test_resize_keeps_the_zoom(self) -> None:
        """Test that resizing a window never undoes a zoom."""
        self.viewer.camera.zoom(0.5)
        distance = self.viewer.camera.distance

        self.viewer.resize((640, 480))

        self.assertEqual(self.viewer.camera.distance, distance)

    def test_resize_to_nothing(self) -> None:
        """Test that a minimized window is left alone."""
        self.viewer.resize((0, 0))

        self.assertEqual(self.viewer.camera.aspect, 1.0)


@requires_glfw
class TestViewerInput(unittest.TestCase):
    """Tests for the events a viewer answers, without any window."""

    @classmethod
    def setUpClass(cls) -> None:
        """Choose the glfw variant before anything imports the library."""
        select_glfw_variant()

    def setUp(self) -> None:
        """Build a viewer on a solved cube."""
        self.viewer = Viewer(VCube(), window_size=WINDOW_SIZE)

    def test_key_plays_a_move(self) -> None:
        """Test that a letter key queues the move it names."""
        import glfw

        self.viewer.on_key(None, ord('R'), 0, glfw.PRESS, glfw.MOD_SHIFT)

        self.assertEqual(list(self.viewer.pending), ["R'"])

    def test_held_key_repeats_the_move(self) -> None:
        """Test that holding a key down keeps the cube turning."""
        import glfw

        self.viewer.on_key(None, ord('U'), 0, glfw.REPEAT, 0)

        self.assertEqual(list(self.viewer.pending), ['U'])

    def test_released_key_plays_nothing(self) -> None:
        """Test that letting a key go plays no second move."""
        import glfw

        self.viewer.on_key(None, ord('U'), 0, glfw.RELEASE, 0)

        self.assertEqual(len(self.viewer.pending), 0)

    def test_key_frames_the_cube_again(self) -> None:
        """Test that space puts the camera back where it started."""
        import glfw

        self.viewer.camera.orbit(1.0, 0.0)
        self.viewer.on_key(None, glfw.KEY_SPACE, 0, glfw.PRESS, 0)

        self.assertAlmostEqual(self.viewer.camera.yaw, math.radians(45))

    def test_key_resets_the_cube(self) -> None:
        """Test that backspace puts the cube back as it was."""
        import glfw

        self.viewer.push('R')
        self.viewer.advance(self.viewer.duration)
        self.viewer.on_key(None, glfw.KEY_BACKSPACE, 0, glfw.PRESS, 0)

        self.assertEqual(self.viewer.cube.state, VCube().state)

    def test_drag_orbits_the_camera(self) -> None:
        """Test that dragging the mouse turns the cube the way it goes."""
        self.viewer.dragging = True
        self.viewer.cursor = (100.0, 100.0)

        yaw, pitch = self.viewer.camera.yaw, self.viewer.camera.pitch
        self.viewer.on_cursor(None, 150.0, 120.0)

        self.assertLess(self.viewer.camera.yaw, yaw)
        self.assertGreater(self.viewer.camera.pitch, pitch)
        self.assertEqual(self.viewer.cursor, (150.0, 120.0))

    def test_moving_without_dragging(self) -> None:
        """Test that a mouse nobody holds down moves nothing."""
        yaw = self.viewer.camera.yaw

        self.viewer.on_cursor(None, 150.0, 120.0)

        self.assertEqual(self.viewer.camera.yaw, yaw)
        self.assertEqual(self.viewer.cursor, (150.0, 120.0))

    def test_wheel_zooms_in(self) -> None:
        """Test that scrolling forward brings the camera closer."""
        distance = self.viewer.camera.distance

        self.viewer.on_scroll(None, 0.0, 2.0)

        self.assertLess(self.viewer.camera.distance, distance)

    def test_wheel_zooms_out(self) -> None:
        """Test that scrolling backwards takes the camera away."""
        distance = self.viewer.camera.distance

        self.viewer.on_scroll(None, 0.0, -2.0)

        self.assertGreater(self.viewer.camera.distance, distance)

    def test_resize_event(self) -> None:
        """Test that a resized window reaches the camera."""
        self.viewer.on_resize(None, 800, 400)

        self.assertEqual(self.viewer.camera.aspect, 2.0)


@requires_window
class HiddenViewerTestCase(unittest.TestCase):
    """A viewer whose window is opened for real, but never shown."""

    @classmethod
    def setUpClass(cls) -> None:
        """Choose the glfw variant before anything imports the library."""
        select_glfw_variant()

    def setUp(self) -> None:
        """Open a hidden viewer on a scrambled cube."""
        cube = VCube()
        cube.rotate(SCRAMBLE)

        self.viewer = Viewer(
            cube, window_size=WINDOW_SIZE, look=WINDOW_LOOK,
        )

        self.hidden = mock.patch(
            'cubing_algs.display.gl.viewer.create_window',
            hidden_window,
        )
        self.hidden.start()

    def tearDown(self) -> None:
        """Close whatever the test left open."""
        self.viewer.close()
        self.hidden.stop()


class TestViewerHeldFromOutside(HiddenViewerTestCase):
    """Tests for a viewer drawing a cube something outside is holding."""

    def test_draw_hands_the_external_orientation_over(self) -> None:
        """Test that a frame is drawn with the cube held as it is."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())
        tracker.update(*Quat.from_axis_angle(AXIS_Y, math.pi / 2))

        self.viewer.orientation = tracker
        self.viewer.open()

        with mock.patch.object(Renderer, 'draw') as drawn:
            self.viewer.draw()

        drawn.assert_called_once_with(
            self.viewer.scene,
            self.viewer.camera,
            self.viewer.look,
            tracker.orientation,
        )

    def test_screenshot_holds_the_external_orientation(self) -> None:
        """Test that a capture shows the cube as the window does."""
        quarter = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        self.viewer.orientation = quarter
        self.viewer.open()

        with (
                TemporaryDirectory() as folder,
                mock.patch.object(Renderer, 'draw') as drawn,
        ):
            self.viewer.screenshot(Path(folder) / 'held.png')

        self.assertEqual(drawn.call_args.args[3], quarter)


class TestViewerWindow(HiddenViewerTestCase):
    """Tests for a viewer holding a real, hidden, window."""

    def test_open_and_close(self) -> None:
        """Test that a viewer gives its window back."""
        stage = self.viewer.open()

        self.assertIs(self.viewer.stage, stage)
        self.assertEqual(stage.size, WINDOW_SIZE)

        self.viewer.close()

        self.assertIsNone(self.viewer.stage)

    def test_draw(self) -> None:
        """Test that a frame reaches the window framebuffer."""
        self.viewer.open()

        self.viewer.draw()

    def test_tick_lets_time_pass(self) -> None:
        """Test that a frame plays the move under way."""
        self.viewer.open()
        self.viewer.push('R')
        self.viewer.clock -= self.viewer.duration

        self.viewer.tick()

        self.assertIsNone(self.viewer.animation)

    def test_tick_counts_no_frame_by_default(self) -> None:
        """Test that a viewer left alone keeps the title of its window."""
        stage = self.viewer.open()

        self.viewer.tick()

        self.assertEqual(stage.frames, 0)

    def test_tick_counts_a_frame_when_asked(self) -> None:
        """Test that a frame is counted once the rate is asked for."""
        self.viewer.show_fps = True
        stage = self.viewer.open()

        self.viewer.tick()

        self.assertEqual(stage.frames, 1)

    def test_frame_counter_holds_its_rate_for_a_second(self) -> None:
        """Test that the title is not rewritten on every frame."""
        stage = self.viewer.open()
        stage.frames = 0
        stage.clock = 0.0

        with mock.patch('glfw.set_window_title') as written:
            stage.count_frame(FPS_INTERVAL / 2)

        self.assertEqual(stage.frames, 1)
        written.assert_not_called()

    def test_frame_counter_writes_the_rate_in_the_title(self) -> None:
        """Test that a whole period of frames reaches the title."""
        stage = self.viewer.open()
        stage.frames = 59
        stage.clock = 0.0

        with mock.patch('glfw.set_window_title') as written:
            stage.count_frame(FPS_INTERVAL)

        written.assert_called_once_with(
            stage.window, f'{ WINDOW_TITLE } — 60 fps',
        )
        self.assertEqual(stage.frames, 0)
        self.assertEqual(stage.clock, FPS_INTERVAL)

    def test_run_until_the_window_closes(self) -> None:
        """Test that the loop draws until the window is closed."""
        with mock.patch(
                'glfw.window_should_close',
                side_effect=[False, True],
        ) as should_close:
            self.viewer.run()

        self.assertEqual(should_close.call_count, 2)
        self.assertIsNone(self.viewer.stage)

    def test_run_gives_the_window_back_on_failure(self) -> None:
        """Test that a loop brought down closes its window anyway."""
        with mock.patch(
                'glfw.window_should_close',
                side_effect=RuntimeError('boom'),
        ), self.assertRaises(RuntimeError):
            self.viewer.run()

        self.assertIsNone(self.viewer.stage)

    def test_escape_closes_the_window(self) -> None:
        """Test that escape asks the loop to stop."""
        import glfw

        stage = self.viewer.open()
        self.viewer.on_key(stage.window, glfw.KEY_ESCAPE, 0, glfw.PRESS, 0)

        self.assertTrue(glfw.window_should_close(stage.window))

    def test_mouse_button_starts_a_drag(self) -> None:
        """Test that holding the left button down starts an orbit."""
        import glfw

        stage = self.viewer.open()

        self.viewer.on_mouse_button(
            stage.window, glfw.MOUSE_BUTTON_LEFT, glfw.PRESS, 0,
        )
        self.assertTrue(self.viewer.dragging)

        self.viewer.on_mouse_button(
            stage.window, glfw.MOUSE_BUTTON_LEFT, glfw.RELEASE, 0,
        )
        self.assertFalse(self.viewer.dragging)

    def test_other_mouse_button_does_nothing(self) -> None:
        """Test that only the left button drags the cube around."""
        import glfw

        stage = self.viewer.open()

        self.viewer.on_mouse_button(
            stage.window, glfw.MOUSE_BUTTON_RIGHT, glfw.PRESS, 0,
        )

        self.assertFalse(self.viewer.dragging)

    def test_screenshot(self) -> None:
        """Test that a screenshot is a PNG of the window."""
        self.viewer.open()

        with TemporaryDirectory() as directory:
            path = Path(directory) / 'shot.png'

            self.assertEqual(self.viewer.screenshot(path), path)
            self.assertTrue(
                path.read_bytes().startswith(PNG_SIGNATURE),
            )

    def test_screenshot_key(self) -> None:
        """Test that F12 writes a screenshot of its own."""
        import glfw

        stage = self.viewer.open()

        with mock.patch(
                'cubing_algs.display.gl.viewer.screenshot_path',
        ) as destination, TemporaryDirectory() as directory:
            path = Path(directory) / 'shot.png'
            destination.return_value = path

            self.viewer.on_key(stage.window, glfw.KEY_F12, 0, glfw.PRESS, 0)

            self.assertTrue(path.exists())

    def test_resize_reaches_the_stage(self) -> None:
        """Test that the window and the framebuffer keep the same size."""
        stage = self.viewer.open()

        self.viewer.resize((64, 32))

        self.assertEqual(stage.size, (64, 32))

    def test_stage_holds_the_geometry_of_the_viewer(self) -> None:
        """Test that a stage is built for the geometry it draws."""
        geometry = self.viewer.geometry
        stage = Stage.open(WINDOW_SIZE, geometry, WINDOW_LOOK)

        self.assertEqual(
            stage.renderer.instance_buffer.size,
            len(geometry.cubies) * INSTANCE_SIZE,
        )

        stage.close()
