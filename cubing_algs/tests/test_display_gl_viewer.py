"""
Tests for the interactive viewer of the GPU rendering backend.

Not one test here names glfw, and that is the point: a viewer holds a
cube, a camera and a queue of moves, and answers a neutral vocabulary of
input. What needs a GPU is drawn through a ``Stage`` attached to a
**headless** context - exactly what an embedded host hands over - so the
whole viewer is exercised without opening a window at all.

The glfw host has its own file, ``test_display_gl_host.py``.
"""
import math
import unittest
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from typing import ClassVar
from unittest import mock

from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.gl.constants import COLOR_CHANNELS
from cubing_algs.display.gl.constants import EXPLODE_SPREAD
from cubing_algs.display.gl.constants import SCREENSHOT_NAME
from cubing_algs.display.gl.constants import VIEWER_BACKGROUND
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.encode import PNG_SIGNATURE
from cubing_algs.display.gl.renderer import AxesRenderer
from cubing_algs.display.gl.renderer import Renderer
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.scene import Color
from cubing_algs.display.gl.transforms import AXIS_Y
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import ORIGIN
from cubing_algs.display.gl.transforms import OrientationTracker
from cubing_algs.display.gl.transforms import Quat
from cubing_algs.display.gl.transforms import Vec3
from cubing_algs.display.gl.viewer import CUBE_DRAW_CALLS
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


def queued(viewer: Viewer) -> list[str]:
    """
    Read the notations a viewer has queued, dates left out.

    Args:
        viewer: The viewer to read the queue of.

    Returns:
        The notations waiting to be played, in order.

    """
    return [notation for notation, _arrival in viewer.pending]


def play(viewer: Viewer, moves: int = 1) -> None:
    """
    Let a viewer play what it was handed, one beat at a time.

    A move starts when it arrives rather than when the frame drawing it
    begins, so a move pushed just now takes one beat to start turning
    and one more to land.

    Args:
        viewer: The viewer to advance.
        moves: How many moves are waiting to be played.

    """
    for _frame in range(moves + 1):
        viewer.advance(viewer.duration)


class FakeClock:
    """
    A clock a test moves by hand, standing in for ``perf_counter()``.

    A viewer stamps a move with the moment it arrived, so telling what
    cadence a producer holds means telling what the clock said when it
    pushed.
    """

    def __init__(self, now: float = 0.0) -> None:
        """Start the clock where the test wants it."""
        self.now = now

    def __call__(self) -> float:
        """
        Read the clock.

        Returns:
            The moment the test has set.

        """
        return self.now


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
        tracker.advance(1.0)

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
        play(self.viewer)

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
        self.assertEqual(queued(self.viewer), ['R'])

    def test_push_nothing(self) -> None:
        """Test that a key playing no move queues nothing."""
        self.assertFalse(self.viewer.push(''))
        self.assertEqual(len(self.viewer.pending), 0)

    def test_push_a_timed_move(self) -> None:
        """Test that a producer stamping its moves is not turned away."""
        self.assertTrue(self.viewer.push('R@100'))

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
        play(self.viewer)

        self.assertEqual(self.viewer.cube.state, expected.state)
        self.assertTrue(self.viewer.animation.finished)

    def test_advance_turns_before_landing(self) -> None:
        """Test that a move under way is drawn part of the way round."""
        resting = self.viewer.scene

        self.viewer.push('R')
        self.viewer.advance(self.viewer.duration)
        turning = self.viewer.advance(self.viewer.duration / 2)

        self.assertFalse(self.viewer.animation.finished)
        self.assertNotEqual(turning.instances, resting.instances)
        self.assertEqual(self.viewer.cube.state, self.cube.state)

    def test_advance_plays_the_moves_in_order(self) -> None:
        """Test that a queue of moves is played one move at a time."""
        expected = self.cube.copy()
        expected.rotate("R U'")

        self.viewer.push('R')
        self.viewer.push("U'")

        play(self.viewer, moves=2)

        self.assertEqual(self.viewer.cube.state, expected.state)
        self.assertEqual(len(self.viewer.pending), 0)

    def test_advance_without_anything_to_play(self) -> None:
        """Test that an idle viewer keeps drawing the cube at rest."""
        self.assertIs(self.viewer.advance(1.0), self.viewer.scene)

    def test_advance_drives_an_orientation_tracker(self) -> None:
        """Test that a tracker set as the orientation is fed the frame time."""
        tracker = OrientationTracker()
        tracker.update(*Quat.identity())
        tracker.update(*Quat.from_axis_angle(AXIS_Y, math.pi / 2))
        self.viewer.orientation = tracker

        self.viewer.advance(1.0)

        self.assertEqual(
            tracker.orientation,
            Quat.from_axis_angle(AXIS_Y, math.pi / 2),
        )

    def test_advance_plays_a_cube_swapped_from_outside(self) -> None:
        """Test that a cube put in the viewer by hand is the one played on."""
        other = VCube()
        other.rotate('F')

        self.viewer.cube = other
        self.viewer.push('R')
        play(self.viewer)

        expected = VCube()
        expected.rotate('F R')

        self.assertEqual(self.viewer.cube.state, expected.state)

    def test_a_burst_of_moves_never_leaves_the_cube_behind(self) -> None:
        """Test that hammering the keyboard is caught up with, not queued."""
        hammered = 'R U F R U F R U F R'

        expected = self.cube.copy()
        expected.rotate(hammered)

        for notation in hammered.split():
            self.viewer.push(notation)

        frame = 1.0 / 60.0
        played = 0.0

        while self.viewer.pending or not self.viewer.animation.finished:
            self.viewer.advance(frame)
            played += frame

        self.assertEqual(self.viewer.cube.state, expected.state)
        self.assertLess(played, 10 * self.viewer.duration)

    def test_the_cadence_is_the_one_the_moves_arrived_at(self) -> None:
        """Test that a move lasts the gap the producer left behind it."""
        clock = FakeClock()

        with mock.patch(
                'cubing_algs.display.gl.viewer.time.perf_counter', clock,
        ):
            self.viewer.push('R')

            clock.now = 0.1
            self.viewer.advance(0.1)

            clock.now = 0.2
            self.viewer.push('U')
            self.viewer.advance(0.1)

        self.assertAlmostEqual(self.viewer.animation.step, 0.2)

    def test_reset_cube(self) -> None:
        """Test that the cube goes back to the state it was opened on."""
        self.viewer.push('R')
        play(self.viewer)
        self.viewer.push('U')

        self.viewer.reset_cube()

        self.assertEqual(self.viewer.cube.state, self.cube.state)
        self.assertEqual(len(self.viewer.pending), 0)
        self.assertTrue(self.viewer.animation.finished)

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


class TestViewerAgedMoves(unittest.TestCase):
    """Tests for a move that is already over when it is pushed."""

    def setUp(self) -> None:
        """Build a viewer on a scrambled cube."""
        self.cube = VCube()
        self.cube.rotate(SCRAMBLE)

        self.viewer = Viewer(self.cube, window_size=WINDOW_SIZE)

    def test_push_an_aged_move_dates_it_back(self) -> None:
        """Test that a move already over is queued where it happened."""
        clock = FakeClock(now=1.0)

        with mock.patch(
                'cubing_algs.display.gl.viewer.time.perf_counter', clock,
        ):
            self.viewer.push('R')
            self.viewer.push('U', age=0.1)

        fresh, aged = (arrival for _, arrival in self.viewer.pending)

        self.assertAlmostEqual(fresh - aged, 0.1)

    def test_push_an_age_never_runs_backwards(self) -> None:
        """Test that nothing is ever played before it is pushed."""
        clock = FakeClock(now=1.0)

        with mock.patch(
                'cubing_algs.display.gl.viewer.time.perf_counter', clock,
        ):
            self.viewer.push('R', age=-1.0)
            self.viewer.push('U')

        first, second = (arrival for _, arrival in self.viewer.pending)

        self.assertAlmostEqual(first, second)

    def test_an_aged_move_starts_the_turn_part_way_through(self) -> None:
        """
        Test that a move as old as its beat lands without waiting.

        This is the whole of what an age buys: the turn is started where
        it would already stand rather than from zero, so a move older
        than the beat has nothing left to turn at all.

        The animation is let run first, and it has to be: an age dates a
        move back, and a date landing before the animation existed is
        held at its origin by ``max(date, end)``. So an age only counts
        for what the clock of the animation has already run, which is a
        matter of the frames following a ``reload()`` and of nothing
        else.
        """
        expected = self.cube.copy()
        expected.rotate('R')

        self.viewer.advance(self.viewer.duration * 4)
        self.viewer.push('R', age=self.viewer.duration * 2)
        self.viewer.advance(0.0)

        self.assertEqual(self.viewer.cube.state, expected.state)


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
        self.assertEqual(queued(self.viewer), ["R'"])

    def test_press_a_key_playing_nothing(self) -> None:
        """Test that a letter naming no move queues none."""
        self.assertFalse(self.viewer.press('K'))
        self.assertEqual(len(self.viewer.pending), 0)

    def test_press_a_wide_move(self) -> None:
        """Test that the modifiers reach the notation."""
        self.viewer.press('L', double=True, wide=True)

        self.assertEqual(queued(self.viewer), ['Lw2'])

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
class TestViewerExplosion(unittest.TestCase):
    """Tests for the cube a viewer opens up, and puts back together."""

    def setUp(self) -> None:
        """Build a viewer on a solved cube."""
        self.viewer = Viewer(VCube(), window_size=WINDOW_SIZE)

    def settle(self) -> None:
        """Let the cube reach the state it is asked for."""
        for _frame in range(20):
            self.viewer.advance(0.1)

    def test_a_new_viewer_is_closed(self) -> None:
        """Test that a cube opens on nothing but itself."""
        self.assertFalse(self.viewer.exploded)
        self.assertEqual(self.viewer.spread, 0.0)
        self.assertIs(self.viewer.scene, self.viewer.assembled)

    def test_the_cube_travels_rather_than_jumping(self) -> None:
        """Test that one frame only carries a share of the way."""
        self.viewer.exploded = True
        self.viewer.advance(0.05)

        self.assertGreater(self.viewer.spread, 0.0)
        self.assertLess(self.viewer.spread, EXPLODE_SPREAD)

    def test_an_open_cube_reaches_what_it_is_asked_for(self) -> None:
        """Test that the opening lands exactly on its target."""
        self.viewer.exploded = True
        self.settle()

        self.assertEqual(self.viewer.spread, EXPLODE_SPREAD)

    def test_the_pieces_stand_apart(self) -> None:
        """Test that an open cube draws its pieces away from the center."""
        self.viewer.exploded = True
        self.settle()

        for closed, opened in zip(
                self.viewer.assembled.instances,
                self.viewer.scene.instances,
                strict=True,
        ):
            for place, expected in zip(
                    opened.model.transform_point(ORIGIN),
                    closed.cubie.center.scaled(1.0 + EXPLODE_SPREAD),
                    strict=True,
            ):
                self.assertAlmostEqual(place, expected)

    def test_the_cube_is_put_back_together(self) -> None:
        """Test that a closed cube is the scene the animation built."""
        self.viewer.exploded = True
        self.settle()

        self.viewer.exploded = False
        self.settle()

        self.assertEqual(self.viewer.spread, 0.0)
        self.assertIs(self.viewer.scene, self.viewer.assembled)

    def test_a_settled_cube_is_never_rebuilt(self) -> None:
        """Test that an open cube standing still hands the same scene back."""
        self.viewer.exploded = True
        self.settle()

        scene = self.viewer.scene

        self.assertIs(self.viewer.advance(0.1), scene)

    def test_opening_the_cube_leaves_the_camera_alone(self) -> None:
        """Test that the camera never stands back as the cube grows."""
        camera = replace(self.viewer.camera)

        self.viewer.exploded = True
        self.settle()

        self.assertEqual(self.viewer.camera, camera)

    def test_a_move_lands_on_an_open_cube(self) -> None:
        """Test that a cube goes on turning while it stands open."""
        self.viewer.exploded = True
        self.settle()

        expected = VCube()
        expected.rotate('R')

        self.viewer.push('R')
        play(self.viewer)

        self.assertEqual(self.viewer.cube.state, expected.state)
        self.assertIsNot(self.viewer.scene, self.viewer.assembled)

    def places(self) -> dict[frozenset[Color], Vec3]:
        """
        Read where every piece of the cube is drawn right now.

        A piece is named by the colors it carries, which travel with it:
        the instances are indexed by the cell of the grid they fill, and
        a move hands a cell over to another piece.

        Returns:
            The place each piece is drawn at, the mesh being centered on
            its own origin.

        """
        return {
            frozenset(instance.colors):
                instance.model.transform_point(ORIGIN)
            for instance in self.viewer.scene.instances
        }

    def test_a_move_lands_without_a_jump(self) -> None:
        """
        Test that an open cube turns as one piece, right to the end.

        A turning layer flies along the place it is heading for rather
        than along the one it left, so the last frame of a move and the
        scene rebuilt on the cube it landed on draw a piece at the very
        same place. Composed the other way round - the offset applied on
        top of the model matrix rather than into it - a corner of an
        open 3x3 jumped by 0.95 on that one frame, against 0.18 for the
        fastest frame of the turn itself.
        """
        self.viewer.exploded = True
        self.settle()

        self.viewer.push('R')
        self.viewer.advance(0.0)

        before = self.places()
        steps = []

        while not self.viewer.animation.finished:
            self.viewer.advance(self.viewer.duration / 12)
            places = self.places()
            steps.append(
                max(
                    max(
                        abs(now - was)
                        for now, was in zip(place, before[piece], strict=True)
                    )
                    for piece, place in places.items()
                ),
            )
            before = places

        self.assertLessEqual(steps[-1], max(steps[:-1]))

    def test_a_reset_cube_stays_open(self) -> None:
        """Test that a fresh animation is built into the open cube."""
        self.viewer.exploded = True
        self.settle()

        self.viewer.reset_cube()

        self.assertIsNot(self.viewer.scene, self.viewer.assembled)
        for place, expected in zip(
                self.viewer.scene.instances[0].model.transform_point(ORIGIN),
                self.viewer.assembled.instances[0].cubie.center.scaled(
                    1.0 + EXPLODE_SPREAD,
                ),
                strict=True,
        ):
            self.assertAlmostEqual(place, expected)


class AttachedViewerTestCase(unittest.TestCase):
    """
    A viewer drawing into a stage built on a headless context.

    No window is opened: the context is standalone and the frames land
    in a framebuffer of the test. This is the very path an embedded host
    takes - a ``QOpenGLWidget`` hands over its own FBO the same way - so
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
        """Test that what the cube does not cover is the opaque ground."""
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
        self.viewer.frame(self.viewer.duration)

        self.assertTrue(self.viewer.animation.finished)

    def test_frame_draws_what_time_led_to(self) -> None:
        """Test that a frame is the scene the elapsed time built."""
        self.attach()
        self.viewer.push('R')

        self.viewer.frame(self.viewer.duration / 2)

        self.assertFalse(self.viewer.animation.finished)

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


class TestViewerDrawnThroughEffects(AttachedViewerTestCase):
    """Tests for the frame a host layering effects asks for."""

    def test_a_frame_is_drawn_with_what_it_is_given(self) -> None:
        """Test that the three overrides are what reaches the renderer."""
        self.attach()

        scene = replace(self.viewer.scene, instances=())
        look = replace(self.viewer.look, ambient=0.1)
        camera = replace(self.viewer.camera, distance=42.0)

        with mock.patch.object(Renderer, 'draw') as drawn:
            self.viewer.draw(scene=scene, look=look, camera=camera)

        drawn.assert_called_once_with(scene, camera, look, IDENTITY)

    def test_a_frame_of_its_own_leaves_the_viewer_alone(self) -> None:
        """
        Test that an effect never lands in the state of the viewer.

        The camera is what this is really about: the mouse writes to it
        too, so an effect leaking into it would drag the cube away one
        frame at a time.
        """
        self.attach()

        scene, look, camera = (
            self.viewer.scene, self.viewer.look, self.viewer.camera,
        )
        distance = camera.distance

        self.viewer.draw(
            scene=replace(scene, instances=()),
            look=replace(look, ambient=0.1),
            camera=replace(camera, distance=distance * 2),
        )

        self.assertIs(self.viewer.scene, scene)
        self.assertIs(self.viewer.look, look)
        self.assertIs(self.viewer.camera, camera)
        self.assertEqual(camera.distance, distance)

    def test_what_is_left_out_comes_from_the_viewer(self) -> None:
        """Test that a partial override draws the rest as it stands."""
        self.attach()

        look = replace(self.viewer.look, ambient=0.1)

        with mock.patch.object(Renderer, 'draw') as drawn:
            self.viewer.draw(look=look)

        drawn.assert_called_once_with(
            self.viewer.scene, self.viewer.camera, look, IDENTITY,
        )

    def test_the_axes_follow_the_camera_they_are_drawn_with(self) -> None:
        """Test that an effect moving the camera moves the axes too."""
        self.viewer.show_axes = True
        self.attach()

        camera = replace(self.viewer.camera, distance=42.0)

        with mock.patch.object(AxesRenderer, 'draw') as drawn:
            self.viewer.draw(camera=camera)

        drawn.assert_called_once_with(camera, IDENTITY)


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


class TestViewerMonitoring(AttachedViewerTestCase):
    """Tests for what a viewer measures of its own frames."""

    def test_the_two_halves_of_a_frame_are_always_measured(self) -> None:
        """Test that a frame is timed whether it is watched or not."""
        self.attach()

        self.viewer.frame(0.01)

        monitor = self.viewer.monitor
        self.assertEqual(monitor.advance.count, 1)
        self.assertEqual(monitor.draw.count, 1)
        self.assertGreater(monitor.draw.mean, 0.0)

    def test_the_gpu_is_left_alone_until_it_is_asked_for(self) -> None:
        """Test that the one measure that costs stays off by default."""
        self.attach()

        self.viewer.draw()
        self.viewer.draw()

        self.assertEqual(self.viewer.monitor.gpu.count, 0)

    def test_the_gpu_is_timed_one_frame_late(self) -> None:
        """
        Test that a timer answers for the frame before the one drawn.

        Reading a query right after the draw would wait on the GPU,
        which is the very pipeline the timer is there to measure: the
        first frame therefore records nothing, and the second one
        carries what the first cost.
        """
        self.attach()
        self.viewer.debug = True

        self.viewer.draw()
        self.assertEqual(self.viewer.monitor.gpu.count, 0)

        self.viewer.draw()

        self.assertEqual(self.viewer.monitor.gpu.count, 1)
        self.assertGreater(self.viewer.monitor.gpu.mean, 0.0)

    def test_a_driver_without_a_timer_still_draws(self) -> None:
        """Test that a missing timer query costs a line, not a frame."""
        stage = self.attach()
        stage.timer = None
        self.viewer.debug = True

        self.viewer.draw()

        self.assertEqual(self.viewer.monitor.gpu.count, 0)

    def test_closing_a_stage_drops_its_timer(self) -> None:
        """Test that a query goes with the stage that built it."""
        stage = self.attach()

        self.assertIsNotNone(stage.timer)

        stage.close()

        self.assertIsNone(stage.timer)

    def test_the_profile_counts_what_a_frame_draws(self) -> None:
        """Test that the profile is read off the scene being drawn."""
        stage = self.attach()

        profile = self.viewer.profile()

        instances = len(self.viewer.scene.instances)
        self.assertEqual(profile.instances, instances)
        self.assertEqual(profile.instance_bytes, instances * INSTANCE_SIZE)
        self.assertEqual(
            profile.triangles,
            instances * self.viewer.geometry.mesh.triangle_count,
        )
        self.assertEqual(profile.size, stage.size)
        self.assertEqual(profile.samples, self.viewer.look.samples)

    def test_the_profile_names_the_context(self) -> None:
        """Test that a report says which GPU drew the frames."""
        self.attach()

        self.assertIn('-', self.viewer.profile().context)

    def test_the_axes_are_a_draw_call_of_their_own(self) -> None:
        """Test that showing the axes shows in the draw calls."""
        self.attach()

        self.assertEqual(self.viewer.profile().draw_calls, CUBE_DRAW_CALLS)

        self.viewer.show_axes = True

        self.assertEqual(
            self.viewer.profile().draw_calls, CUBE_DRAW_CALLS + 1,
        )

    def test_a_profile_needs_a_stage(self) -> None:
        """Test that nothing is profiled before a host attaches one."""
        with self.assertRaises(GLContextError):
            self.viewer.profile()
