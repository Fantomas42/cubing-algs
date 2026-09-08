"""Tests for the clock reading how old an arriving move already is."""
import unittest

from cubing_algs.display.gl.clock import MoveClock
from cubing_algs.display.gl.constants import CLOCK_SPAN
from cubing_algs.display.gl.constants import MOVE_LEAD

PLACES = 9


class TestMoveClockLead(unittest.TestCase):
    """Tests for what every move is aged by before anything is measured."""

    def test_a_move_with_no_stamp_is_worth_the_lead(self) -> None:
        """Test that a producer saying nothing of its time gets the lead."""
        clock = MoveClock(lead=0.05)

        self.assertAlmostEqual(clock.age(None, 12.0), 0.05, places=PLACES)

    def test_the_lead_is_the_one_of_the_backend_by_default(self) -> None:
        """Test that a clock nobody argued with carries the stated lead."""
        self.assertAlmostEqual(MoveClock().lead, MOVE_LEAD, places=PLACES)

    def test_the_span_is_the_one_of_the_backend_by_default(self) -> None:
        """Test that the offset is read on the stated number of arrivals."""
        self.assertEqual(MoveClock().delays.maxlen, CLOCK_SPAN)


class TestMoveClockOffset(unittest.TestCase):
    """Tests for the offset two clocks with no common origin are read by."""

    def test_the_first_arrival_is_worth_the_lead_alone(self) -> None:
        """Test that a delay is only ever known against another one."""
        clock = MoveClock(lead=0.0)

        self.assertAlmostEqual(clock.age(1000.0, 5.0), 0.0, places=PLACES)

    def test_a_later_arrival_is_aged_by_what_it_exceeds_the_minimum_by(
            self,
    ) -> None:
        """Test that the jitter of one arrival is what is measured."""
        clock = MoveClock(lead=0.0)

        clock.age(1000.0, 1.1)

        self.assertAlmostEqual(clock.age(2000.0, 2.3), 0.2, places=PLACES)

    def test_a_constant_delay_is_never_seen_at_all(self) -> None:
        """Test that the minimum absorbs whatever the link costs always."""
        clock = MoveClock(lead=0.0)

        for step in range(5):
            age = clock.age(1000.0 * step, 0.08 + step)

        self.assertAlmostEqual(age, 0.0, places=PLACES)

    def test_a_lucky_packet_is_forgotten_past_the_span(self) -> None:
        """Test that the window is what lets an old minimum be dropped."""
        clock = MoveClock(lead=0.0, span=2)

        clock.age(1000.0, 1.0)
        clock.age(2000.0, 2.5)
        clock.age(3000.0, 3.5)

        self.assertAlmostEqual(clock.age(4000.0, 5.5), 1.0, places=PLACES)

    def test_a_reset_forgets_the_producer_that_was_timed(self) -> None:
        """Test that an offset belongs to the connection it was read in."""
        clock = MoveClock(lead=0.0)

        clock.age(1000.0, 1.0)
        clock.reset()

        self.assertAlmostEqual(clock.age(9000.0, 12.0), 0.0, places=PLACES)


class TestMoveClockBurst(unittest.TestCase):
    """Tests for what reading the clock of a producer actually buys."""

    def test_a_burst_is_dated_by_the_producer_and_not_by_the_packet(
            self,
    ) -> None:
        """
        Test that two moves handed over at once are put back apart.

        This is the whole of what reading the clock of the producer
        buys: a bluetooth stack batching a pair gives them one arrival,
        and the older of the two has to be played as the older of the
        two - a hundred and twenty milliseconds apart here, which is
        the gap the gesture made and not the one the radio reports.
        """
        clock = MoveClock(lead=0.0)

        clock.age(1000.0, 10.0)
        clock.age(1120.0, 10.0)

        first = clock.age(2000.0, 11.0)
        second = clock.age(2120.0, 11.0)

        self.assertAlmostEqual(first - second, 0.12, places=PLACES)
        self.assertAlmostEqual(second, 0.0, places=PLACES)

    def test_the_first_burst_is_what_settles_the_offset(self) -> None:
        """
        Test that a move is only known to be old against a younger one.

        The offset is the quickest arrival there has been, so the head
        of the very first burst is read before anything has yet shown
        how quick the link can be, and is handed over younger than it
        is. It is inherent to measuring a delay against a minimum, it
        lasts one burst, and it errs on the side of the producer being
        behind rather than ahead.
        """
        clock = MoveClock(lead=0.0)

        first = clock.age(1000.0, 10.0)
        second = clock.age(1120.0, 10.0)

        self.assertAlmostEqual(first, 0.0, places=PLACES)
        self.assertAlmostEqual(second, 0.0, places=PLACES)


class TestMoveClockCeiling(unittest.TestCase):
    """Tests for how far an age is ever allowed to reach."""

    def test_an_age_is_held_under_the_ceiling(self) -> None:
        """Test that a turn is never started where it ends."""
        clock = MoveClock(lead=0.09, ceiling=0.06)

        self.assertAlmostEqual(clock.age(None, 3.0), 0.06, places=PLACES)

    def test_no_ceiling_holds_nothing_at_all(self) -> None:
        """Test that a null ceiling is the absence of a limit."""
        clock = MoveClock(lead=0.5, ceiling=0.0)

        self.assertAlmostEqual(clock.age(None, 3.0), 0.5, places=PLACES)

    def test_a_clock_read_wrong_costs_a_snap_and_never_a_freeze(self) -> None:
        """Test that a stamp from another origin cannot go past the cap."""
        clock = MoveClock(lead=0.0, ceiling=0.075)

        clock.age(1000.0, 1.0)

        self.assertAlmostEqual(clock.age(0.0, 40.0), 0.075, places=PLACES)
