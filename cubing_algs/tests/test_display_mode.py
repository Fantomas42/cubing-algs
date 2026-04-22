"""Tests for ModeDisplay methods."""
import unittest

from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.display.masks import OLL_MASK
from cubing_algs.display.masks import PLL_MASK
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
        """Solved cube does not return new orientation."""
        display = self.make_display()
        self.assertEqual(display.cross_top_orientation(), '')

    def test_y_rotation_shifts_front(self) -> None:
        """After y rotation on solved cube does not return new orientation."""
        display = self.make_display('y')
        self.assertEqual(display.cross_top_orientation(), '')

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
        But already in UF so no rotations.
        """
        display = self.make_display('L')
        self.assertEqual(display.cross_top_orientation(), '')


class CrossBottomOrientationTestCase(ModeDisplayMixin, unittest.TestCase):
    """Tests for ModeDisplay.cross_bottom_orientation()."""

    def test_solved_cube(self) -> None:
        """Solved cube does not return new orientation."""
        display = self.make_display()
        self.assertEqual(display.cross_bottom_orientation(), '')

    def test_y_rotation_shifts_front(self) -> None:
        """After y rotation on solved cube does not return new orientation."""
        display = self.make_display('y')
        self.assertEqual(display.cross_bottom_orientation(), '')

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
        But already in UF so no rotations.
        """
        display = self.make_display('R')
        self.assertEqual(display.cross_bottom_orientation(), '')

    def test_l_move_selects_back_face(self) -> None:
        """After L move B has 3 D-colored facelets and wins."""
        display = self.make_display('L')
        self.assertEqual(display.cross_bottom_orientation(), 'UB')


class F2LOrientationTestCase(ModeDisplayMixin, unittest.TestCase):
    """
    Tests for ModeDisplay.f2l_orientation().

    The method scans each side face's bottom rows (below the first row) to find
    which faces have non-uniform facelets (``impacted``). Based on the number
    of impacted faces it infers the active F2L slot and returns an orientation
    string.

    NOTE: Behaviour for 3 or 4 impacted faces is under review — the method
    overwrites ``saved_facelets`` each iteration, so only the *last* impacted
    face's facelets drive the slot inference when more than two faces are
    affected. Tests for those cases document the current output without
    asserting it is correct.
    """

    # ------------------------------------------------------------------
    # 0 impacted faces
    # ------------------------------------------------------------------

    def test_solved_cube_returns_top_only(self) -> None:
        """Solved cube has no impacted faces; no orientation."""
        display = self.make_display()
        self.assertEqual(display.f2l_orientation(), '')

    def test_u_layer_only_moves_leave_f2l_intact(self) -> None:
        """U-layer moves don't touch F2L rows; no orientation."""
        display = self.make_display('z2 U2')
        self.assertEqual(display.f2l_orientation(), '')

    # ------------------------------------------------------------------
    # 2 impacted faces — opposite-face pairs (no valid slot)
    # ------------------------------------------------------------------

    def test_opposite_faces_impacted_returns_no_front(self) -> None:
        """F+B are impacted but form no corner slot; no front is appended."""
        # z2 R moves U-colored facelets onto B and D-colored onto F:
        # (F,B) is not an F2L corner slot so F2L_FACE_ORIENTATIONS returns ''.
        display = self.make_display('z2 R')
        self.assertEqual(display.f2l_orientation(), '')

    # ------------------------------------------------------------------
    # 2 impacted faces — valid F2L corner slots
    # ------------------------------------------------------------------

    def test_fl_slot(self) -> None:
        """F and L both impacted → FL slot → front F."""
        display = self.make_display("z2 R' D' R U R' D R U'")
        self.assertEqual(display.f2l_orientation(), 'DF')

    def test_bl_slot(self) -> None:
        """L and B both impacted → BL slot → front L."""
        display = self.make_display("y' z2 R U R' U'")
        self.assertEqual(display.f2l_orientation(), 'DL')

    def test_br_slot(self) -> None:
        """R and B both impacted → BR slot → front B."""
        display = self.make_display("z2 L U' L' U' L U L' U' L U2 L'")
        self.assertEqual(display.f2l_orientation(), 'DB')

    # ------------------------------------------------------------------
    # 1 impacted face — slot inferred from saved_facelets
    # ------------------------------------------------------------------

    def test_one_impacted_face_fr_slot(self) -> None:
        """Only R face impacted; slot inferred as FR → front R."""
        display = self.make_display("z2 F' L F L'")
        self.assertEqual(display.f2l_orientation(), 'DR')

    def test_one_impacted_face_fl_slot(self) -> None:
        """Only L face impacted; slot inferred as FL → front F."""
        display = self.make_display("z2 R U' R' U R U' R' U R U' R'")
        self.assertEqual(display.f2l_orientation(), 'DF')

    # ------------------------------------------------------------------
    # y-rotation invariance — same F2L state, different cube orientation
    # ------------------------------------------------------------------

    def test_y_rotation_invariance(self) -> None:
        """Same F2L sequence under each y rotation maps to a distinct slot."""
        base = "z2 R U' R' U R' F R F' U"
        expected = {
            '':   'DF',
            'y':  'DR',
            'y2': 'DB',
            "y'": 'DL',
        }
        for prefix, orientation in expected.items():
            with self.subTest(prefix=prefix or 'none'):
                alg = f'{prefix} {base}' if prefix else base
                display = self.make_display(alg)
                self.assertEqual(display.f2l_orientation(), orientation)

    # ------------------------------------------------------------------
    # Edge cases: 3 and 4 impacted faces (under review — may be buggy)
    # ------------------------------------------------------------------

    def test_three_impacted_faces_current_behaviour(self) -> None:
        """
        With 3 impacted faces the method falls into the 1-face branch.

        ``saved_facelets`` holds only the *last* impacted face's facelets,
        so the slot inference is driven by that face alone — the other two
        impacted faces are ignored. This behaviour is under review.
        """
        display = self.make_display('z2 R F B')
        self.assertEqual(display.f2l_orientation(), 'DF')

    def test_four_impacted_faces_current_behaviour(self) -> None:
        """
        With all 4 faces impacted the method again falls into the 1-face branch.

        Only the last impacted face's facelets are used to determine the slot.
        This behaviour is under review.
        """
        display = self.make_display('z2 R F B L')
        self.assertEqual(display.f2l_orientation(), 'DB')

    # Issues found

    def test_issue_01(self) -> None:
        """Reproduce issue #01."""
        for orientation, solution in zip(
                ('', 'y', "y'", 'y2'),
                ('UF', 'UR', 'UL', 'UB'),
                strict=True,
        ):
            with self.subTest(orientation=orientation):
                display = self.make_display(
                    f"{ orientation } R U R' U' M",
                )
                self.assertEqual(display.f2l_orientation(), solution)

    def test_issue_02(self) -> None:
        """Reproduce issue #02."""
        for solution, orientation in ORIENTATION_FACE_MOVES.items():
            with self.subTest(orientation=orientation):
                display = self.make_display(
                    f"{ orientation } R U' R' U R' F R F' U",
                )
                self.assertEqual(display.f2l_orientation(), solution)


class RealignMaskTestCase(ModeDisplayMixin, unittest.TestCase):
    """Tests for ModeDisplay.realign_mask()."""

    def test_default_orientation_is_identity(self) -> None:
        """At UF orientation realign_mask returns the mask unchanged."""
        display = self.make_display()
        self.assertEqual(display.realign_mask(OLL_MASK), OLL_MASK)
        self.assertEqual(display.realign_mask(PLL_MASK), PLL_MASK)

    def test_y_rotation_leaves_oll_mask_unchanged(self) -> None:
        """y-rotation keeps U-face positions intact in OLL_MASK."""
        # OLL_MASK covers the whole U face; a y only cycles the U
        # layer around the vertical axis, leaving all U facelets in place.
        display = self.make_display('y')
        self.assertEqual(display.realign_mask(OLL_MASK), OLL_MASK)

    def test_z2_shifts_u_positions_to_d_face(self) -> None:
        """After z2 the user-POV U positions map to internal D-face slots."""
        # z2 puts the physical D face on top.  The realigned mask must mark
        # internal D-face positions (27-35 in URFDLB order) instead of U.
        display = self.make_display('z2')
        expected = '000000000000000222000000222111111111000000222000000222'
        self.assertEqual(display.realign_mask(OLL_MASK), expected)

    def test_x_shifts_u_positions_to_f_face(self) -> None:
        """After x rotation POV-U positions map to internal F-face slots."""
        display = self.make_display('x')
        expected = '000000222200200200111111111222000000002002002000000000'
        self.assertEqual(display.realign_mask(OLL_MASK), expected)

    def test_all_ones_mask_is_invariant(self) -> None:
        """A fully-set mask is unchanged by any rotation."""
        all_ones = '1' * 54
        display = self.make_display('z2')
        self.assertEqual(display.realign_mask(all_ones), all_ones)

    def test_all_zeros_mask_is_invariant(self) -> None:
        """An all-zero mask is unchanged by any rotation."""
        all_zeros = '0' * 54
        display = self.make_display('x')
        self.assertEqual(display.realign_mask(all_zeros), all_zeros)


class ScaleMaskTestCase(ModeDisplayMixin, unittest.TestCase):
    """Tests for ModeDisplay.scale_mask()."""

    # ------------------------------------------------------------------
    # Identity: 3 → 3
    # ------------------------------------------------------------------

    def test_identity_all_ones(self) -> None:
        """Scaling a full mask from 3 to 3 returns it unchanged."""
        display = self.make_display()
        mask = '1' * 54
        self.assertEqual(display.scale_mask(mask, 3), mask)

    def test_identity_all_zeros(self) -> None:
        """Scaling an empty mask from 3 to 3 returns it unchanged."""
        display = self.make_display()
        mask = '0' * 54
        self.assertEqual(display.scale_mask(mask, 3), mask)

    def test_identity_oll_mask(self) -> None:
        """Scaling OLL_MASK from 3 to 3 returns it unchanged."""
        display = self.make_display()
        self.assertEqual(display.scale_mask(OLL_MASK, 3), OLL_MASK)

    # ------------------------------------------------------------------
    # Downscale: 3 → 2 (only corners survive, edges and centers dropped)
    # ------------------------------------------------------------------

    def test_downscale_all_ones(self) -> None:
        """All-ones mask scaled to 2x2 gives all-ones (6x4=24)."""
        display = self.make_display()
        mask = '1' * 54
        self.assertEqual(display.scale_mask(mask, 2), '1' * 24)

    def test_downscale_all_zeros(self) -> None:
        """All-zeros mask scaled to 2x2 gives all-zeros (6x4=24)."""
        display = self.make_display()
        mask = '0' * 54
        self.assertEqual(display.scale_mask(mask, 2), '0' * 24)

    def test_downscale_oll_mask(self) -> None:
        """OLL_MASK scaled to 2x2."""
        display = self.make_display()
        expected = '111122002200000022002200'
        self.assertEqual(display.scale_mask(OLL_MASK, 2), expected)

    def test_downscale_corners_only(self) -> None:
        """A mask with only corners set keeps them after downscale."""
        display = self.make_display()
        # Build a mask where each face has only corners set: 101 000 101
        face_corners = '101000101'
        mask = face_corners * 6
        self.assertEqual(display.scale_mask(mask, 2), '1111' * 6)

    def test_downscale_edges_only_disappear(self) -> None:
        """A mask with only edges set loses everything at size 2."""
        display = self.make_display()
        # Each face has only edges set: 010 101 010
        face_edges = '010101010'
        mask = face_edges * 6
        self.assertEqual(display.scale_mask(mask, 2), '0000' * 6)

    def test_downscale_center_only_disappear(self) -> None:
        """A mask with only centers set loses everything at size 2."""
        display = self.make_display()
        face_center = '000010000'
        mask = face_center * 6
        self.assertEqual(display.scale_mask(mask, 2), '0000' * 6)

    # ------------------------------------------------------------------
    # Upscale: 3 → 4
    # ------------------------------------------------------------------

    def test_upscale_4_all_ones(self) -> None:
        """All-ones mask scaled to 4x4 gives all-ones (6x16=96)."""
        display = self.make_display()
        mask = '1' * 54
        self.assertEqual(display.scale_mask(mask, 4), '1' * 96)

    def test_upscale_4_all_zeros(self) -> None:
        """All-zeros mask scaled to 4x4 gives all-zeros (6x16=96)."""
        display = self.make_display()
        mask = '0' * 54
        self.assertEqual(display.scale_mask(mask, 4), '0' * 96)

    def test_upscale_4_corners_only(self) -> None:
        """Corners-only mask scaled to 4x4 has corners set."""
        display = self.make_display()
        face_corners = '101000101'
        mask = face_corners * 6
        # 4x4 face: corners at (0,0),(0,3),(3,0),(3,3)
        # Row 0: 1 0 0 1
        # Row 1: 0 0 0 0
        # Row 2: 0 0 0 0
        # Row 3: 1 0 0 1
        face_4 = (
            '1001'
            '0000'
            '0000'
            '1001'
        )
        self.assertEqual(display.scale_mask(mask, 4), face_4 * 6)

    def test_upscale_4_edges_only(self) -> None:
        """Edges-only mask scaled to 4x4 has border non-corner positions set."""
        display = self.make_display()
        face_edges = '010101010'
        mask = face_edges * 6
        # 4x4 face: edges are border non-corner positions
        # Row 0: 0 1 1 0  (top edge positions)
        # Row 1: 1 0 0 1  (left and right edges)
        # Row 2: 1 0 0 1  (left and right edges)
        # Row 3: 0 1 1 0  (bottom edge positions)
        face_4 = (
            '0110'
            '1001'
            '1001'
            '0110'
        )
        self.assertEqual(display.scale_mask(mask, 4), face_4 * 6)

    def test_upscale_4_center_only(self) -> None:
        """Center-only mask scaled to 4x4 has interior positions set."""
        display = self.make_display()
        face_center = '000010000'
        mask = face_center * 6
        # 4x4 face: interior is (1..2, 1..2)
        # Row 0: 0 0 0 0
        # Row 1: 0 1 1 0
        # Row 2: 0 1 1 0
        # Row 3: 0 0 0 0
        face_4 = (
            '0000'
            '0110'
            '0110'
            '0000'
        )
        self.assertEqual(display.scale_mask(mask, 4), face_4 * 6)

    # ------------------------------------------------------------------
    # Upscale: 3 → 5
    # ------------------------------------------------------------------

    def test_upscale_5_all_ones(self) -> None:
        """All-ones mask scaled to 5x5 gives all-ones (6x25=150)."""
        display = self.make_display()
        mask = '1' * 54
        self.assertEqual(display.scale_mask(mask, 5), '1' * 150)

    def test_upscale_5_corners_only(self) -> None:
        """Corners-only mask scaled to 5x5 has 4 corner positions per face."""
        display = self.make_display()
        face_corners = '101000101'
        mask = face_corners * 6
        # 5x5 face:
        # Row 0: 1 0 0 0 1
        # Row 1: 0 0 0 0 0
        # Row 2: 0 0 0 0 0
        # Row 3: 0 0 0 0 0
        # Row 4: 1 0 0 0 1
        face_5 = (
            '10001'
            '00000'
            '00000'
            '00000'
            '10001'
        )
        self.assertEqual(display.scale_mask(mask, 5), face_5 * 6)

    def test_upscale_5_edges_only(self) -> None:
        """Edges-only mask scaled to 5x5 has border non-corner positions set."""
        display = self.make_display()
        face_edges = '010101010'
        mask = face_edges * 6
        # 5x5 face:
        # Row 0: 0 1 1 1 0  (top edge: 3 positions)
        # Row 1: 1 0 0 0 1  (left and right edges)
        # Row 2: 1 0 0 0 1
        # Row 3: 1 0 0 0 1
        # Row 4: 0 1 1 1 0  (bottom edge: 3 positions)
        face_5 = (
            '01110'
            '10001'
            '10001'
            '10001'
            '01110'
        )
        self.assertEqual(display.scale_mask(mask, 5), face_5 * 6)

    def test_upscale_5_center_only(self) -> None:
        """Center-only mask scaled to 5x5 has all interior positions set."""
        display = self.make_display()
        face_center = '000010000'
        mask = face_center * 6
        # 5x5 face: interior is (1..3, 1..3) = 3x3 = 9 positions
        # Row 0: 0 0 0 0 0
        # Row 1: 0 1 1 1 0
        # Row 2: 0 1 1 1 0
        # Row 3: 0 1 1 1 0
        # Row 4: 0 0 0 0 0
        face_5 = (
            '00000'
            '01110'
            '01110'
            '01110'
            '00000'
        )
        self.assertEqual(display.scale_mask(mask, 5), face_5 * 6)

    # ------------------------------------------------------------------
    # Mixed masks: per-face different corner/edge/center values
    # ------------------------------------------------------------------

    def test_upscale_4_pll_mask(self) -> None:
        """PLL_MASK scaled to 4x4 preserves per-face structure."""
        display = self.make_display()
        # PLL_MASK: U='000000000' R='111000000' F='111000000'
        #           D='000000000' L='111000000' B='111000000'
        # U face all zeros → 4x4 all zeros
        u_4 = '0' * 16
        # R face '111000000': corners(0,2,6,8)=1,1,0,0
        #   edges(1,3,5,7)=1,0,0,0  center(4)=0
        # 4x4:
        # Row 0: 1 1 1 1  (TL=1, T-edge=1, TR=1)
        # Row 1: 0 0 0 0  (L-edge=0, center=0, R-edge=0)
        # Row 2: 0 0 0 0
        # Row 3: 0 0 0 0  (BL=0, B-edge=0, BR=0)
        r_4 = (
            '1111'
            '0000'
            '0000'
            '0000'
        )
        f_4 = r_4  # same pattern
        d_4 = '0' * 16
        l_4 = r_4
        b_4 = r_4
        expected = u_4 + r_4 + f_4 + d_4 + l_4 + b_4
        self.assertEqual(display.scale_mask(PLL_MASK, 4), expected)

    def test_upscale_mixed_face(self) -> None:
        """A face with different corner values scales correctly."""
        display = self.make_display()
        # Custom mask: first face has TL=1, TR=0, BL=0, BR=1
        # edges all 0, center 0
        # 3x3: 100 000 001
        face_3 = '100000001'
        mask = face_3 + '0' * 45  # only first face has data
        # 4x4:
        # Row 0: 1 0 0 0  (TL=1, T-edge=0, TR=0)
        # Row 1: 0 0 0 0  (L-edge=0, center=0, R-edge=0)
        # Row 2: 0 0 0 0
        # Row 3: 0 0 0 1  (BL=0, B-edge=0, BR=1)
        face_4 = (
            '1000'
            '0000'
            '0000'
            '0001'
        )
        expected = face_4 + '0' * 80
        self.assertEqual(display.scale_mask(mask, 4), expected)


class ResolveModeTestCase(ModeDisplayMixin, unittest.TestCase):
    """Tests for ModeDisplay.resolve_mode()."""

    def test_unknown_mode_returns_empty_triple(self) -> None:
        """Unrecognised mode string returns three empty strings."""
        display = self.make_display()
        self.assertEqual(display.resolve_mode('unknown'), ('', '', ''))

    def test_empty_mode_returns_empty_triple(self) -> None:
        """Empty mode string returns three empty strings."""
        display = self.make_display()
        self.assertEqual(display.resolve_mode(''), ('', '', ''))

    def test_oll_layout_mask_and_no_orientation(self) -> None:
        """OLL mode yields 'top' layout, realigned mask, empty orientation."""
        display = self.make_display()
        mask, layout, orientation = display.resolve_mode('oll')
        self.assertEqual(layout, 'top')
        self.assertEqual(orientation, '')
        self.assertEqual(mask, OLL_MASK)  # identity at default UF

    def test_pll_layout_mask_and_no_orientation(self) -> None:
        """PLL mode yields 'top' layout, realigned mask, empty orientation."""
        display = self.make_display()
        mask, layout, orientation = display.resolve_mode('pll')
        self.assertEqual(layout, 'top')
        self.assertEqual(orientation, '')
        self.assertEqual(mask, PLL_MASK)

    def test_cross_calls_orientation_callback(self) -> None:
        """Cross mode calls cross_bottom_orientation and returns its value."""
        # After F move cross_bottom_orientation() returns 'UL'.
        display = self.make_display('F')
        _, layout, orientation = display.resolve_mode('cross')
        self.assertEqual(layout, '')
        self.assertEqual(orientation, 'UL')

    def test_cross_top_calls_orientation_callback(self) -> None:
        """cross-top mode calls cross_top_orientation and returns its value."""
        display = self.make_display('F')
        _, layout, orientation = display.resolve_mode('cross-top')
        self.assertEqual(layout, '')
        self.assertEqual(orientation, 'UR')

    def test_f2l_calls_orientation_callback(self) -> None:
        """f2l mode calls f2l_orientation and returns its value."""
        display = self.make_display()
        _, layout, orientation = display.resolve_mode('f2l')
        self.assertEqual(layout, '')
        self.assertEqual(orientation, '')  # solved

    def test_cross_and_cross_bottom_are_aliases(self) -> None:
        """'cross' and 'cross-bottom' produce identical results."""
        display = self.make_display()
        self.assertEqual(
            display.resolve_mode('cross'),
            display.resolve_mode('cross-bottom'),
        )

    def test_mask_differs_after_orientation_change(self) -> None:
        """Mask returned reflects the cube's current orientation."""
        mask_uf, _, _ = self.make_display().resolve_mode('oll')
        mask_z2, _, _ = self.make_display('z2').resolve_mode('oll')
        self.assertNotEqual(mask_uf, mask_z2)

    def test_non_3x3_returns_mask(self) -> None:
        """On a non-3x3 cube every mode returns a mask."""
        display = VCubeDisplay(VCube(size=4))
        for mode in ('oll', 'pll', 'll', 'cross', 'f2l'):
            with self.subTest(mode=mode):
                mask, _, _ = display.resolve_mode(mode)
                self.assertNotEqual(mask, '')

    def test_non_3x3_preserves_layout(self) -> None:
        """On a non-3x3 cube the layout from the mode config is returned."""
        display = VCubeDisplay(VCube(size=4))
        _, layout, _ = display.resolve_mode('oll')
        self.assertEqual(layout, 'top')
