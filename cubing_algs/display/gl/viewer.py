"""
Interactive viewer of the GPU rendering backend.

A cube, a camera, a queue of moves, and the very same renderer an
offscreen render uses: nothing is drawn here that ``render()`` would not
draw, the cube simply keeps moving.

**This module owns no window and no loop.** It names neither glfw nor
any toolkit: a ``Viewer`` is driven by a *host* - the glfw one lives in
``host.py``, a Qt widget or anything else is written the same way - which
opens a context, hands it over as a ``Stage``, and calls ``frame()``,
``press()``, ``drag()`` and ``scroll()`` from its own loop. That is what
lets the very same viewer be embedded in an application that already has
an event loop of its own.

``Viewer.run()`` is the convenience of the library, and the only line
here reaching for the glfw host.
"""
import math
import sys
import tempfile
import time
from collections import deque
from contextlib import nullcontext
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Self

from cubing_algs.annotations import CubeDisplayMask
from cubing_algs.display.constants import DISTANCE
from cubing_algs.display.gl.animation import Animation
from cubing_algs.display.gl.camera import OrbitCamera
from cubing_algs.display.gl.camera import fit_aspect
from cubing_algs.display.gl.camera import fit_fov
from cubing_algs.display.gl.constants import AXES_REACH
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import EXPLODE_SPEED
from cubing_algs.display.gl.constants import EXPLODE_SPREAD
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import ORBIT_SENSITIVITY
from cubing_algs.display.gl.constants import SCREENSHOT_NAME
from cubing_algs.display.gl.constants import SPREAD_SETTLED
from cubing_algs.display.gl.constants import VIEWER_BACKGROUND
from cubing_algs.display.gl.constants import VIEWER_SIZE
from cubing_algs.display.gl.constants import ZOOM_STEP
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import describe
from cubing_algs.display.gl.encode import write_png
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.metrics import Monitor
from cubing_algs.display.gl.metrics import RenderProfile
from cubing_algs.display.gl.presentation import Presentation
from cubing_algs.display.gl.renderer import AxesRenderer
from cubing_algs.display.gl.renderer import GpuTimer
from cubing_algs.display.gl.renderer import OffscreenTarget
from cubing_algs.display.gl.renderer import Renderer
from cubing_algs.display.gl.scene import INSTANCE_SIZE
from cubing_algs.display.gl.scene import Scene
from cubing_algs.display.gl.scene import resolve_display
from cubing_algs.display.gl.transforms import IDENTITY
from cubing_algs.display.gl.transforms import OrientationTracker
from cubing_algs.display.gl.transforms import Quat
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.timing import untime_moves

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

    from cubing_algs.vcube import VCube

# Letters turning a face of the cube, and the ones turning a middle
# slice. A host hands over the letter of the key that was pressed, which
# is already the notation of the move: no table maps the two.
FACE_KEYS = frozenset('RUFLDB')
SLICE_KEYS = frozenset('MES')

# Letters turning the whole cube, whose notation is lowercase.
ROTATION_KEYS = {'X': 'x', 'Y': 'y', 'Z': 'z'}

# Draw calls a frame always makes: the ball core, then the cube itself.
# The axes add one more when they are shown.
CUBE_DRAW_CALLS = 2


def key_notation(
        letter: str,
        *,
        prime: bool = False,
        double: bool = False,
        wide: bool = False,
) -> str:
    """
    Read the move a key stands for, modifiers included.

    Args:
        letter: The uppercase letter of the key, empty for none.
        prime: Whether the move is turned the other way.
        double: Whether the move is a half turn. Wins over ``prime``.
        wide: Whether a face turn takes the layer behind it along.
            Meaningless on a slice or on a rotation, and ignored there.

    Returns:
        The notation of the move, empty when the key plays none.

    """
    if letter in ROTATION_KEYS:
        base = ROTATION_KEYS[letter]
    elif letter in SLICE_KEYS:
        base = letter
    elif letter in FACE_KEYS:
        base = f'{ letter }w' if wide else letter
    else:
        return ''

    if double:
        return f'{ base }2'

    return f"{ base }'" if prime else base


def resolve_orientation(
        source: Quat | OrientationTracker | None,
) -> Quat:
    """
    Read how the cube is held, whoever is holding it.

    A tracker is read rather than copied, so that whatever feeds it -
    the thread of a bluetooth cube, a replay - only has to hand it over
    once, and every frame then draws the last quaternion it received. A
    quaternion given directly is taken as it comes.

    Args:
        source: The tracker following a sensor, a quaternion of its own,
            or nothing when no one outside is holding the cube.

    Returns:
        The rotation to draw the whole cube with, the identity when
        nothing outside is holding it.

    """
    if source is None:
        return IDENTITY

    if isinstance(source, OrientationTracker):
        return source.orientation

    return source


def settle_spread(spread: float, target: float, delta: float) -> float:
    """
    Move the opening of the cube towards what it is asked for.

    An exponential approach rather than a fixed step: the same second of
    elapsed time carries the same share of the distance, whether it came
    as one frame or as sixty. It never quite lands, so what is within
    ``SPREAD_SETTLED`` of the target is snapped onto it - a cube still
    moving by a thousandth would rebuild its scene forever.

    Args:
        spread: How far the cube stands open now.
        target: How far open it is heading.
        delta: Seconds gone by since the last call.

    Returns:
        The opening the elapsed time leads to.

    """
    moved = target + (spread - target) * math.exp(-EXPLODE_SPEED * delta)

    if abs(moved - target) < SPREAD_SETTLED:
        return target

    return moved


def screenshot_path() -> Path:
    """
    Build the name of the next screenshot.

    Returns:
        A path in the temporary directory, stamped with the current
        time so that two screenshots never overwrite one another.

    """
    return Path(tempfile.gettempdir()) / time.strftime(SCREENSHOT_NAME)


def output(text: str) -> None:
    """Write a line to standard output."""
    sys.stdout.write(text + '\n')


@dataclass(slots=True)
class Stage:
    """
    The GPU side of a viewer: a context, and what draws into it.

    Held apart from the viewer so that the cube, the camera and the
    animation all exist before any context does, and outlive it - which
    is what keeps the rest of the viewer testable without a GPU.

    It knows nothing of windows. Whoever opened the context owns it and
    gives it back; the stage only ever releases what it built itself.
    ``target`` is the framebuffer a frame lands in: the screen when left
    out, and the widget one under a toolkit rendering into an FBO of its
    own, ``QOpenGLWidget`` among them.
    """

    context: 'moderngl.Context'
    renderer: Renderer
    axes: AxesRenderer
    size: tuple[int, int]
    target: 'moderngl.Framebuffer | None' = None
    background: tuple[float, float, float, float] = VIEWER_BACKGROUND
    timer: GpuTimer | None = None

    @classmethod
    def attach(
            cls,
            context: 'moderngl.Context',
            geometry: CubeGeometry,
            size: tuple[int, int],
            target: 'moderngl.Framebuffer | None' = None,
    ) -> Self:
        """
        Build everything drawing takes, on a context somebody else owns.

        The context must have been made current beforehand.

        Args:
            context: The context to draw with.
            geometry: The mesh of a cubie and the cubies to place it on.
            size: Width and height of the drawing surface, in pixels.
            target: The framebuffer to draw into. The screen of the
                context when left out.

        Returns:
            A stage ready to be drawn into.

        """
        return cls(
            context=context,
            renderer=Renderer.create(context, geometry),
            axes=AxesRenderer.create(context, geometry.radius * AXES_REACH),
            size=size,
            target=target,
            timer=GpuTimer.create(context),
        )

    @property
    def framebuffer(self) -> 'moderngl.Framebuffer':
        """
        Tell where a frame lands.

        Returns:
            The framebuffer given at attach time, the screen of the
            context when none was.

        """
        if self.target is None:
            return self.context.screen

        return self.target

    def use(self) -> None:
        """
        Make the drawing surface current and clear it.

        The viewport is set on every frame rather than on resize alone:
        moderngl reads the size of the screen framebuffer once, when the
        context is created, and would otherwise draw into the window the
        user opened rather than into the one they are looking at.
        """
        framebuffer = self.framebuffer

        framebuffer.use()
        self.context.viewport = (0, 0, *self.size)
        framebuffer.clear(color=self.background)

    def close(self) -> None:
        """
        Give back what the stage built on the GPU.

        The context is left alone: it belongs to whoever created it, and
        an embedded viewer must not take a toolkit's context down with
        it. The timer is dropped rather than released, moderngl giving a
        query back to the garbage collector alone.
        """
        self.timer = None

        self.axes.release()
        self.renderer.release()


@dataclass(slots=True)
class Viewer:
    """
    A cube turning under the mouse and the keyboard, in any host.

    Built with the options of ``render()``, so that what a window shows
    and what a PNG holds are the same picture: same palette, same mode,
    same mask, same framing. The mode is resolved once, when the viewer
    is built, exactly as an animation does it: it may reorient the cube,
    and reading that orientation again after every move would make the
    cube jump around.

    The viewer owns no window and no loop. A host attaches a ``Stage``
    to it, then calls ``frame()`` once per frame and hands the input
    over through ``press()``, ``drag()``, ``scroll()`` and ``resize()``.
    ``run()`` is the shortcut opening a glfw window of its own.

    ``orientation`` is where something outside takes the cube in hand: a
    quaternion, or an ``OrientationTracker`` fed by a bluetooth sensor,
    the tracker then being read anew on every frame. The camera keeps
    orbiting on top of it, and the light stays where it is.

    ``exploded`` opens the cube up, every piece flying away from the
    center: a host toggles it the way it toggles ``show_axes``, and the
    cube travels there rather than jumping. The camera stays where it
    is, so an open cube grows on the screen and reaches past the border
    of the window - the wheel is what looking inside costs. ``scene``
    stays the picture of the frame, ``assembled`` the cube as the
    animation built it, before it was opened.

    ``debug`` turns the performance monitoring on: what a frame costs is
    always measured on the processor, two clock readings being nothing
    next to a frame, but the GPU is only timed when it is asked for, a
    timer query being the one measure that costs something.
    """

    cube: 'VCube'
    palette: str = ''
    mode: str = ''
    mask: CubeDisplayMask = ''
    rotation: str = ''
    distance: float = 0.0
    window_size: tuple[int, int] = VIEWER_SIZE
    look: Look = DEFAULT_LOOK
    duration: float = MOVE_DURATION
    debug: bool = False
    show_axes: bool = False
    orientation: Quat | OrientationTracker | None = None
    exploded: bool = False

    monitor: Monitor = field(init=False, default_factory=Monitor)
    geometry: CubeGeometry = field(init=False)
    camera: OrbitCamera = field(init=False)
    scene: Scene = field(init=False)
    assembled: Scene = field(init=False)
    spread: float = field(init=False, default=0.0)
    origin: 'VCube' = field(init=False)
    stage: Stage | None = field(init=False, default=None)
    animation: Animation = field(init=False)
    pending: deque[tuple[str, float]] = field(
        init=False, default_factory=deque[tuple[str, float]],
    )

    def __post_init__(self) -> None:
        """Settle what is drawn, and how it is framed, once and for all."""
        self.cube, self.mask = resolve_display(
            self.cube.copy(full=True), self.palette,
            mode=self.mode, mask=self.mask,
        )

        self.origin = self.cube.copy(full=True)
        self.geometry = build_cube_geometry(self.cube.size)
        self.reload()

        width, height = self.window_size
        self.camera = OrbitCamera.from_rotation(
            self.rotation, self.distance, self.geometry.radius, width / height,
        )

    @property
    def framing_fov(self) -> float:
        """
        Tell the field of view holding the whole cube, before any zoom.

        Returns:
            The vertical field of view of a square viewport, in radians.

        """
        return fit_fov(self.geometry.radius, self.distance or DISTANCE)

    def reload(self) -> None:
        """
        Start a fresh animation on the cube the viewer now holds.

        One animation is built and kept, rather than one per move: it
        is the queue every producer pours into, and the only thing that
        ever turns the cube. The viewer holds the very cube the
        animation plays on, so what a move lands on is what the viewer
        shows, with nothing to hand back and forth.
        """
        self.animation = Animation(
            self.cube, '',
            Presentation(palette=self.palette, mask=self.mask),
            duration=self.duration,
        )

        self.cube = self.animation.cube
        self.assembled = self.animation.resting
        self.scene = self.assembled.exploded(self.spread)

    def require_stage(self) -> Stage:
        """
        Hand the stage being drawn into over.

        Returns:
            The stage the viewer draws into.

        Raises:
            GLContextError: When no stage is attached.

        """
        if self.stage is None:
            msg = 'The viewer has no window open'
            raise GLContextError(msg)

        return self.stage

    def attach(self, stage: Stage) -> None:
        """
        Draw into the stage a host has just opened.

        Args:
            stage: The context and the renderers to draw with. Its size
                is taken as the one of the drawing surface, so a host
                reporting a framebuffer larger than the window it asked
                for frames the cube on what it truly has.

        """
        self.stage = stage
        self.resize(stage.size)

    def detach(self) -> None:
        """
        Give the stage back, if one is attached.

        What the stage built on the GPU is released; the context is not,
        a host having every right to keep drawing something else with
        it.
        """
        if self.stage is None:
            return

        self.stage.close()
        self.stage = None

    def push(self, notation: str) -> bool:
        """
        Queue a move to be played, when the cube can take it.

        A cube refuses what its size makes meaningless, an ``M`` on a
        2x2x2 among others. Such a move is dropped here rather than in
        the middle of the loop, where it would bring the window down.
        What is played on is a copy of ``origin``: whether a move is
        valid only depends on the size of the cube, never on its state,
        and nothing touches ``origin`` after the viewer is built. A
        producer of its own thread may therefore push, ``deque.append``
        being atomic.

        The move is validated undressed of its timestamps, and queued
        dressed: a producer stamping what it sends - a bluetooth cube, a
        replay - has its cadence read from those very stamps.

        Args:
            notation: The move to play, empty for none.

        Returns:
            True when the move was queued.

        """
        if not notation:
            return False

        try:
            self.origin.copy().rotate(
                parse_moves(notation).transform(untime_moves),
            )
        except InvalidMoveError:
            return False

        self.pending.append((notation, time.perf_counter()))

        return True

    def press(
            self,
            letter: str,
            *,
            prime: bool = False,
            double: bool = False,
            wide: bool = False,
    ) -> bool:
        """
        Queue the move a key stands for.

        The vocabulary a host speaks: a letter and three modifiers, none
        of which belongs to any toolkit.

        Args:
            letter: The uppercase letter of the key, empty for none.
            prime: Whether the move is turned the other way.
            double: Whether the move is a half turn.
            wide: Whether a face turn takes the layer behind it along.

        Returns:
            True when the key played a move.

        """
        return self.push(
            key_notation(letter, prime=prime, double=double, wide=wide),
        )

    def drag(self, delta_x: float, delta_y: float) -> None:
        """
        Orbit the camera along a movement of the mouse.

        The cube turns the way the mouse goes: dragging to the right
        brings the left face in, dragging down brings the top in.

        Args:
            delta_x: Pixels the cursor moved to the right.
            delta_y: Pixels the cursor moved down.

        """
        self.camera.orbit(
            -delta_x * ORBIT_SENSITIVITY,
            delta_y * ORBIT_SENSITIVITY,
        )

    def scroll(self, notches: float) -> None:
        """
        Move the camera closer to the cube, or further away.

        Args:
            notches: Notches the wheel was turned by, forward being
                positive.

        """
        self.camera.zoom(ZOOM_STEP ** notches)

    def advance(self, delta: float) -> Scene:
        """
        Let some time pass, and build the scene it leads to.

        The time it takes is measured, and it is the half of a frame the
        processor spends alone: the state machine, the scene it rebuilds
        and the colors it reads all happen here, with the GPU idle.

        The viewer cadences nothing: it hands the moves that arrived
        over, each with the moment it arrived, and the animation plays
        them at the cadence those moments describe. An arrival is
        stamped on the clock of the caller, so it is handed over as the
        age it has reached on this very frame - the two clocks are never
        assumed to have the same origin.

        The opening of the cube travels here too, and the scene is only
        rebuilt when something moved: a cube standing still, open or
        closed, hands the very same scene over frame after frame, which
        is what the instance buffer is cached on.

        Args:
            delta: Seconds gone by since the last call.

        Returns:
            The scene to draw right now.

        """
        start = time.perf_counter()

        if self.cube is not self.animation.cube:
            self.reload()

        clock = self.animation.clock + max(delta, 0.0)

        while self.pending:
            notation, arrival = self.pending.popleft()
            self.animation.extend(notation, at=clock - (start - arrival))

        spread = settle_spread(
            self.spread, EXPLODE_SPREAD if self.exploded else 0.0, delta,
        )
        assembled = self.animation.advance(delta)

        if assembled is not self.assembled or spread != self.spread:
            self.assembled = assembled
            self.scene = assembled.exploded(spread)

        self.spread = spread

        self.monitor.advance.add(time.perf_counter() - start)

        return self.scene

    def reset_cube(self) -> None:
        """Put the cube back to the state the viewer opened on."""
        self.cube = self.origin.copy(full=True)
        self.pending.clear()
        self.reload()

    def reset_camera(self) -> None:
        """Frame the cube again, as it was framed when the window opened."""
        self.camera = OrbitCamera.from_rotation(
            self.rotation, self.distance,
            self.geometry.radius, self.camera.aspect,
        )

    def resize(self, size: tuple[int, int]) -> None:
        """
        Take the drawing surface to a new size.

        The field of view is fitted again rather than kept: a window
        taller than it is wide would cut the cube on both sides. It is
        fitted on the framing distance and not on the current one, so
        that resizing a window never undoes a zoom.

        Args:
            size: Width and height of the framebuffer, in pixels. A null
                one, as a minimized window reports, is ignored.

        """
        width, height = size

        if not width or not height:
            return

        if self.stage is not None:
            self.stage.size = size

        self.camera.aspect = width / height
        self.camera.fov = fit_aspect(self.framing_fov, self.camera.aspect)

    def draw(
            self,
            scene: Scene | None = None,
            look: Look | None = None,
            camera: OrbitCamera | None = None,
    ) -> None:
        """
        Draw a picture into the stage, the one the viewer holds by default.

        The three overrides are the door of an effect: a host layering
        something on the cube describes the frame it wants and draws it,
        instead of writing into the viewer and putting it back
        afterwards. Nothing is kept, the next frame starting from the
        fields again - which is what keeps effects from compounding, and
        above all from leaking into the camera the mouse writes to too.

        Args:
            scene: The cube to draw, where its pieces stand and what
                color they take. The current scene when left out.
            look: How the light falls on it, an ambiance being all a
                ``Look`` should be asked for. The viewer's when left out.
            camera: Where the cube is looked at from. The camera of the
                viewer when left out, and a ``replace()`` of it moves
                nothing the mouse relies on.

        """
        start = time.perf_counter()

        stage = self.require_stage()
        orientation = resolve_orientation(self.orientation)

        scene = self.scene if scene is None else scene
        look = self.look if look is None else look
        camera = self.camera if camera is None else camera

        stage.use()

        timer = stage.timer if self.debug else None

        with timer.timing() if timer else nullcontext():
            stage.renderer.draw(scene, camera, look, orientation)

            if self.show_axes:
                stage.axes.draw(camera, orientation)

        # A timer answers for the frame before this one, which is what
        # keeps the reading from waiting on the GPU. Nothing is recorded
        # on the very first frame, no result having come back yet.
        if timer and timer.elapsed:
            self.monitor.gpu.add(timer.elapsed)

        self.monitor.draw.add(time.perf_counter() - start)

    def frame(self, delta: float) -> None:
        """
        Play one frame: let time pass, and draw what it leads to.

        Neither swapping the buffers nor reading the events happens
        here: both belong to whoever owns the loop, and a toolkit does
        them on its own.

        Args:
            delta: Seconds gone by since the last frame. Measured by the
                host rather than assumed, so an animation lasts as long
                as it should whatever frame rate the machine holds.

        """
        self.advance(delta)
        self.draw()

    def profile(self) -> RenderProfile:
        """
        Tell what a frame has to draw, and what it draws into.

        The steady half of a performance report: it only moves when the
        cube, the window or the mode does. What belongs to a window -
        the refresh rate of the screen, the vsync - is left to the host
        to fill in.

        Returns:
            The profile of the picture being drawn.

        """
        stage = self.require_stage()
        info = describe(stage.context)
        instances = len(self.scene.instances)

        return RenderProfile(
            instances=instances,
            triangles=instances * self.geometry.mesh.triangle_count,
            instance_bytes=instances * INSTANCE_SIZE,
            size=stage.size,
            samples=self.look.samples,
            draw_calls=CUBE_DRAW_CALLS + int(self.show_axes),
            context=f'{ info["renderer"] } - { info["version"] }',
        )

    def screenshot(self, path: str | Path = '') -> Path:
        """
        Write what the viewer shows to a PNG file.

        Drawn again into an offscreen framebuffer rather than read back
        from the window: a multisampled framebuffer cannot be read from
        directly, and the background comes out transparent this way, as
        it does in every other image of the backend. What the window
        shows is what the image holds, the axes included when they are
        on.

        Args:
            path: Where to write the image. A stamped name in the
                temporary directory when left out.

        Returns:
            The path the image was written to.

        """
        stage = self.require_stage()
        orientation = resolve_orientation(self.orientation)
        target = OffscreenTarget.create(
            stage.context, stage.size, self.look.samples,
        )

        try:
            target.use()
            stage.renderer.draw(
                self.scene, self.camera, self.look, orientation,
            )

            if self.show_axes:
                stage.axes.draw(self.camera, orientation)

            written = write_png(
                path or screenshot_path(), target.read(), stage.size,
            )
        finally:
            target.release()

        output(f'Screenshot: { written }')

        return written

    def run(self) -> None:
        """
        Open a glfw window of its own and draw the cube until it closes.

        The convenience of the library, and the one place here knowing a
        host exists. An application owning its event loop attaches a
        stage and calls ``frame()`` instead.
        """
        from cubing_algs.display.gl.host import GlfwHost

        GlfwHost(self).run()
