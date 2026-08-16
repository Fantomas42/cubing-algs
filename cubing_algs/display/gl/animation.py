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
"""
import math
from collections.abc import Iterable
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import replace
from typing import TYPE_CHECKING

from cubing_algs.constants import INNER_MOVES
from cubing_algs.display.gl.constants import FRAME_RATE
from cubing_algs.display.gl.constants import HALF_TURN_FACTOR
from cubing_algs.display.gl.constants import MOVE_DURATION
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

# Angle of a single quarter turn, in radians.
QUARTER_TURN = math.pi / 2

# Axis every base move turns around, and the sign of a clockwise
# quarter turn around it. The axes are the ones of the grid of
# geometry.py: 0 runs from L to R, 1 from D to U, 2 from B to F.
#
# A move is called clockwise as seen from its own face, so a face
# sitting at the positive end of its axis turns the negative way of the
# right hand rule, and the one facing it turns the other way. The
# slices follow the face they are named after: M follows L, E follows
# D, S follows F, and the three rotations follow R, U and F.
MOVE_TURNS: dict[str, tuple[int, int]] = {
    'R': (0, -1), 'L': (0, 1), 'M': (0, 1), 'x': (0, -1),
    'U': (1, -1), 'D': (1, 1), 'E': (1, 1), 'y': (1, -1),
    'F': (2, -1), 'B': (2, 1), 'S': (2, -1), 'z': (2, -1),
}

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
            moves: The algorithm to play.
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
        self.moves: tuple[Move, ...] = tuple(parse_moves(moves))
        self.geometry: CubeGeometry = build_cube_geometry(self.cube.size)

        self.index = 0
        self.elapsed = 0.0
        self.resting = self.build_scene()
        self.turn = self.load_turn()

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

    def load_turn(self) -> Turn | None:
        """
        Walk to the next move that actually turns something.

        A pause turns nothing and is not applied to the cube either: it
        is simply skipped.

        Returns:
            The turn of the next move, or None once the algorithm is
            over.

        """
        while self.index < len(self.moves):
            turn = build_turn(self.moves[self.index], self.cube.size)

            if turn is not None:
                return turn

            self.index += 1

        return None

    @property
    def finished(self) -> bool:
        """
        Tell whether every move has been played.

        Returns:
            True when the cube has reached its final state.

        """
        return self.turn is None

    @property
    def step(self) -> float:
        """
        Tell how long the move under way is given to happen.

        Returns:
            The beat of the current turn, in seconds, which a half turn
            stretches. The plain duration once nothing is turning.

        """
        if self.turn is None:
            return self.duration

        return self.turn.duration(self.duration)

    @property
    def scene(self) -> Scene:
        """
        Build the scene to draw at the current moment.

        Returns:
            The cube, the layers of the move under way turned as far as
            they have gone.

        """
        if self.turn is None:
            return self.resting

        return turned_scene(
            self.resting,
            self.turn,
            ease(self.elapsed / self.step),
        )

    def land(self) -> None:
        """
        Land the move under way on the cube, and load the next one.

        This is the only place the state of the cube changes, which is
        what keeps the final state of an animation equal to the one a
        plain ``VCube.rotate()`` of the whole algorithm gives.
        """
        self.cube.rotate(self.moves[self.index])
        self.index += 1

        self.resting = self.build_scene()
        self.turn = self.load_turn()

        if self.turn is None:
            self.elapsed = 0.0

    def advance(self, delta: float) -> Scene:
        """
        Let some time pass, and build the scene it leads to.

        A delta longer than a move is honored: several moves then land
        at once, which is what keeps an animation on time on a machine
        that cannot keep up.

        Args:
            delta: Seconds gone by since the last call. A negative one
                is ignored: an animation does not run backwards.

        Returns:
            The scene to draw right now.

        """
        self.elapsed += max(delta, 0.0)

        while self.turn is not None and self.elapsed >= self.step:
            self.elapsed -= self.step
            self.land()

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
