"""Tests for the rotation strings every backend frames a cube with."""
import unittest

from cubing_algs.display.constants import ROTATION
from cubing_algs.display.rotation import fold_rotation
from cubing_algs.display.rotation import format_rotation
from cubing_algs.display.rotation import parse_rotation
from cubing_algs.display.rotation import turned_rotation
from cubing_algs.display.rotation import valid_rotation


class ValidRotationTestCase(unittest.TestCase):
    """Tests for the grammar of a framing."""

    def test_axis_and_angle_parts(self) -> None:
        """Test that the usual framings are read."""
        for rotation in ('y45', 'y45x-34', 'x20y45z10', 'y-30', 'x0'):
            with self.subTest(rotation=rotation):
                self.assertTrue(valid_rotation(rotation))

    def test_anything_else(self) -> None:
        """Test that what names no framing is refused."""
        for rotation in ('', 'nonsense', 'y45garbage', 'w45', 'y'):
            with self.subTest(rotation=rotation):
                self.assertFalse(valid_rotation(rotation))


class ParseRotationTestCase(unittest.TestCase):
    """Tests for rotation string parsing."""

    def test_single_axis(self) -> None:
        """Test parsing a single axis rotation."""
        result = parse_rotation('y45')
        self.assertEqual(result, [('y', 45)])

    def test_two_axes(self) -> None:
        """Test parsing two axis rotations."""
        result = parse_rotation('y45x-25')
        self.assertEqual(result, [('y', 45), ('x', -25)])

    def test_three_axes(self) -> None:
        """Test parsing three axis rotations."""
        result = parse_rotation('x20y45z10')
        self.assertEqual(
            result, [('x', 20), ('y', 45), ('z', 10)],
        )

    def test_negative_angle(self) -> None:
        """Test parsing negative angle."""
        result = parse_rotation('y-30')
        self.assertEqual(result, [('y', -30)])

    def test_zero_angle(self) -> None:
        """Test parsing zero angle."""
        result = parse_rotation('x0')
        self.assertEqual(result, [('x', 0)])

    def test_large_angle(self) -> None:
        """Test parsing angle above 360."""
        result = parse_rotation('y999')
        self.assertEqual(result, [('y', 999)])

    def test_empty_string(self) -> None:
        """Test that empty string returns default value."""
        result = parse_rotation('')
        self.assertEqual(result, [('y', 45), ('x', -34)])

    def test_partial_match_raises(self) -> None:
        """Test that partially valid string returns default value."""
        result = parse_rotation('y45garbage')
        self.assertEqual(result, [('y', 45), ('x', -34)])


class FoldRotationTestCase(unittest.TestCase):
    """Tests for adding the parts of a framing up."""

    def test_every_axis_is_answered(self) -> None:
        """Test that an axis nothing turns comes back at zero."""
        self.assertEqual(
            fold_rotation('y45x-34'),
            {'y': 45, 'x': -34, 'z': 0},
        )

    def test_repeated_axes_add_up(self) -> None:
        """Test that a chain turning twice around an axis is summed."""
        self.assertEqual(fold_rotation('y30y15')['y'], 45)

    def test_empty_is_the_library_framing(self) -> None:
        """Test that nothing typed is the default of the library."""
        self.assertEqual(fold_rotation(''), fold_rotation(ROTATION))


class FormatRotationTestCase(unittest.TestCase):
    """Tests for writing a framing back out."""

    def test_the_axes_are_written_in_camera_order(self) -> None:
        """Test that a framing reads yaw, pitch, roll whatever built it."""
        self.assertEqual(
            format_rotation({'x': -34, 'z': 10, 'y': 45}),
            'y45x-34z10',
        )

    def test_an_axis_turning_nothing_is_left_out(self) -> None:
        """Test that a null pitch and roll are not written."""
        self.assertEqual(
            format_rotation({'y': 45, 'x': 0, 'z': 0}), 'y45',
        )

    def test_the_yaw_is_written_whatever_it_says(self) -> None:
        """Test that a framing is never written as an empty string."""
        self.assertEqual(
            format_rotation({'y': 0, 'x': 0, 'z': 0}), 'y0',
        )

    def test_what_is_written_is_read_back(self) -> None:
        """Test that a framing survives a round trip through both."""
        for rotation in ('y45x-34', 'y0', 'y90x-20', 'y45x-34z10'):
            with self.subTest(rotation=rotation):
                self.assertEqual(
                    format_rotation(fold_rotation(rotation)), rotation,
                )


class TurnedRotationTestCase(unittest.TestCase):
    """Tests for turning a framing and writing where it lands."""

    def test_the_angle_landed_on_is_written(self) -> None:
        """Test that what comes out is a framing, not a pile of turns."""
        self.assertEqual(turned_rotation('y45x-34', yaw=180), 'y225x-34')

    def test_a_full_revolution_comes_back(self) -> None:
        """Test that a turned axis is brought inside one revolution."""
        self.assertEqual(turned_rotation('y270x-20', yaw=180), 'y90x-20')
        self.assertEqual(turned_rotation('y180', yaw=180), 'y0')

    def test_an_untouched_axis_is_written_as_it_was_read(self) -> None:
        """Test that an elevation is left alone rather than wrapped."""
        self.assertEqual(turned_rotation('x-34', yaw=180), 'y180x-34')

    def test_the_pitch_and_the_roll_turn_too(self) -> None:
        """Test that the three axes are all reachable."""
        self.assertEqual(
            turned_rotation('y45', pitch=-34, roll=10), 'y45x326z10',
        )

    def test_turning_by_nothing_writes_the_framing_out(self) -> None:
        """Test that a null turn still normalizes what it was given."""
        self.assertEqual(turned_rotation('y30y15'), 'y45')

    def test_empty_is_the_library_framing(self) -> None:
        """Test that a framing nobody typed is the one of the library."""
        self.assertEqual(turned_rotation(''), ROTATION)
