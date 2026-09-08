"""
How old a move already is by the time a viewer hears about it.

The companion of ``Viewer.push(age=)``: it says what to do with an age,
and this is where one is read. A producer feeding a viewer from outside
- a bluetooth cube counting its own milliseconds, a replay stamped on
the clock it was captured on, a publisher stamping epoch seconds - never
shares an origin with ``perf_counter``, and it never has to: two clocks
with no common origin still tell the same *durations*, which is the
whole of what is asked of them here.

Pure arithmetic: nothing of a cube, of a socket or of a window.
"""
from collections import deque

from cubing_algs.display.gl.constants import CLOCK_SPAN
from cubing_algs.display.gl.constants import MILLISECONDS
from cubing_algs.display.gl.constants import MOVE_LEAD


class MoveClock:
    """
    Where the clock of a producer stands next to the clock of a viewer.

    A producer stamps what it reports on a counter of its own, started
    when it was powered on and sharing no origin with anything here. The
    offset between the two is read as the smallest delay ever observed
    between a stamp and its arrival, and what a later arrival exceeds it
    by is the delay that move alone suffered.

    So what is measured is the **jitter** and never the latency: the
    minimum absorbs whatever the link costs every single time, and no
    reading from this side can tell a constant delay from a difference
    of origins. That constant is what ``lead`` stands for, and why it is
    a setting rather than a measurement.

    What it buys is the cadence of the gesture in place of the cadence of
    the link: a bluetooth stack batching two moves into one packet hands
    them over at the very same instant, and the stamps the producer wrote
    are what puts them back where they happened.

    A delay is only ever known against a **younger** arrival, so the head
    of the very first burst is handed over younger than it is. It lasts
    one burst, and it errs on the side of the cube being behind rather
    than ahead.
    """

    def __init__(
            self,
            lead: float = MOVE_LEAD,
            ceiling: float = 0.0,
            span: int = CLOCK_SPAN,
    ) -> None:
        """
        Open a clock on a producer nothing has been heard from yet.

        Args:
            lead: What every move is aged by before anything is
                measured, in seconds.
            ceiling: The most a move may ever be aged by, in seconds,
                zero for no limit at all.
            span: How many arrivals the offset is read on.

        """
        self.lead = lead
        self.ceiling = ceiling
        self.span = span
        self.delays: deque[float] = deque(maxlen=span)

    def reset(self) -> None:
        """
        Forget the producer that was being timed.

        The offset belongs to the connection it was measured in: a cube
        that comes back has been counting all along, and a session that
        restarts may not even be the same producer. Keeping the reading
        would age every move of the new one by the drift of the old.
        """
        self.delays.clear()

    def age(self, stamp: float | None, now: float) -> float:
        """
        Tell how long ago the move carrying a stamp truly happened.

        Args:
            stamp: The clock of the producer when it reported the move,
                in milliseconds. None when it reported none, which is
                what a producer saying nothing of its own time looks
                like.
            now: The moment the move arrived, on the clock of the
                consumer, in seconds.

        Returns:
            The age of the move in seconds, never negative and never
            past the ceiling.

        """
        if stamp is None:
            return self.capped(self.lead)

        delay = now - stamp / MILLISECONDS
        self.delays.append(delay)

        return self.capped(self.lead + delay - min(self.delays))

    def capped(self, age: float) -> float:
        """
        Hold an age under what a turn can give away and stay one.

        An age reaching the beat starts the turn where it ends, and the
        face lands without ever being seen to move. It is also what a
        clock read wrong cannot get past - a producer whose counter
        jumped, a stamp from another origin - so a reading that makes no
        sense costs a snap and never a cube frozen in the future.

        Nothing holds the other end: an age is a delay measured against
        the smallest delay ever seen, so it cannot come out negative,
        and ``Viewer.push()`` answers for a lead given below zero.

        Args:
            age: The age to hold, in seconds.

        Returns:
            The age, never past the ceiling.

        """
        if self.ceiling and age > self.ceiling:
            return self.ceiling

        return age
