"""
Tests for the interactive viewer of the GPU rendering backend.

Not one test here names glfw, and that is the point: a viewer holds a
cube, a camera and a queue of moves, and answers a neutral vocabulary of
input. What needs a GPU is drawn through a ``Stage`` attached to a
**headless** context — exactly what an embedded host hands over — so the
whole viewer is exercised without opening a window at all.

The glfw host has its own file, ``test_display_gl_host.py``.
"""
import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from typing import ClassVar
from unittest import mock

from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.gl.constants import SCREENSHOT_NAME
from cubing_algs.display.gl.constants import VIEWER_BACKGROUND
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.renderer import COLOR_CHANNELS
from cubing_algs.display.gl.renderer import AxesRenderer
from cubing_algs.display.gl.renderer import Renderer
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import OrientationTracker
from cubing_algs.display.gl.transforms import Quat
from cubing_algs.display.gl.viewer import Stage
from cubing_algs.display.gl.viewer import Viewer
from cubing_algs.display.gl.viewer import key_notation
from cubing_algs.display.gl.viewer import resolve_orientation
from cubing_algs.display.gl.viewer import screenshot_path
from cubing_algs.vcube import VCube

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

SCRAMBLE = "R U R' U' F' L F R"

WINDOW_SIZE = (128, 128)

# A stage is drawn into for real, so the shortest antialiasing that
# still exercises the multisampled path is enough here.
WINDOW_LOOK = Look(samples=2)

# The GPU rounds a color channel to a byte; two units of tolerance
# absorb that, and nothing more.
COLOR_TOLERANCE = 2


def probe_gpu() -> bool:
    """
    Tell whether this machine can create an OpenGL context.

    Returns:
        True when the drawing tests can run.

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


class TestKeyNotation(unittest.TestCase):
    """Tests for the key_notation function."""

    def test_face_key(self) -> None:
        """Test that a letter key turns the face it names."""
        self.assertEqual(key_notation('R'), 'R')

    def test_prime(self) -> None:
        """Test that shift turns a face the other way."""
        self.assertEqual(key_notation('U', prime=True), "U'")

    def test_double(self) -> None:
        """Test that ctrl turns a face twice."""
        self.assertEqual(key_notation('F', double=True), 'F2')

    def test_double_wins_over_prime(self) -> None:
        """Test that a half turn has no direction to be primed in."""
        self.assertEqual(
            key_notation('B', prime=True, double=True),
            'B2',
        )

    def test_wide_face(self) -> None:
        """Test that alt takes the layer behind a face along."""
        self.assertEqual(key_notation('L', wide=True), 'Lw')

    def test_wide_prime_face(self) -> None:
        """Test that a wide move is primed like any other."""
        self.assertEqual(
            key_notation('D', prime=True, wide=True),
            "Dw'",
        )

    def test_slice_key(self) -> None:
        """Test that a slice key turns the middle layer."""
        self.assertEqual(key_notation('M'), 'M')

    def test_slice_is_never_wide(self) -> None:
        """Test that widening a slice means nothing, and does nothing."""
        self.assertEqual(key_notation('S', wide=True), 'S')

    def test_rotation_key(self) -> None:
        """Test that a rotation key turns the whole cube, in lowercase."""
        self.assertEqual(key_notation('Y'), 'y')

    def test_rotation_is_never_wide(self) -> None:
        """Test that widening a rotation means nothing, and does nothing."""
        self.assertEqual(key_notation('X', wide=True, prime=True), "x'")

    def test_unknown_key(self) -> None:
        """Test that a key playing no move is turned into nothing."""
        self.assertEqual(key_notation('K'), '')

    def test_no_key_at_all(self) -> None:
        """Test that a key the host could not name plays nothing."""
        self.assertEqual(key_notation(''), '')


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

    def test_drawing_without_a_stage(self) -> None:
        """Test that a viewer nobody attached says so rather than crashing."""
        with self.assertRaises(GLContextError):
            self.viewer.draw()

    def test_screenshot_without_a_stage(self) -> None:
        """Test that a viewer nobody attached has nothing to capture."""
        with self.assertRaises(GLContextError):
            self.viewer.screenshot()

    def test_detaching_a_detached_viewer(self) -> None:
        """Test that giving a stage back twice is harmless."""
        self.viewer.detach()

        self.assertIsNone(self.viewer.stage)


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


class TestViewerInput(unittest.TestCase):
    """
    Tests for the neutral vocabulary a host speaks to a viewer.

    A letter and three modifiers, a movement in pixels, a number of
    notches: nothing here belongs to any toolkit, which is what lets a
    second host be written without touching the viewer.
    """

    def setUp(self) -> None:
        """Build a viewer on a solved cube."""
        self.viewer = Viewer(VCube(), window_size=WINDOW_SIZE)

    def test_press_plays_a_move(self) -> None:
        """Test that a letter queues the move it names."""
        self.assertTrue(self.viewer.press('R', prime=True))
        self.assertEqual(list(self.viewer.pending), ["R'"])

    def test_press_a_key_playing_nothing(self) -> None:
        """Test that a letter naming no move queues none."""
        self.assertFalse(self.viewer.press('K'))
        self.assertEqual(len(self.viewer.pending), 0)

    def test_press_a_wide_move(self) -> None:
        """Test that the modifiers reach the notation."""
        self.viewer.press('L', double=True, wide=True)

        self.assertEqual(list(self.viewer.pending), ['Lw2'])

    def test_drag_orbits_the_camera(self) -> None:
        """Test that dragging the mouse turns the cube the way it goes."""
        yaw, pitch = self.viewer.camera.yaw, self.viewer.camera.pitch

        self.viewer.drag(50.0, 20.0)

        self.assertLess(self.viewer.camera.yaw, yaw)
        self.assertGreater(self.viewer.camera.pitch, pitch)

    def test_drag_the_other_way(self) -> None:
        """Test that dragging back takes the camera back."""
        yaw = self.viewer.camera.yaw

        self.viewer.drag(-50.0, 0.0)

        self.assertGreater(self.viewer.camera.yaw, yaw)

    def test_scroll_zooms_in(self) -> None:
        """Test that scrolling forward brings the camera closer."""
        distance = self.viewer.camera.distance

        self.viewer.scroll(2.0)

        self.assertLess(self.viewer.camera.distance, distance)

    def test_scroll_zooms_out(self) -> None:
        """Test that scrolling backwards takes the camera away."""
        distance = self.viewer.camera.distance

        self.viewer.scroll(-2.0)

        self.assertGreater(self.viewer.camera.distance, distance)


@requires_gpu
class AttachedViewerTestCase(unittest.TestCase):
    """
    A viewer drawing into a stage built on a headless context.

    No window is opened: the context is standalone and the frames land
    in a framebuffer of the test. This is the very path an embedded host
    takes — a ``QOpenGLWidget`` hands over its own FBO the same way — so
    running the viewer here is what proves it needs no window.
    """

    context: ClassVar['moderngl.Context']

    @classmethod
    def setUpClass(cls) -> None:
        """Create the headless context every test of the class draws in."""
        cls.context = create_standalone_context()

    @classmethod
    def tearDownClass(cls) -> None:
        """Give the headless context back."""
        cls.context.release()

    def setUp(self) -> None:
        """Build a viewer on a scrambled cube, and a target for it."""
        cube = VCube()
        cube.rotate(SCRAMBLE)

        self.viewer = Viewer(
            cube, window_size=WINDOW_SIZE, look=WINDOW_LOOK,
        )
        self.target = self.context.simple_framebuffer(
            WINDOW_SIZE, COLOR_CHANNELS,
        )

    def tearDown(self) -> None:
        """Give back whatever the test attached."""
        self.viewer.detach()
        self.target.release()

    def attach(self) -> Stage:
        """
        Hand a stage over to the viewer, as a host would.

        Returns:
            The stage the viewer now draws into.

        """
        stage = Stage.attach(
            self.context, self.viewer.geometry, WINDOW_SIZE, self.target,
        )
        self.viewer.attach(stage)

        return stage

    def corner(self) -> tuple[int, ...]:
        """
        Read the pixel of the target no cube can reach.

        Returns:
            The four channels of the bottom left pixel.

        """
        pixels = self.target.read(components=COLOR_CHANNELS)

        return tuple(pixels[:COLOR_CHANNELS])


class TestStage(AttachedViewerTestCase):
    """Tests for the GPU side a host hands to a viewer."""

    def test_stage_holds_the_geometry_of_the_viewer(self) -> None:
        """Test that a stage is built for the geometry it draws."""
        geometry = self.viewer.geometry
        stage = self.attach()

        self.assertEqual(
            stage.renderer.instance_buffer.size,
            len(geometry.cubies) * INSTANCE_SIZE,
        )

    def test_a_stage_draws_into_the_target_it_was_given(self) -> None:
        """Test that a host framebuffer is the one a frame lands in."""
        stage = self.attach()

        self.assertIs(stage.framebuffer, self.target)

    def test_a_stage_without_a_target_draws_on_the_screen(self) -> None:
        """Test that a plain window needs no framebuffer of its own."""
        stage = Stage.attach(
            self.context, self.viewer.geometry, WINDOW_SIZE,
        )

        try:
            self.assertIs(stage.framebuffer, self.context.screen)
        finally:
            stage.close()

    def test_background_is_the_one_of_the_viewer(self) -> None:
        """Test that what the cube does not cover is the opaque grey."""
        self.attach()

        self.viewer.draw()

        for channel, expected in zip(
                self.corner(), VIEWER_BACKGROUND, strict=True,
        ):
            self.assertAlmostEqual(
                channel, round(expected * 255), delta=COLOR_TOLERANCE,
            )

    def test_background_is_a_field_a_host_may_change(self) -> None:
        """Test that an embedded stage lets the desktop through."""
        stage = self.attach()
        stage.background = (0.0, 0.0, 0.0, 0.0)

        self.viewer.draw()

        self.assertEqual(self.corner(), (0, 0, 0, 0))

    def test_closing_a_stage_leaves_the_context_alone(self) -> None:
        """Test that a stage never takes a host context down with it."""
        stage = Stage.attach(
            self.context, self.viewer.geometry, WINDOW_SIZE, self.target,
        )

        stage.close()

        # A released context builds nothing; this one still answers, as
        # a toolkit going on drawing with it needs it to.
        survivor = self.context.simple_framebuffer((4, 4), COLOR_CHANNELS)

        self.assertEqual(survivor.size, (4, 4))

        survivor.release()

    def test_detach_gives_the_stage_back(self) -> None:
        """Test that a viewer forgets the stage it was handed."""
        self.attach()

        self.viewer.detach()

        self.assertIsNone(self.viewer.stage)

    def test_attach_frames_on_the_size_of_the_stage(self) -> None:
        """Test that the surface truly given is the one framed on."""
        stage = Stage.attach(
            self.context, self.viewer.geometry, (256, 128), self.target,
        )

        self.viewer.attach(stage)

        self.assertEqual(self.viewer.camera.aspect, 2.0)


class TestViewerDrawing(AttachedViewerTestCase):
    """Tests for a viewer drawing frames into a stage."""

    def test_draw(self) -> None:
        """Test that a frame reaches the framebuffer of the stage."""
        self.attach()

        self.viewer.draw()

    def test_frame_lets_time_pass(self) -> None:
        """Test that a frame plays the move under way."""
        self.attach()
        self.viewer.push('R')

        self.viewer.frame(self.viewer.duration)

        self.assertIsNone(self.viewer.animation)

    def test_frame_draws_what_time_led_to(self) -> None:
        """Test that a frame is the scene the elapsed time built."""
        self.attach()
        self.viewer.push('R')

        self.viewer.frame(self.viewer.duration / 2)

        self.assertIsNotNone(self.viewer.animation)

    def test_screenshot(self) -> None:
        """Test that a screenshot is a PNG of what the viewer shows."""
        self.attach()

        with TemporaryDirectory() as directory:
            path = Path(directory) / 'shot.png'

            self.assertEqual(self.viewer.screenshot(path), path)
            self.assertTrue(
                path.read_bytes().startswith(PNG_SIGNATURE),
            )

    def test_axes_are_drawn_only_when_asked(self) -> None:
        """Test that the axes reach a frame once they are turned on."""
        self.attach()

        with mock.patch.object(AxesRenderer, 'draw') as drawn:
            self.viewer.draw()

            drawn.assert_not_called()

            self.viewer.show_axes = True
            self.viewer.draw()

        drawn.assert_called_once_with(self.viewer.camera, IDENTITY)

    def test_screenshot_holds_the_axes(self) -> None:
        """Test that a capture shows the axes the viewer shows."""
        self.viewer.show_axes = True
        self.attach()

        with (
                TemporaryDirectory() as folder,
                mock.patch.object(AxesRenderer, 'draw') as drawn,
        ):
            self.viewer.screenshot(Path(folder) / 'axes.png')

        drawn.assert_called_once_with(self.viewer.camera, IDENTITY)


class TestViewerHeldFromOutside(AttachedViewerTestCase):
    """Tests for a viewer drawing a cube something outside is holding."""

    def test_draw_hands_the_external_orientation_over(self) -> None:
        """Test that a frame is drawn with the cube held as it is."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())
        tracker.update(*Quat.from_axis_angle(AXIS_Y, math.pi / 2))

        self.viewer.orientation = tracker
        self.attach()

        with mock.patch.object(Renderer, 'draw') as drawn:
            self.viewer.draw()

        drawn.assert_called_once_with(
            self.viewer.scene,
            self.viewer.camera,
            self.viewer.look,
            tracker.orientation,
        )

    def test_screenshot_holds_the_external_orientation(self) -> None:
        """Test that a capture shows the cube as the viewer does."""
        quarter = Quat.from_axis_angle(AXIS_Y, math.pi / 2)

        self.viewer.orientation = quarter
        self.attach()

        with (
                TemporaryDirectory() as folder,
                mock.patch.object(Renderer, 'draw') as drawn,
        ):
            self.viewer.screenshot(Path(folder) / 'held.png')

        self.assertEqual(drawn.call_args.args[3], quarter)
