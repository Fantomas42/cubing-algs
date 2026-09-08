"""Tests for the readings the constants of the backend are written with."""
import unittest

from cubing_algs.display.gl.constants import CORE_COLOR
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import HELP_MOUSE
from cubing_algs.display.gl.constants import HELP_MOVE
from cubing_algs.display.gl.constants import HELP_WINDOW
from cubing_algs.display.gl.constants import VIEWER_HELP
from cubing_algs.display.gl.constants import VIEWER_SHORTCUTS
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.constants import HelpEntry
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.constants import blended
from cubing_algs.display.gl.constants import clamp
from cubing_algs.display.gl.constants import help_block
from cubing_algs.display.gl.constants import lerp
from cubing_algs.display.gl.constants import viewer_entries
from cubing_algs.display.gl.constants import viewer_help

PLACES = 9


class TestClamp(unittest.TestCase):
    """Tests for holding a value between two bounds."""

    def test_a_value_inside_the_bounds_is_handed_back(self) -> None:
        """Test that nothing happens to a value that needs nothing."""
        self.assertAlmostEqual(clamp(0.4), 0.4, places=PLACES)

    def test_the_unit_interval_is_the_default(self) -> None:
        """Test that a share is what a clamp is asked about by default."""
        self.assertAlmostEqual(clamp(-3.0), 0.0, places=PLACES)
        self.assertAlmostEqual(clamp(12.0), 1.0, places=PLACES)

    def test_the_bounds_are_arguments(self) -> None:
        """Test that a clamp holds whatever it is asked to hold."""
        self.assertAlmostEqual(clamp(12.0, 1.0, 4.0), 4.0, places=PLACES)


class TestLerp(unittest.TestCase):
    """Tests for reading a value part of the way to another."""

    def test_both_ends_are_reached_exactly(self) -> None:
        """Test that no rounding stands between a share and its end."""
        self.assertAlmostEqual(lerp(2.0, 6.0, 0.0), 2.0, places=PLACES)
        self.assertAlmostEqual(lerp(2.0, 6.0, 1.0), 6.0, places=PLACES)

    def test_the_middle_is_the_middle(self) -> None:
        """Test that half of the way is half of the distance."""
        self.assertAlmostEqual(lerp(2.0, 6.0, 0.5), 4.0, places=PLACES)

    def test_a_share_is_taken_as_it_comes(self) -> None:
        """Test that nothing is clamped, a caller knowing where it is."""
        self.assertAlmostEqual(lerp(0.0, 1.0, 2.0), 2.0, places=PLACES)


class TestBlended(unittest.TestCase):
    """Tests for mixing one term of a look with the same one of another."""

    def test_a_number_is_mixed(self) -> None:
        """Test that a quantity of light travels."""
        self.assertAlmostEqual(blended(0.0, 1.0, 0.25), 0.25, places=PLACES)

    def test_a_color_is_mixed_channel_by_channel(self) -> None:
        """Test that three channels are a place walked towards."""
        self.assertEqual(
            blended((0.0, 0.0, 0.0), (1.0, 2.0, 4.0), 0.5),
            (0.5, 1.0, 2.0),
        )

    def test_an_integer_is_not_a_term_to_be_mixed(self) -> None:
        """Test that a sample count stays the one of the look being left."""
        self.assertEqual(blended(8, 1, 0.5), 8)

    def test_two_terms_of_different_shapes_keep_the_first(self) -> None:
        """Test that nothing is invented out of two things that disagree."""
        self.assertEqual(blended((0.0, 0.0, 0.0), 1.0, 0.5), (0.0, 0.0, 0.0))


class TestLookBlended(unittest.TestCase):
    """Tests for reading a whole look part of the way towards another."""

    def setUp(self) -> None:
        """Take a look far from the default one to travel towards."""
        self.other = Look(
            core_color=(0.0, 0.0, 0.0),
            core_metalness=1.0,
            ambient=0.0,
            light_direction=(1.0, 1.0, 1.0),
            samples=1,
        )

    def test_no_share_hands_the_very_look_back(self) -> None:
        """Test that a look not moving costs nothing, identity included."""
        self.assertIs(DEFAULT_LOOK.blended(self.other, 0.0), DEFAULT_LOOK)

    def test_the_whole_way_lands_on_the_other_look(self) -> None:
        """Test that every term of light reaches the one it travels to."""
        landed = DEFAULT_LOOK.blended(self.other, 1.0)

        self.assertAlmostEqual(landed.ambient, 0.0, places=PLACES)
        self.assertAlmostEqual(landed.core_metalness, 1.0, places=PLACES)
        self.assertEqual(landed.core_color, (0.0, 0.0, 0.0))

    def test_a_color_travels_channel_by_channel(self) -> None:
        """Test that a core is mixed as the color it is."""
        mixed = DEFAULT_LOOK.blended(self.other, 0.5)

        for channel, value in zip(mixed.core_color, CORE_COLOR, strict=True):
            self.assertAlmostEqual(channel, value / 2.0, places=PLACES)

    def test_the_sample_count_is_not_a_light_and_stays(self) -> None:
        """Test that an integer is kept whatever the share says."""
        mixed = DEFAULT_LOOK.blended(self.other, 0.5)

        self.assertEqual(mixed.samples, DEFAULT_LOOK.samples)

    def test_a_term_added_tomorrow_needs_nothing_written_here(self) -> None:
        """Test that every float field of a look is mixed, none named."""
        mixed = DEFAULT_LOOK.blended(self.other, 0.5)

        for name in ('ambient', 'gamma', 'rim_strength', 'specular_power',
                     'core_rim_power', 'groove_falloff', 'sticker_grain'):
            with self.subTest(term=name):
                self.assertAlmostEqual(
                    getattr(mixed, name),
                    lerp(
                        getattr(DEFAULT_LOOK, name),
                        getattr(self.other, name),
                        0.5,
                    ),
                    places=PLACES,
                )


class TestViewerShortcuts(unittest.TestCase):
    """Tests for the one place the shortcuts of a window are written."""

    def test_every_shortcut_belongs_to_a_known_group(self) -> None:
        """Test that nothing is filed under a group nobody can ask for."""
        groups = {HELP_MOUSE, HELP_MOVE, HELP_WINDOW}

        for entry in VIEWER_SHORTCUTS:
            with self.subTest(keys=entry.keys):
                self.assertIn(entry.group, groups)

    def test_no_group_asked_for_is_every_group(self) -> None:
        """Test that a list of nothing in particular is the whole list."""
        self.assertEqual(viewer_entries(), VIEWER_SHORTCUTS)

    def test_a_group_keeps_the_order_it_is_declared_in(self) -> None:
        """Test that filtering never reshuffles what is read top down."""
        kept = viewer_entries(HELP_MOUSE, HELP_WINDOW)

        self.assertEqual(
            list(kept),
            [entry for entry in VIEWER_SHORTCUTS if entry.group != HELP_MOVE],
        )

    def test_the_mouse_is_a_group_of_its_own(self) -> None:
        """Test that the gestures are reachable without the keys."""
        self.assertEqual(
            [entry.keys for entry in viewer_entries(HELP_MOUSE)],
            ['Drag', 'Ctrl Drag', 'Wheel'],
        )


class TestViewerHelpBlock(unittest.TestCase):
    """Tests for writing a list of shortcuts out."""

    def test_the_heading_opens_the_block(self) -> None:
        """Test that a window says what it is before what it answers."""
        block = help_block('a window', (HelpEntry('X', 'do something'),))

        self.assertEqual(block.splitlines()[0], 'a window')

    def test_a_description_starts_on_the_same_column_for_all(self) -> None:
        """Test that the keys are padded rather than laid out by hand."""
        block = help_block(
            'a window',
            (HelpEntry('X', 'first'), HelpEntry('Ctrl Drag', 'second')),
        )

        self.assertEqual(
            [line.index(word) for line, word in zip(
                block.splitlines()[1:], ('first', 'second'), strict=True,
            )],
            [19, 19],
        )

    def test_the_viewer_help_is_the_whole_list_under_its_name(self) -> None:
        """Test that the constant is what the builder writes."""
        self.assertEqual(
            VIEWER_HELP,
            help_block(f'{ WINDOW_TITLE } viewer', VIEWER_SHORTCUTS),
        )

    def test_a_window_turning_nothing_offers_no_move(self) -> None:
        """Test that a list describes the window it is printed by."""
        block = viewer_help('a stream', moves=False)

        for keys in ('R U F L D B', 'M E S', 'Shift', 'Backspace'):
            with self.subTest(keys=keys):
                self.assertIn(keys, VIEWER_HELP)
                self.assertNotIn(keys, block)

    def test_a_window_turning_nothing_keeps_what_it_does_answer(self) -> None:
        """Test that holding the moves back holds nothing else back."""
        block = viewer_help('a stream', moves=False)

        for keys in ('Drag', 'Ctrl Drag', 'Wheel', 'Space', 'Tab', 'Esc, Q'):
            with self.subTest(keys=keys):
                self.assertIn(keys, block)
