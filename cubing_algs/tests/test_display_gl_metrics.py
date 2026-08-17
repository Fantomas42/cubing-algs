"""
Tests for what a frame of the viewer costs, and how it is told.

Everything here is pure: no context, no window, no clock. A monitor is
fed by hand, exactly as a viewer and a host feed it, and what it writes
is compared to the very characters a terminal would show.
"""
import unittest

from cubing_algs.display.gl.constants import DEFAULT_BUDGET
from cubing_algs.display.gl.constants import MONITOR_INTERVAL
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.metrics import Meter
from cubing_algs.display.gl.metrics import Monitor
from cubing_algs.display.gl.metrics import RenderProfile
from cubing_algs.display.gl.metrics import budget_line
from cubing_algs.display.gl.metrics import debug_report
from cubing_algs.display.gl.metrics import debug_title
from cubing_algs.display.gl.metrics import meter_line
from cubing_algs.display.gl.metrics import milliseconds
from cubing_algs.display.gl.metrics import scene_line
from cubing_algs.display.gl.metrics import target_line

# A tenth of a second per frame, which makes every duration of these
# tests readable in milliseconds without a single rounding.
BEAT = 0.1


def filled(meter: Meter, *values: float) -> Meter:
    """
    Feed a meter with the samples of a test.

    Args:
        meter: The meter to fill.
        values: The samples to record, in seconds.

    Returns:
        The meter, filled.

    """
    for value in values:
        meter.add(value)

    return meter


class TestMilliseconds(unittest.TestCase):
    """Tests for the milliseconds function."""

    def test_a_duration_is_written_in_milliseconds(self) -> None:
        """Test that seconds come out as milliseconds."""
        self.assertEqual(milliseconds(0.0182), '18.20')

    def test_a_duration_keeps_two_decimals(self) -> None:
        """Test that a fraction of a millisecond still shows."""
        self.assertEqual(milliseconds(0.000_412), '0.41')


class TestMeter(unittest.TestCase):
    """Tests for the sliding window of samples."""

    def test_an_empty_window_answers_zero(self) -> None:
        """Test that nothing measured is worth nothing, never a crash."""
        meter = Meter()

        self.assertEqual(meter.count, 0)
        self.assertEqual(meter.total, 0.0)
        self.assertEqual(meter.mean, 0.0)
        self.assertEqual(meter.minimum, 0.0)
        self.assertEqual(meter.maximum, 0.0)
        self.assertEqual(meter.percentile(), 0.0)

    def test_a_single_sample_is_every_statistic(self) -> None:
        """Test that one sample answers for the whole window."""
        meter = filled(Meter(), 0.02)

        self.assertEqual(meter.count, 1)
        self.assertEqual(meter.mean, 0.02)
        self.assertEqual(meter.minimum, 0.02)
        self.assertEqual(meter.maximum, 0.02)
        self.assertEqual(meter.percentile(), 0.02)

    def test_statistics_are_read_on_every_sample(self) -> None:
        """Test that the window is summarized as a whole."""
        meter = filled(Meter(), 0.01, 0.03, 0.02)

        self.assertAlmostEqual(meter.total, 0.06)
        self.assertAlmostEqual(meter.mean, 0.02)
        self.assertEqual(meter.minimum, 0.01)
        self.assertEqual(meter.maximum, 0.03)

    def test_the_window_forgets_its_oldest_sample(self) -> None:
        """Test that a bounded window slides rather than grows."""
        meter = filled(Meter(window=3), 0.01, 0.02, 0.03, 0.04)

        self.assertEqual(meter.count, 3)
        self.assertEqual(meter.minimum, 0.02)

    def test_a_percentile_reads_the_ordered_window(self) -> None:
        """Test that a share is read on the sorted samples."""
        meter = filled(Meter(), *(value / 100 for value in range(1, 101)))

        self.assertAlmostEqual(meter.percentile(), 0.95)
        self.assertAlmostEqual(meter.percentile(0.0), 0.01)
        self.assertAlmostEqual(meter.percentile(1.0), 1.0)

    def test_a_stutter_shows_in_the_percentile(self) -> None:
        """Test that the reading catches what an average hides."""
        meter = filled(Meter(), *([0.01] * 94), *([0.5] * 6))

        self.assertAlmostEqual(meter.mean, 0.0394)
        self.assertEqual(meter.percentile(), 0.5)

    def test_a_window_can_be_emptied(self) -> None:
        """Test that a cleared meter has measured nothing."""
        meter = filled(Meter(), 0.01, 0.02)

        meter.clear()

        self.assertEqual(meter.count, 0)


class TestMonitor(unittest.TestCase):
    """Tests for what a monitor counts across the meters it holds."""

    def test_a_monitor_starts_on_the_default_budget(self) -> None:
        """Test that a frame is given a sixtieth of a second by default."""
        self.assertEqual(Monitor().budget, DEFAULT_BUDGET)

    def test_every_meter_shares_the_window(self) -> None:
        """Test that the five meters slide over the same length."""
        monitor = Monitor(window=12)

        for meter in (
                monitor.frame, monitor.advance,
                monitor.draw, monitor.swap, monitor.gpu,
        ):
            self.assertEqual(meter.window, 12)

    def test_a_counted_frame_reaches_the_frame_meter(self) -> None:
        """Test that counting a frame records how long it took."""
        monitor = Monitor()

        monitor.count_frame(0.02)

        self.assertEqual(monitor.frames, 1)
        self.assertEqual(monitor.frame.mean, 0.02)

    def test_restarting_forgets_the_frames_of_the_period(self) -> None:
        """Test that a new period counts from where it starts."""
        monitor = Monitor()
        monitor.count_frame(0.02)

        monitor.restart(12.0)

        self.assertEqual(monitor.frames, 0)
        self.assertEqual(monitor.period, 12.0)

    def test_restarting_keeps_the_sliding_window(self) -> None:
        """Test that a period of counting is not a window of samples."""
        monitor = Monitor()
        monitor.count_frame(0.02)

        monitor.restart(12.0)

        self.assertEqual(monitor.frame.count, 1)

    def test_a_period_is_due_once_the_interval_is_over(self) -> None:
        """Test that a rate is held until the interval has gone by."""
        monitor = Monitor()
        monitor.restart(10.0)

        self.assertFalse(monitor.due(10.0 + MONITOR_INTERVAL / 2))
        self.assertTrue(monitor.due(10.0 + MONITOR_INTERVAL))

    def test_the_rate_is_the_average_of_the_period(self) -> None:
        """Test that the rate is counted over the whole period."""
        monitor = Monitor()
        monitor.restart(0.0)

        for _ in range(120):
            monitor.count_frame(BEAT)

        self.assertEqual(monitor.rate(2.0), 60.0)

    def test_a_period_of_no_time_holds_no_rate(self) -> None:
        """Test that a rate is never divided by nothing."""
        monitor = Monitor()
        monitor.restart(10.0)
        monitor.count_frame(BEAT)

        self.assertEqual(monitor.rate(10.0), 0.0)

    def test_a_frame_far_past_the_pace_is_dropped(self) -> None:
        """Test that only the frames well over the pace held are counted."""
        monitor = Monitor(budget=0.01)

        for value in (0.008, 0.011, 0.014, 0.02, 0.4):
            monitor.count_frame(value)

        self.assertEqual(monitor.drops, 1)

    def test_the_pace_is_the_interval_the_frames_hold(self) -> None:
        """Test that the pace is read in the middle of the window."""
        monitor = Monitor()

        for value in (0.008, 0.011, 0.014, 0.02, 0.4):
            monitor.count_frame(value)

        self.assertEqual(monitor.pace, 0.014)

    def test_an_empty_window_holds_no_pace(self) -> None:
        """Test that a monitor asked before a frame answers with nothing."""
        monitor = Monitor()

        self.assertEqual(monitor.pace, 0.0)
        self.assertEqual(monitor.drops, 0)

    def test_a_steady_pace_drops_nothing_under_any_budget(self) -> None:
        """
        Test that frames held at a regular interval are never dropped.

        The regression this holds: a window vsynced at sixty hertz on a
        screen announcing a hundred spent every frame past its budget,
        and the whole window read as dropped though not one frame was.
        A pace slower than the budget is a headroom question, which
        ``headroom`` answers on the work; a drop is a stutter.
        """
        monitor = Monitor(budget=0.01)

        for _ in range(60):
            monitor.count_frame(1 / 60)

        self.assertEqual(monitor.drops, 0)

    def test_a_doubled_frame_is_a_dropped_one(self) -> None:
        """Test that a frame missing its refresh stands out of the pace."""
        monitor = Monitor(budget=0.01)

        for _ in range(60):
            monitor.count_frame(1 / 60)

        monitor.count_frame(2 / 60)

        self.assertEqual(monitor.drops, 1)

    def test_the_processor_holds_the_two_halves_of_a_frame(self) -> None:
        """Test that the CPU time is what advancing and drawing cost."""
        monitor = Monitor()
        filled(monitor.advance, 0.001, 0.003)
        filled(monitor.draw, 0.004)

        self.assertAlmostEqual(monitor.cpu, 0.006)

    def test_the_headroom_is_what_the_budget_has_left(self) -> None:
        """Test that the free share of a frame is measured on the work."""
        monitor = Monitor(budget=0.01)
        filled(monitor.advance, 0.001)
        filled(monitor.draw, 0.001)

        self.assertAlmostEqual(monitor.headroom, 0.8)

    def test_work_past_the_budget_leaves_no_headroom(self) -> None:
        """Test that an overrun reads as no room at all, never as less."""
        monitor = Monitor(budget=0.01)
        filled(monitor.draw, 0.05)

        self.assertEqual(monitor.headroom, 0.0)

    def test_a_null_budget_leaves_no_headroom(self) -> None:
        """Test that a frame given no time is never divided by it."""
        monitor = Monitor(budget=0.0)
        filled(monitor.draw, 0.001)

        self.assertEqual(monitor.headroom, 0.0)


class TestReportLines(unittest.TestCase):
    """Tests for the lines a report is made of."""

    def test_a_meter_line_holds_the_whole_window(self) -> None:
        """Test that a line carries the average and its extremes."""
        meter = filled(Meter(), 0.01, 0.02, 0.03)

        self.assertEqual(
            meter_line('draw', meter),
            '  draw       20.00 ms   min  10.00   p95  30.00   max  30.00',
        )

    def test_a_meter_nothing_fed_says_so(self) -> None:
        """Test that an empty meter never shows a made up zero."""
        self.assertEqual(
            meter_line('gpu', Meter()),
            '  gpu       not measured',
        )

    def test_a_note_closes_the_line(self) -> None:
        """Test that a line carries what the caller adds to it."""
        self.assertEqual(
            meter_line('swap', Meter(), '   vsync on'),
            '  swap      not measured   vsync on',
        )

    def test_the_budget_line_names_the_screen(self) -> None:
        """Test that the refresh rate of the screen is said plainly."""
        monitor = Monitor(budget=0.01)
        filled(monitor.draw, 0.002)

        self.assertEqual(
            budget_line(monitor, RenderProfile(refresh=100.0)),
            '  headroom  80%   budget 10.00 ms (100 Hz screen)',
        )

    def test_the_budget_line_without_a_screen(self) -> None:
        """Test that an unknown refresh rate is left out of the line."""
        self.assertEqual(
            budget_line(Monitor(budget=0.01), RenderProfile()),
            '  headroom  100%   budget 10.00 ms',
        )

    def test_the_scene_line_counts_what_is_drawn(self) -> None:
        """Test that the line says the instances and what they weigh."""
        self.assertEqual(
            scene_line(
                RenderProfile(
                    instances=26, triangles=1456, instance_bytes=2560,
                ),
            ),
            '  scene     26 instances, 1456 triangles, 2.5 KiB',
        )

    def test_the_target_line_says_where_it_is_drawn(self) -> None:
        """Test that the line says the size, the samples and the calls."""
        self.assertEqual(
            target_line(
                RenderProfile(size=(720, 720), samples=8, draw_calls=3),
            ),
            '  target    720x720, 8 samples, 3 draw calls',
        )


def windowed_monitor() -> Monitor:
    """
    Build a monitor holding a plain second of frames.

    Returns:
        A monitor of sixty frames, each one inside its budget.

    """
    monitor = Monitor(budget=0.01)
    monitor.restart(0.0)

    for _ in range(60):
        monitor.count_frame(0.01)

    filled(monitor.advance, 0.0005)
    filled(monitor.draw, 0.0013)
    filled(monitor.gpu, 0.0007)

    return monitor


class TestDebugTitle(unittest.TestCase):
    """Tests for what a window shows of its own performance."""

    def test_the_title_carries_the_four_numbers(self) -> None:
        """Test that a rate never travels alone in the title."""
        self.assertEqual(
            debug_title(windowed_monitor(), 1.0),
            f'{ WINDOW_TITLE } - 60 fps | cpu 1.80 | gpu 0.70 ms | 0 dropped',
        )

    def test_the_title_is_kept_ahead(self) -> None:
        """Test that the window keeps being named after what it shows."""
        self.assertTrue(
            debug_title(windowed_monitor(), 1.0, 'cube').startswith('cube - '),
        )

    def test_a_gpu_nobody_timed_reads_as_nothing(self) -> None:
        """Test that a title holds even before the GPU is asked."""
        monitor = Monitor()
        monitor.restart(0.0)
        monitor.count_frame(0.01)

        self.assertEqual(
            debug_title(monitor, 1.0),
            f'{ WINDOW_TITLE } - 1 fps | cpu 0.00 | gpu 0.00 ms | 0 dropped',
        )

    def test_dropped_frames_are_said_in_the_title(self) -> None:
        """Test that a stutter is named where it is seen."""
        monitor = windowed_monitor()
        monitor.count_frame(0.5)

        self.assertTrue(debug_title(monitor, 1.0).endswith('| 1 dropped'))

    def test_a_free_running_window_says_so(self) -> None:
        """Test that a rate without a vsync is never taken for one."""
        self.assertTrue(
            debug_title(
                windowed_monitor(), 1.0, vsync=False,
            ).endswith('| vsync off'),
        )


class TestDebugReport(unittest.TestCase):
    """Tests for the block a report writes to a terminal."""

    def setUp(self) -> None:
        """Build a monitor and a profile of a plain windowed frame."""
        self.monitor = Monitor(budget=0.01)
        self.monitor.restart(0.0)

        for _ in range(3):
            self.monitor.count_frame(0.01)

        filled(self.monitor.advance, 0.0004)
        filled(self.monitor.draw, 0.0013)
        filled(self.monitor.swap, 0.008)
        filled(self.monitor.gpu, 0.0007)

        self.profile = RenderProfile(
            instances=26,
            triangles=1456,
            instance_bytes=2560,
            size=(720, 720),
            samples=8,
            draw_calls=2,
            context='Mesa Intel - 4.6',
            refresh=100.0,
        )

    def test_the_report_holds_every_meter(self) -> None:
        """Test that the block says the whole of what a frame costs."""
        self.assertEqual(
            debug_report(self.monitor, self.profile),
            '\n'.join((
                f'{ WINDOW_TITLE } debug - 3 frames over 0.0 s, 0 dropped',
                (
                    '  frame      10.00 ms   min  10.00'
                    '   p95  10.00   max  10.00'
                ),
                (
                    '  advance     0.40 ms   min   0.40'
                    '   p95   0.40   max   0.40'
                ),
                (
                    '  draw        1.30 ms   min   1.30'
                    '   p95   1.30   max   1.30'
                ),
                (
                    '  swap        8.00 ms   min   8.00'
                    '   p95   8.00   max   8.00   vsync on'
                ),
                (
                    '  gpu         0.70 ms   min   0.70'
                    '   p95   0.70   max   0.70'
                ),
                '  headroom  83%   budget 10.00 ms (100 Hz screen)',
                '  scene     26 instances, 1456 triangles, 2.5 KiB',
                '  target    720x720, 8 samples, 2 draw calls',
                '  context   Mesa Intel - 4.6',
            )),
        )

    def test_the_report_is_named_after_the_window(self) -> None:
        """Test that a report says which window it is about."""
        report = debug_report(self.monitor, self.profile, 'cube')

        self.assertTrue(report.startswith('cube debug - '))

    def test_the_report_says_a_freed_vsync(self) -> None:
        """Test that the swap line tells what it was waiting for."""
        from dataclasses import replace

        report = debug_report(
            self.monitor, replace(self.profile, vsync=False),
        )

        self.assertIn('vsync off', report)
