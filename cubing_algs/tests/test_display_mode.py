"""Tests for ModeDisplay methods."""
import unittest

from cubing_algs.display.vcube import VCubeDisplay
from cubing_algs.vcube import VCube


class ModeDisplayMixin:
    """Helper for creating VCubeDisplay instances in ModeDisplay tests."""

    @staticmethod
    def make_display(alg: str = '') -> VCubeDisplay:
        """
        Create a VCubeDisplay for a solved cube with optional moves applied.

        Returns:
            VCubeDisplay instance ready for method calls.

        """
        cube = VCube()
        if alg:
            cube.rotate(alg)
        return VCubeDisplay(cube)


class ComputeBestFrontFaceTestCase(ModeDisplayMixin, unittest.TestCase):
    """Tests for ModeDisplay.compute_best_front_face()."""

    def test_front_wins_on_tie(self) -> None:
        """
        Front face wins when all candidates
        have zero matching facelets.
        """
        display = self.make_display()
        result = display.compute_best_front_face('U', 'F')
        self.assertEqual(result, 'F')

    def test_different_front_wins_on_tie(self) -> None:
        """A different front face also wins when all candidates tie."""
        display = self.make_display()
        result = display.compute_best_front_face('U', 'R')
        self.assertEqual(result, 'R')

    def test_face_with_most_matches_wins(self) -> None:
        """Face with the most matching facelets wins over front on a tie."""
        # After F move: R gets 3 U-colored facelets; front F has 0
        display = self.make_display('F')
        result = display.compute_best_front_face('U', 'F')
        self.assertEqual(result, 'R')

    def test_bottom_color_winner(self) -> None:
        """Face with the most D-colored facelets wins."""
        # After F move: L gets 3 D-colored facelets
        display = self.make_display('F')
        result = display.compute_best_front_face('D', 'F')
        self.assertEqual(result, 'L')


class CrossTopOrientationTestCase(ModeDisplayMixin, unittest.TestCase):
    """Tests for ModeDisplay.cross_top_orientation()."""

    def test_solved_cube(self) -> None:
        """Solved cube returns default orientation 'UF'."""
        display = self.make_display()
        self.assertEqual(display.cross_top_orientation(), 'UF')

    def test_y_rotation_shifts_front(self) -> None:
        """After y rotation the new front (R) wins the zero-score tie."""
        display = self.make_display('y')
        self.assertEqual(display.cross_top_orientation(), 'UR')

    def test_f_move_selects_right_face(self) -> None:
        """After F move R has 3 U-colored facelets and wins."""
        display = self.make_display('F')
        self.assertEqual(display.cross_top_orientation(), 'UR')

    def test_b_move_selects_left_face(self) -> None:
        """After B move L has 3 U-colored facelets and wins."""
        display = self.make_display('B')
        self.assertEqual(display.cross_top_orientation(), 'UL')

    def test_r_move_selects_back_face(self) -> None:
        """After R move B has 3 U-colored facelets and wins."""
        display = self.make_display('R')
        self.assertEqual(display.cross_top_orientation(), 'UB')

    def test_l_move_keeps_front_face(self) -> None:
        """
        After L move F gains 3 U-colored facelets
        and wins as the highest scorer.
        """
        display = self.make_display('L')
        self.assertEqual(display.cross_top_orientation(), 'UF')


class CrossBottomOrientationTestCase(ModeDisplayMixin, unittest.TestCase):
    """Tests for ModeDisplay.cross_bottom_orientation()."""

    def test_solved_cube(self) -> None:
        """Solved cube returns default orientation 'UF'."""
        display = self.make_display()
        self.assertEqual(display.cross_bottom_orientation(), 'UF')

    def test_y_rotation_shifts_front(self) -> None:
        """After y rotation the new front (R) wins the zero-score tie."""
        display = self.make_display('y')
        self.assertEqual(display.cross_bottom_orientation(), 'UR')

    def test_f_move_selects_left_face(self) -> None:
        """After F move L has 3 D-colored facelets and wins."""
        display = self.make_display('F')
        self.assertEqual(display.cross_bottom_orientation(), 'UL')

    def test_b_move_selects_right_face(self) -> None:
        """After B move R has 3 D-colored facelets and wins."""
        display = self.make_display('B')
        self.assertEqual(display.cross_bottom_orientation(), 'UR')

    def test_r_move_keeps_front_face(self) -> None:
        """
        After R move F gains 3 D-colored facelets
        and wins as the highest scorer.
        """
        display = self.make_display('R')
        self.assertEqual(display.cross_bottom_orientation(), 'UF')

    def test_l_move_selects_back_face(self) -> None:
        """After L move B has 3 D-colored facelets and wins."""
        display = self.make_display('L')
        self.assertEqual(display.cross_bottom_orientation(), 'UB')
