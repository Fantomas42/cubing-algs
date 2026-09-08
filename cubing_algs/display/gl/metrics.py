"""
What a frame of the viewer costs, and how it is told.

A frame rate says nothing about the rendering when the vsync holds it:
what a window shows then is the refresh rate of the screen, whatever the
cube costs to draw. What does mean something is where the time goes -
building the scene, submitting it, waiting for the swap - how long the
GPU works on it, and how much of the frame budget is left.

Everything here is pure: no context, no window, no clock of its own. A
host measures, hands the seconds over, and prints what these functions
write. The whole module is therefore tested without a GPU, exactly as
the camera and the geometry are.
"""
from collections import deque
from dataclasses import dataclass
from dataclasses import field

from cubing_algs.display.gl.constants import DEFAULT_BUDGET
from cubing_algs.display.gl.constants import DROP_FACTOR
from cubing_algs.display.gl.constants import MILLISECONDS
from cubing_algs.display.gl.constants import MONITOR_INTERVAL
from cubing_algs.display.gl.constants import MONITOR_WINDOW
from cubing_algs.display.gl.constants import WINDOW_TITLE

# Where a percentile is read: the time nineteen frames out of twenty
# stay under, which is what a stutter shows up in and an average hides.
PERCENTILE = 0.95

# Where the interval the frames truly hold is read. The middle of the
# window rather than its average, a single frame doubled by a missed
# refresh being enough to drag a mean off the pace it is measuring.
MEDIAN = 0.5

# What a kibibyte holds.
KIBIBYTE = 1024.0

# Where the name of a line of the report stops and its numbers start.
REPORT_COLUMN = 9


def milliseconds(seconds: float) -> str:
    """
    Write a duration in milliseconds.

    Args:
        seconds: The duration to write, in seconds.

    Returns:
        The duration in milliseconds, with two decimals.

    """
    return f'{ seconds * MILLISECONDS:.2f}'


@dataclass(slots=True)
class Meter:
    """
    A sliding window of samples, and what that window is worth.

    Bounded on purpose: a monitor answers for the last few seconds, not
    for the whole session, so a slowdown shows up while it lasts and is
    forgotten once it is over.
    """

    window: int = MONITOR_WINDOW

    samples: deque[float] = field(init=False)

    def __post_init__(self) -> None:
        """Open the window the samples slide through."""
        self.samples = deque(maxlen=self.window)

    def add(self, value: float) -> None:
        """
        Record one sample, dropping the oldest when the window is full.

        Args:
            value: The duration measured, in seconds.

        """
        self.samples.append(value)

    @property
    def count(self) -> int:
        """
        Tell how many samples the window holds.

        Returns:
            The number of samples, zero when nothing was measured.

        """
        return len(self.samples)

    @property
    def total(self) -> float:
        """
        Tell how long the window covers.

        Returns:
            The sum of the samples, in seconds.

        """
        return sum(self.samples)

    @property
    def mean(self) -> float:
        """
        Tell what a sample of the window is worth on average.

        Returns:
            The average of the samples, zero when there is none.

        """
        if not self.samples:
            return 0.0

        return self.total / len(self.samples)

    @property
    def minimum(self) -> float:
        """
        Tell the shortest sample of the window.

        Returns:
            The smallest sample, zero when there is none.

        """
        return min(self.samples, default=0.0)

    @property
    def maximum(self) -> float:
        """
        Tell the longest sample of the window.

        Returns:
            The largest sample, zero when there is none.

        """
        return max(self.samples, default=0.0)

    def percentile(self, share: float = PERCENTILE) -> float:
        """
        Tell the sample a given share of the window stays under.

        Args:
            share: Where to read the window, from 0 to 1.

        Returns:
            The sample at that share, zero when the window is empty.

        """
        if not self.samples:
            return 0.0

        ordered = sorted(self.samples)

        return ordered[round((len(ordered) - 1) * share)]


@dataclass(slots=True)
class Monitor:
    """
    What a frame costs, over the last few seconds.

    Five meters, fed by whoever is in a position to measure them: the
    viewer times the two halves of its own frame, a host times the swap
    and reads the GPU timer. Nothing here reaches for a clock - a host
    hands the seconds over, which is what keeps the whole thing pure.

    It also holds the period the frame rate is counted over. That period
    is not the sliding window: the rate is counted on frames truly
    drawn since it started, while the meters answer for the last few
    hundred of them.
    """

    budget: float = DEFAULT_BUDGET
    window: int = MONITOR_WINDOW

    frame: Meter = field(init=False)
    advance: Meter = field(init=False)
    draw: Meter = field(init=False)
    swap: Meter = field(init=False)
    gpu: Meter = field(init=False)
    frames: int = field(init=False, default=0)
    period: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        """Open one window per meter, all of the same length."""
        self.frame = Meter(self.window)
        self.advance = Meter(self.window)
        self.draw = Meter(self.window)
        self.swap = Meter(self.window)
        self.gpu = Meter(self.window)

    def count_frame(self, total: float) -> None:
        """
        Record a frame that was drawn, and how long it took.

        Args:
            total: How long the whole frame took, in seconds.

        """
        self.frames += 1
        self.frame.add(total)

    def restart(self, now: float) -> None:
        """
        Start counting the frame rate afresh.

        Called whenever the monitor is turned on or off: turned on, the
        first rate covers the second that follows instead of all the
        time the monitor spent asleep.

        Args:
            now: The moment the new period starts, in seconds.

        """
        self.frames = 0
        self.period = now

    def due(self, now: float) -> bool:
        """
        Tell whether the period is over and a rate can be shown.

        Args:
            now: The current moment, in seconds.

        Returns:
            True when the period has lasted long enough.

        """
        return now - self.period >= MONITOR_INTERVAL

    def rate(self, now: float) -> float:
        """
        Tell the frame rate held since the period started.

        Args:
            now: The current moment, in seconds.

        Returns:
            Frames per second, zero when no time has passed.

        """
        elapsed = now - self.period

        if elapsed <= 0:
            return 0.0

        return self.frames / elapsed

    @property
    def pace(self) -> float:
        """
        Tell the interval the frames have truly been holding.

        Not the budget: under a vsync a frame lasts what the screen
        gives it, and what the screen gives it is not always what it
        announces - a compositor may hold a window at sixty hertz on a
        screen naming a hundred, and a window dragged onto another
        screen changes pace without saying so.

        Returns:
            The interval half the frames stay under, in seconds, zero
            when nothing was measured.

        """
        return self.frame.percentile(MEDIAN)

    @property
    def drops(self) -> int:
        """
        Count the frames of the window that broke the pace.

        A drop is a stutter, which is to say a frame standing out of
        the interval its neighbours hold - a missed refresh lasting
        twice what the others last. It is not a frame slower than the
        budget: rendering that never fits in the budget is regular, and
        what says so is ``headroom``, measured on the work.

        Returns:
            How many frames exceeded the pace by the drop factor.

        """
        limit = self.pace * DROP_FACTOR

        return sum(1 for sample in self.frame.samples if sample > limit)

    @property
    def cpu(self) -> float:
        """
        Tell what the two halves of a frame cost on the processor.

        This is the one number the vsync cannot flatter: it is measured
        on the work, not on the wait.

        Returns:
            The average of advancing and drawing, in seconds.

        """
        return self.advance.mean + self.draw.mean

    @property
    def headroom(self) -> float:
        """
        Tell the share of the frame budget nothing is using.

        Returns:
            The free share of the budget, from 0 to 1.

        """
        if self.budget <= 0:
            return 0.0

        return max(0.0, 1.0 - self.cpu / self.budget)


@dataclass(frozen=True, slots=True)
class RenderProfile:
    """
    What a frame has to draw, and what it draws into.

    The steady half of the report, next to the meters that move: it only
    changes when the cube, the window or the mode does. The viewer fills
    in what it knows and a host completes the rest - the refresh rate of
    a screen and the vsync belong to a window - through a
    ``dataclasses.replace()``.
    """

    instances: int = 0
    triangles: int = 0
    instance_bytes: int = 0
    size: tuple[int, int] = (0, 0)
    samples: int = 0
    draw_calls: int = 0
    context: str = ''
    refresh: float = 0.0
    vsync: bool = True


def meter_line(name: str, meter: Meter, note: str = '') -> str:
    """
    Write one line of the report, for one meter.

    Args:
        name: What the meter measures.
        meter: The samples to summarize.
        note: What to add at the end of the line, if anything.

    Returns:
        The line, or a plain mention when nothing was measured.

    """
    if not meter.count:
        return f'  {name:<{ REPORT_COLUMN }} not measured{ note }'

    return (
        f'  {name:<{ REPORT_COLUMN }} {milliseconds(meter.mean):>6} ms'
        f'   min {milliseconds(meter.minimum):>6}'
        f'   p95 {milliseconds(meter.percentile()):>6}'
        f'   max {milliseconds(meter.maximum):>6}{ note }'
    )


def budget_line(monitor: Monitor, profile: RenderProfile) -> str:
    """
    Write what a frame is given, and what is left of it.

    Args:
        monitor: The meters the headroom is read on.
        profile: What the picture is drawn into, the refresh rate of the
            screen included.

    Returns:
        The headroom and budget line of the report.

    """
    screen = f' ({ profile.refresh:.0f} Hz screen)' if profile.refresh else ''

    return (
        f'  {"headroom":<{ REPORT_COLUMN }} {monitor.headroom:.0%}'
        f'   budget { milliseconds(monitor.budget) } ms{ screen }'
    )


def scene_line(profile: RenderProfile) -> str:
    """
    Write what a frame has to draw.

    The triangles are the ones of the cube alone: the ball core is a
    draw call of its own, and it never changes.

    Args:
        profile: What the picture is made of.

    Returns:
        The scene line of the report.

    """
    kibibytes = profile.instance_bytes / KIBIBYTE

    return (
        f'  {"scene":<{ REPORT_COLUMN }} { profile.instances } instances, '
        f'{ profile.triangles } triangles, {kibibytes:.1f} KiB'
    )


def target_line(profile: RenderProfile) -> str:
    """
    Write what a frame is drawn into.

    Args:
        profile: What the picture is drawn into.

    Returns:
        The target line of the report.

    """
    width, height = profile.size

    return (
        f'  {"target":<{ REPORT_COLUMN }} { width }x{ height }, '
        f'{ profile.samples } samples, { profile.draw_calls } draw calls'
    )


def debug_title(
        monitor: Monitor,
        now: float,
        title: str = WINDOW_TITLE,
        *,
        vsync: bool = True,
) -> str:
    """
    Write the performance of the rendering in the title of a window.

    The frame rate is kept, since it is what tells a frame was dropped
    at all, but it comes with the two numbers it never carried: what a
    frame costs on the processor and what it costs on the GPU.

    Args:
        monitor: The meters to read.
        now: The current moment, in seconds.
        title: Title of the window, kept ahead of the numbers.
        vsync: Whether the frames are still waiting for the screen. Said
            plainly when they are not, the rate meaning something else
            entirely then.

    Returns:
        The title to give the window.

    """
    parts = [
        f'{ monitor.rate(now):.0f} fps',
        f'cpu { milliseconds(monitor.cpu) }',
        f'gpu { milliseconds(monitor.gpu.mean) } ms',
        f'{ monitor.drops } dropped',
    ]

    if not vsync:
        parts.append('vsync off')

    return f'{ title } - { " | ".join(parts) }'


def debug_report(
        monitor: Monitor,
        profile: RenderProfile,
        title: str = WINDOW_TITLE,
) -> str:
    """
    Write everything the monitor knows, as a block for a terminal.

    The window has room for three numbers; the rest goes to standard
    output, where the shortcuts and the screenshots already go. Drawing
    it in the scene would take a font, an atlas and a program of its
    own, which is precisely what this backend exists without.

    Args:
        monitor: The meters to read.
        profile: What a frame has to draw and what it draws into.
        title: Name of the window the report is about.

    Returns:
        The report, as a block of lines.

    """
    window = monitor.frame
    vsync = 'on' if profile.vsync else 'off'

    heading = (
        f'{ title } debug - { window.count } frames over '
        f'{window.total:.1f} s, { monitor.drops } dropped'
    )

    return '\n'.join((
        heading,
        meter_line('frame', window),
        meter_line('advance', monitor.advance),
        meter_line('draw', monitor.draw),
        meter_line('swap', monitor.swap, f'   vsync { vsync }'),
        meter_line('gpu', monitor.gpu),
        budget_line(monitor, profile),
        scene_line(profile),
        target_line(profile),
        f'  {"context":<{ REPORT_COLUMN }} { profile.context }',
    ))
