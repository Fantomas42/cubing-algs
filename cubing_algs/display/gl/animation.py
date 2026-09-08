"""
Animation of the GPU rendering backend.

Turns an algorithm into the series of scenes drawing it: one move at a
time, the layers it carries turning while the rest of the cube stands
still, and the move landing on the ``VCube`` once its turn is over.

Pure Python, and driven by elapsed time rather than by a loop of its
own: ``advance()`` is handed the seconds gone by and gives back the
scene to draw right now. Nothing blocks and nothing sleeps, so the very
same animation plays in a window and in an offscreen encoder.

Which cubies a move takes along is read from the move itself, no new
table: ``Move.layers`` covers every notation there is, from ``R`` to
``3-4Rw``, and the two cases it cannot tell apart on its own, the
slices and the rotations, are named here.

**A move carries a date, it starts on that date, and it lasts the gap
separating it from the next one**, bounded by the beat and by a floor.
A move with no date keeps the beat, so an ordinary algorithm plays
exactly as it always did; a gap between the end of a turn and the start
of the next is a **rest**, the cube standing still, which is the whole
information a replay of a solve carries. The dates come from the ``@``
of a timed algorithm, anchored on the first, or from whoever pushes a
move into the queue as it arrives.
"""
from collections import deque
from collections.abc import Iterable
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import replace
from typing import TYPE_CHECKING

from cubing_algs.constants import INNER_MOVES
from cubing_algs.display.gl.constants import FRAME_RATE
from cubing_algs.display.gl.constants import HALF_TURN_FACTOR
from cubing_algs.display.gl.constants import MINIMUM_MOVE_DURATION
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import MOVE_TURNS
from cubing_algs.display.gl.constants import PAUSE_DURATION
from cubing_algs.display.gl.constants import QUARTER_TURN
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.geometry import Cubie
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.presentation import DEFAULT_PRESENTATION
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.scene import Scene
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.display.gl.scene import resolve_display
from cubing_algs.display.gl.transforms import Mat4
from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves

if TYPE_CHECKING:  # pragma: no cover
    from cubing_algs.vcube import VCube

# The three rotation matrices, indexed by the axis they turn around.
ROTATION_BUILDERS = (Mat4.rotation_x, Mat4.rotation_y, Mat4.rotation_z)

# Faces lying at the far end of their axis: their layers are counted
# from there down, the other three straight up from the origin.
FAR_FACES = frozenset({'R', 'U', 'F'})

# The middle slices, which turn a single layer whatever the notation
# says. Move.is_inner_move also answers True for a layered move such as
# ``2R``, so the base move is what has to be looked at here.
SLICE_MOVES = frozenset(INNER_MOVES)

# Coefficients of the smoothstep easing a turn in and out.
EASE_SLOPE = 3.0
EASE_CURVE = 2.0

# A timestamp of the notation is written in milliseconds, a clock of the
# backend counts in seconds.
MILLISECONDS = 1000.0


@dataclass(frozen=True, slots=True)
class Turn:
    """
    The rotation one move applies, and the cubies it takes along.

    The angle is the whole turn, signed: a quarter turn one way or the
    other, or a half turn. Where the move stands at a given moment is
    a matter of progress, not of state.
    """

    axis: int
    angle: float
    coordinates: frozenset[int]

    def carries(self, cubie: Cubie) -> bool:
        """
        Tell whether a cubie turns along with the move.

        Args:
            cubie: The cubie to look at.

        Returns:
            True when the cubie belongs to a layer the move turns.

        """
        return (cubie.x, cubie.y, cubie.z)[self.axis] in self.coordinates

    def duration(self, base: float) -> float:
        """
        Tell how long the turn should be given to happen.

        A half turn covers twice the angle of a quarter one, so the same
        beat makes it go twice as fast. It gets a longer one instead,
        read on the angle rather than on the notation: ``M2`` and ``z2``
        are half turns as much as ``R2`` is.

        Args:
            base: How long a quarter turn lasts, in seconds.

        Returns:
            How long this turn lasts, in seconds.

        """
        if abs(self.angle) > QUARTER_TURN:
            return base * HALF_TURN_FACTOR

        return base

    def matrix(self, progress: float) -> Mat4:
        """
        Build the rotation the turn has reached.

        Args:
            progress: How far the turn has gone, from 0 to 1.

        Returns:
            The rotation matrix, to be applied before the model matrix
            of an instance: the cubie turns around the center of the
            cube, not around itself.

        """
        return ROTATION_BUILDERS[self.axis](self.angle * progress)


def turn_coordinates(move: Move, size: int) -> frozenset[int]:
    """
    Pick the layers of the grid a move takes along.

    Args:
        move: The move to animate.
        size: Size of the cube.

    Returns:
        The indices, along the axis of the move, of the layers it turns.

    """
    if move.is_rotation_move:
        return frozenset(range(size))

    if move.base_move in SLICE_MOVES:
        return frozenset({size // 2})

    if move.base_move in FAR_FACES:
        return frozenset(size - 1 - layer for layer in move.layers)

    return frozenset(move.layers)


def build_turn(move: Move, size: int) -> Turn | None:
    """
    Read the rotation a move applies to a cube of a given size.

    Args:
        move: The move to animate.
        size: Size of the cube.

    Returns:
        The turn of the move, or None when it turns nothing at all, as
        a pause does.

    """
    quarters = move.quarter_turns
    if not quarters:
        return None

    axis, direction = MOVE_TURNS[move.base_move]

    return Turn(
        axis=axis,
        angle=direction * quarters * QUARTER_TURN,
        coordinates=turn_coordinates(move, size),
    )


def ease(progress: float) -> float:
    """
    Soften both ends of a turn.

    A smoothstep: a layer leaves and reaches its resting place with a
    null speed, which is what a hand does and a linear ramp does not.

    Args:
        progress: How far the turn has gone, from 0 to 1.

    Returns:
        The eased progress, from 0 to 1.

    """
    clamped = min(max(progress, 0.0), 1.0)

    return clamped * clamped * (EASE_SLOPE - EASE_CURVE * clamped)


def turned_scene(scene: Scene, turn: Turn, progress: float) -> Scene:
    """
    Build the scene a turn has reached, part way through a move.

    Only the instances the move carries are rebuilt, and only their
    model matrix changes: the colors of a cubie belong to the piece and
    follow it around without anything to do.

    Args:
        scene: The scene of the cube before the move.
        turn: The rotation the move applies.
        progress: How far the turn has gone, from 0 to 1.

    Returns:
        The scene to draw right now.

    """
    rotation = turn.matrix(progress)

    return replace(
        scene,
        instances=tuple(
            replace(instance, model=rotation @ instance.model)
            if turn.carries(instance.cubie)
            else instance
            for instance in scene.instances
        ),
    )


class Animation:
    """
    An algorithm playing on a cube, one move at a time.

    A state machine driven by elapsed time: ``advance()`` is handed the
    seconds gone by since the last call and gives back the scene to
    draw. It never blocks, so the caller keeps its loop, be it the event
    loop of a window or the frame counter of an encoder.

    It consumes a **queue of dated moves** rather than a fixed tuple, so
    the very same machine plays an algorithm given whole and a stream a
    producer feeds it move by move through ``extend()``. A date is what
    settles the cadence: a move starts on its own, and lasts until the
    next one is due.

    The cube is a copy: playing an algorithm never touches the cube it
    was given. A move is applied to that copy only once its turn is
    over, so the state of the cube and what is on screen never disagree.
    """

    def __init__(
            self,
            cube: 'VCube',
            moves: Iterable[Move | str] | Move | str,
            presentation: Presentation = DEFAULT_PRESENTATION,
            *,
            duration: float = MOVE_DURATION,
    ) -> None:
        """
        Set an algorithm up to be played on a cube.

        The mode is resolved once, here: it may reorient the cube, and
        that orientation is read from the state of the cube, which the
        algorithm is precisely about to change. The moves are therefore
        played on the cube as the mode presents it.

        Args:
            cube: The cube to play the algorithm on, left untouched.
            moves: The algorithm to play. More are added later with
                ``extend()``, an empty one being a perfectly good start.
            presentation: The picture to make, of which the palette, the
                mode and the mask are read: an animation builds scenes,
                and knows nothing of how they are framed or drawn.
            duration: How long a single quarter turn lasts, in seconds.
                A half turn is given ``HALF_TURN_FACTOR`` times that.

        Raises:
            ValueError: When a move is given no time to happen.

        """
        if duration <= 0:
            msg = f'A move must last some time, got { duration }'
            raise ValueError(msg)

        self.cube, self.mask = resolve_display(
            cube.copy(full=True),
            presentation.palette,
            mode=presentation.mode,
            mask=presentation.mask,
        )

        self.presentation = presentation
        self.duration = duration
        self.minimum = MINIMUM_MOVE_DURATION
        self.pause = PAUSE_DURATION
        self.geometry: CubeGeometry = build_cube_geometry(self.cube.size)

        self.pending: deque[tuple[Move, float | None]] = deque()
        self.clock = 0.0
        self.end = 0.0
        self.elapsed = 0.0
        self.step = duration
        self.turn: Turn | None = None
        self.move: Move | None = None
        self.date: float | None = None

        self.resting = self.build_scene()

        self.extend(moves)
        self.load()

    def build_scene(self) -> Scene:
        """
        Build the scene of the cube as it stands right now.

        Returns:
            The scene of the current state of the cube.

        """
        return build_scene(
            self.cube,
            self.presentation.palette,
            self.geometry,
            mask=self.mask,
        )

    @property
    def following(self) -> float | None:
        """
        Tell when the move waiting at the head of the queue is due.

        Returns:
            The date of the next move, None when nothing is waiting or
            when what waits carries no date.

        """
        if not self.pending:
            return None

        return self.pending[0][1]

    def extend(
            self,
            moves: Iterable[Move | str] | Move | str,
            at: float | None = None,
    ) -> None:
        """
        Add moves to the queue, dated by whatever dates them.

        The door of a live producer: a thread pushing a move as it
        happens hands its arrival over as ``at``, and the cadence of the
        animation is the cadence of that hand. A timed algorithm dates
        itself through its ``@``, anchored on the first one so that an
        algorithm starting at twelve seconds does not open on twelve
        seconds of nothing.

        Only the **first** move of an untimed batch takes ``at``: an
        algorithm pushed whole is one entry, hence one date, hence the
        nominal beat for everything behind it, where four key presses
        are four dates, hence the cadence of the fingers.

        The timestamps are dropped on the way in, the parser of the core
        refusing an ``@`` it never produced itself.

        Args:
            moves: The moves to add.
            at: When the entry arrived, on the clock of the animation.
                None for moves carrying no date of their own.

        """
        waiting = bool(self.pending)
        anchor: int | None = None
        base = self.clock if at is None else at

        for position, move in enumerate(parse_moves(moves)):
            date = at if position == 0 else None

            if move.is_timed:
                if anchor is None:
                    anchor = move.timed

                date = base + (move.timed - anchor) / MILLISECONDS

            self.pending.append((move.untimed, date))

        if not waiting:
            self.revise()

    def schedule(
            self,
            turn: Turn,
            date: float | None,
            following: float | None,
    ) -> float:
        """
        Tell how long the turn about to start is given to happen.

        A move lasts the gap separating it from the next one: played at
        the speed it was truly made, a ``U2`` flicked in a tenth of a
        second turns a hundred and eighty degrees in a tenth of a
        second, and there is no other honest reading of that gesture.
        The beat caps it, so nothing ever drags, and the floor keeps a
        turn readable.

        Args:
            turn: The rotation about to start.
            date: When the move is due, None when it carries no date.
            following: When the move behind it is due, None when nothing
                dated waits.

        Returns:
            The duration to give the turn, in seconds.

        """
        beat = turn.duration(self.duration)

        if date is None or following is None:
            return beat

        return max(min(beat, following - date), self.minimum)

    def retime(self, duration: float) -> None:
        """
        Change the duration of the turn under way without making it jump.

        Where a turn stands is read as ``elapsed / step``, so shrinking
        the step alone would send the layer flying forward. The elapsed
        time is remapped instead, which leaves the angle exactly where
        it was: how far the turn has gone is what is kept, not how long
        it has taken.

        Args:
            duration: The duration the turn should have had, in seconds.

        """
        self.elapsed = duration * (self.elapsed / self.step)
        self.step = duration

    def revise(self) -> None:
        """
        Give the turn under way the duration its successor now calls for.

        A move pushed into an empty queue arrives after the one being
        played had to guess its own duration, having nothing behind it:
        that guess is the beat, and this is where it is settled. It is
        what keeps the cube a single move behind the fingers whatever
        the cadence, rather than a whole beat behind.
        """
        if self.turn is None or self.date is None or self.following is None:
            return

        self.retime(self.schedule(self.turn, self.date, self.following))

    def load(self) -> None:
        """
        Start the next move that is both due and turns something.

        A move whose date has not come yet is left where it is: the gap
        in front of it is a rest, nothing turns, and the scene stands
        still. A pause turns nothing and never reaches the cube, but it
        says a hesitation: it holds what follows back by its own beat,
        which a later date of its own overrides.
        """
        while self.pending:
            move, date = self.pending[0]

            if date is not None and date > self.clock:
                break

            self.pending.popleft()
            start = self.end if date is None else max(date, self.end)
            turn = build_turn(move, self.cube.size)

            if turn is None:
                self.end = start + self.pause
                continue

            self.move = move
            self.date = date
            self.turn = turn
            self.elapsed = self.clock - start
            self.step = self.schedule(turn, date, self.following)

            return

        self.move = None
        self.date = None
        self.turn = None
        self.elapsed = 0.0
        self.step = self.duration

    @property
    def finished(self) -> bool:
        """
        Tell whether every move has been played.

        A rest is not the end: nothing turns, but a move is waiting for
        its date, and the frames of that wait are what a replay is made
        of. A pause closing an algorithm is such a rest, with nothing
        behind it but the time it holds.

        Returns:
            True when the cube has reached its final state.

        """
        return (
            self.turn is None
            and not self.pending
            and self.clock >= self.end
        )

    @property
    def scene(self) -> Scene:
        """
        Build the scene to draw at the current moment.

        A move waiting behind a pause is loaded before its turn comes,
        with a negative elapsed time: the very same resting scene is
        handed back frame after frame, which is what the instance cache
        of the renderer reads.

        Returns:
            The cube, the layers of the move under way turned as far as
            they have gone.

        """
        if self.turn is None or self.elapsed <= 0.0:
            return self.resting

        return turned_scene(
            self.resting,
            self.turn,
            ease(self.elapsed / self.step),
        )

    def land(self, move: Move) -> None:
        """
        Land the move under way on the cube, and load the next one.

        This is the only place the state of the cube changes, which is
        what keeps the final state of an animation equal to the one a
        plain ``VCube.rotate()`` of the whole algorithm gives.

        Args:
            move: The move that has just finished turning.

        """
        self.cube.rotate(move)
        self.end = self.clock - self.elapsed

        self.resting = self.build_scene()
        self.load()

    def advance(self, delta: float) -> Scene:
        """
        Let some time pass, and build the scene it leads to.

        A delta longer than a move is honored: several moves then land
        at once, which is what keeps an animation on time on a machine
        that cannot keep up. When nothing turns, the clock still runs:
        that is a rest, and the next move is waiting for its date.

        Args:
            delta: Seconds gone by since the last call. A negative one
                is ignored: an animation does not run backwards.

        Returns:
            The scene to draw right now.

        """
        gone = max(delta, 0.0)
        self.clock += gone

        if self.turn is None:
            self.load()
        else:
            self.elapsed += gone

        move = self.move

        while move is not None and self.elapsed >= self.step:
            self.elapsed -= self.step
            self.land(move)
            move = self.move

        return self.scene

    def play(self, frame_rate: float = FRAME_RATE) -> Iterator[Scene]:
        """
        Play the whole algorithm, one scene per frame.

        The first scene is the cube before anything happens and the last
        one the cube at rest, once every move has landed.

        Args:
            frame_rate: Frames per second the animation is sampled at.

        Yields:
            The scene of each frame, in order.

        Raises:
            ValueError: When the frame rate is not strictly positive.

        """
        if frame_rate <= 0:
            msg = f'A frame rate must be positive, got { frame_rate }'
            raise ValueError(msg)

        step = 1.0 / frame_rate

        yield self.scene

        while not self.finished:
            yield self.advance(step)
