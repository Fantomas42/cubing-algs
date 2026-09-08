"""Tests for the presentation objects of the GPU rendering backend."""
import math
import unittest
from dataclasses import replace

from cubing_algs.display import gl
from cubing_algs.display.gl.constants import ANIMATION_LOOP
from cubing_algs.display.gl.constants import BOUNDING_RADIUS
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import FRAME_RATE
from cubing_algs.display.gl.constants import HOLD_END
from cubing_algs.display.gl.constants import HOLD_START
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.presentation import DEFAULT_PLAYBACK
from cubing_algs.display.gl.presentation import DEFAULT_PRESENTATION
from cubing_algs.display.gl.presentation import Playback
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.transforms import IDENTITY

# How far two angles may differ and still be the same one.
TOLERANCE = 1e-9


class TestPresentationDefaults(unittest.TestCase):
    """Tests for what a presentation asks for when asked nothing."""

    def test_the_default_is_the_library_default(self) -> None:
        """Test that an empty presentation draws the plain picture."""
        presentation = Presentation()

        self.assertEqual(presentation.palette, '')
        self.assertEqual(presentation.mode, '')
        self.assertEqual(presentation.mask, '')
        self.assertEqual(presentation.rotation, '')
        self.assertEqual(presentation.distance, 0.0)
        self.assertEqual(presentation.image_size, RENDER_SIZE)
        self.assertEqual(presentation.look, DEFAULT_LOOK)
        self.assertEqual(presentation.orientation, IDENTITY)

    def test_the_shared_default_is_the_empty_one(self) -> None:
        """Test that the module constant is the plain presentation."""
        self.assertEqual(DEFAULT_PRESENTATION, Presentation())

    def test_a_variant_is_one_replace_away(self) -> None:
        """Test that a presentation is frozen and copies cleanly."""
        variant = replace(DEFAULT_PRESENTATION, mode='oll')

        self.assertEqual(variant.mode, 'oll')
        self.assertEqual(DEFAULT_PRESENTATION.mode, '')
        self.assertEqual(variant.palette, DEFAULT_PRESENTATION.palette)

    def test_a_presentation_cannot_be_written_to(self) -> None:
        """Test that nothing changes a presentation under its caller."""
        with self.assertRaises(AttributeError):
            DEFAULT_PRESENTATION.mode = 'oll'  # type: ignore[misc]


class TestPresentationSize(unittest.TestCase):
    """Tests for the size a presentation hands to a framebuffer."""

    def test_the_size_is_square(self) -> None:
        """Test that an image size becomes the pair moderngl asks for."""
        self.assertEqual(Presentation(image_size=256).size, (256, 256))

    def test_the_default_size_is_the_render_one(self) -> None:
        """Test that nothing said means the default render size."""
        self.assertEqual(
            DEFAULT_PRESENTATION.size,
            (RENDER_SIZE, RENDER_SIZE),
        )


class TestPresentationCamera(unittest.TestCase):
    """Tests for the camera a presentation frames a cube with."""

    def test_the_rotation_reaches_the_camera(self) -> None:
        """Test that the rotation string is the one the camera reads."""
        camera = Presentation(rotation='y90').camera(BOUNDING_RADIUS)

        self.assertAlmostEqual(camera.yaw, math.radians(90), delta=TOLERANCE)

    def test_the_distance_reaches_the_camera(self) -> None:
        """Test that a distance given by hand is the one used."""
        camera = Presentation(distance=6.0).camera(BOUNDING_RADIUS)

        self.assertEqual(camera.distance, 6.0)

    def test_the_radius_frames_the_cube_it_is_given(self) -> None:
        """Test that a wider sphere is framed with a wider angle."""
        presentation = Presentation()

        self.assertGreater(
            presentation.camera(2.0).fov,
            presentation.camera(1.0).fov,
        )


class TestPlayback(unittest.TestCase):
    """Tests for how an animation is paced."""

    def test_the_default_is_the_library_default(self) -> None:
        """Test that an empty playback runs at the library pace."""
        playback = Playback()

        self.assertEqual(playback.frame_rate, FRAME_RATE)
        self.assertEqual(playback.duration, MOVE_DURATION)
        self.assertEqual(playback.loop, ANIMATION_LOOP)
        self.assertEqual(playback.hold_start, HOLD_START)
        self.assertEqual(playback.hold_end, HOLD_END)

    def test_the_shared_default_is_the_empty_one(self) -> None:
        """Test that the module constant is the plain playback."""
        self.assertEqual(DEFAULT_PLAYBACK, Playback())

    def test_a_playback_cannot_be_written_to(self) -> None:
        """Test that nothing changes a playback under its caller."""
        with self.assertRaises(AttributeError):
            DEFAULT_PLAYBACK.loop = 3  # type: ignore[misc]


class TestPlaybackDurations(unittest.TestCase):
    """Tests for how long each frame of an animation is shown."""

    def test_both_ends_are_held(self) -> None:
        """Test that the states an animation starts and ends on last."""
        playback = Playback(frame_rate=25.0, hold_start=0.8, hold_end=1.2)

        self.assertEqual(
            playback.durations(4),
            [0.8, 0.04, 0.04, 1.2],
        )

    def test_a_single_frame_is_held_as_the_end(self) -> None:
        """Test that a state reached by no move takes the last hold."""
        playback = Playback(frame_rate=25.0, hold_start=0.8, hold_end=1.2)

        self.assertEqual(playback.durations(1), [1.2])

    def test_no_frame_lasts_nothing(self) -> None:
        """Test that an empty animation has nothing to show."""
        self.assertEqual(Playback().durations(0), [])

    def test_a_hold_shorter_than_a_frame_is_ignored(self) -> None:
        """Test that a null hold plays the animation straight through."""
        playback = Playback(frame_rate=25.0, hold_start=0.0, hold_end=0.01)

        self.assertEqual(playback.durations(3), [0.04, 0.04, 0.04])


class TestPresentationLook(unittest.TestCase):
    """Tests for the look a presentation carries."""

    def test_a_look_travels_with_the_presentation(self) -> None:
        """Test that a variant look rides along rather than beside."""
        look = Look(ambient=0.1)
        presentation = Presentation(look=look)

        self.assertEqual(presentation.look, look)
        self.assertNotEqual(presentation.look, DEFAULT_LOOK)


class TestPublicDoor(unittest.TestCase):
    """Tests for what the sub-module hands to an outside caller."""

    def test_everything_a_render_needs_is_exported(self) -> None:
        """Test that a picture can be described without a deep import."""
        for name in ('Presentation', 'Playback', 'Look'):
            with self.subTest(name=name):
                self.assertIn(name, gl.__all__)
                self.assertTrue(hasattr(gl, name))

    def test_the_exported_classes_are_the_ones_of_the_modules(self) -> None:
        """Test that the door opens onto the very same classes."""
        self.assertIs(gl.Presentation, Presentation)
        self.assertIs(gl.Playback, Playback)
        self.assertIs(gl.Look, Look)
