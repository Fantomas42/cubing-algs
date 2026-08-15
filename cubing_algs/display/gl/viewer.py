"""
Interactive viewer of the GPU rendering backend.

A window, an event loop, and the very same painter an offscreen render
uses: nothing is drawn here that ``render()`` would not draw, the cube
simply keeps moving. The mouse orbits the camera, the wheel zooms, and
the letters of the notation turn the cube, one animated move at a time.

This is the only layer of the backend owning a loop, and it is kept as
thin as it can be: the state machine of the animation, the framing of
the camera and the building of a scene all live below, where they are
tested without any GPU. What is left here is the plumbing of the events,
and the state a viewer keeps from one frame to the next.

glfw and moderngl are imported lazily, as everywhere else in this
sub-module: nothing is pulled in until a window is asked for.
"""
import sys
import tempfile
import time
from collections import deque
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
from cubing_algs.display.gl.constants import DEFAULT_LOOK
from cubing_algs.display.gl.constants import MOVE_DURATION
from cubing_algs.display.gl.constants import ORBIT_SENSITIVITY
from cubing_algs.display.gl.constants import SCREENSHOT_NAME
from cubing_algs.display.gl.constants import VIEWER_BACKGROUND
from cubing_algs.display.gl.constants import VIEWER_HELP
from cubing_algs.display.gl.constants import VIEWER_SIZE
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.constants import ZOOM_STEP
from cubing_algs.display.gl.constants import Look
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import GLFWWindow
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.encode import write_png
from cubing_algs.display.gl.geometry import CubeGeometry
from cubing_algs.display.gl.geometry import build_cube_geometry
from cubing_algs.display.gl.renderer import OffscreenTarget
from cubing_algs.display.gl.renderer import ScenePainter
from cubing_algs.display.gl.scene import Scene
from cubing_algs.display.gl.scene import build_scene
from cubing_algs.display.gl.scene import resolve_display
from cubing_algs.exceptions import InvalidMoveError

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

    from cubing_algs.vcube import VCube

# Keys turning a face of the cube, and the ones turning a middle slice.
# glfw numbers a letter key after its uppercase ASCII code, so a key is
# already the notation of the move it plays, and no table maps the two.
FACE_KEYS = frozenset('RUFLDB')
SLICE_KEYS = frozenset('MES')

# Keys turning the whole cube, whose notation is lowercase.
ROTATION_KEYS = {'X': 'x', 'Y': 'y', 'Z': 'z'}


def key_notation(
        key: int,
        *,
        prime: bool = False,
        double: bool = False,
        wide: bool = False,
) -> str:
    """
    Read the move a key stands for, modifiers included.

    Args:
        key: The glfw code of the key.
        prime: Whether the move is turned the other way.
        double: Whether the move is a half turn. Wins over ``prime``.
        wide: Whether a face turn takes the layer behind it along.
            Meaningless on a slice or on a rotation, and ignored there.

    Returns:
        The notation of the move, empty when the key plays none.

    """
    if key < 0:
        return ''

    letter = chr(key)

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
    The window a viewer draws into, and what it owns on the GPU.

    Held apart from the viewer so that the cube, the camera and the
    animation all exist before any window does, and outlive it: only
    this handful of fields needs a display server, which is what keeps
    the rest of the viewer testable without one.
    """

    window: GLFWWindow
    context: 'moderngl.Context'
    painter: ScenePainter
    size: tuple[int, int]

    @classmethod
    def open(
            cls,
            size: tuple[int, int],
            geometry: CubeGeometry,
            look: Look = DEFAULT_LOOK,
            title: str = WINDOW_TITLE,
    ) -> Self:
        """
        Open a window and build everything drawing into it takes.

        Args:
            size: Width and height of the window, in pixels.
            geometry: The mesh of a cubie and the cubies to place it on.
            look: How the light falls on the cube, antialiasing
                included: a window framebuffer is multisampled too.
            title: Title of the window.

        Returns:
            A stage ready to be drawn into.

        """
        window = create_window(size, title, samples=look.samples)
        context = create_window_context()

        return cls(
            window=window,
            context=context,
            painter=ScenePainter.create(context, geometry, look),
            size=size,
        )

    def use(
            self,
            background: tuple[float, float, float, float] = VIEWER_BACKGROUND,
    ) -> None:
        """
        Make the window framebuffer current and clear it.

        The viewport is set on every frame rather than on resize alone:
        moderngl reads the size of the screen framebuffer once, when the
        context is created, and would otherwise draw into the window the
        user opened rather than into the one they are looking at.

        Args:
            background: Color the framebuffer is cleared with.

        """
        screen = self.context.screen

        screen.use()
        self.context.viewport = (0, 0, *self.size)
        screen.clear(color=background)

    def close(self) -> None:
        """Give the window and every GPU resource of the stage back."""
        self.painter.release()
        self.context.release()
        destroy_window(self.window)


@dataclass(slots=True)
class Viewer:
    """
    A cube in a window, turning under the mouse and the keyboard.

    Built with the options of ``render()``, so that what a window shows
    and what a PNG holds are the same picture: same palette, same mode,
    same mask, same framing. The mode is resolved once, when the viewer
    is built, exactly as an animation does it: it may reorient the cube,
    and reading that orientation again after every move would make the
    cube jump around.

    Nothing is opened until ``run()`` is called, and everything it opens
    is given back when it returns, however it returns.
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

    geometry: CubeGeometry = field(init=False)
    camera: OrbitCamera = field(init=False)
    scene: Scene = field(init=False)
    origin: 'VCube' = field(init=False)
    stage: Stage | None = field(init=False, default=None)
    animation: Animation | None = field(init=False, default=None)
    pending: deque[str] = field(init=False, default_factory=deque[str])
    dragging: bool = field(init=False, default=False)
    cursor: tuple[float, float] = field(init=False, default=(0.0, 0.0))
    clock: float = field(init=False, default=0.0)

    def __post_init__(self) -> None:
        """Settle what is drawn, and how it is framed, once and for all."""
        self.cube, self.mask = resolve_display(
            self.cube.copy(full=True), self.palette,
            mode=self.mode, mask=self.mask,
        )

        self.origin = self.cube.copy(full=True)
        self.geometry = build_cube_geometry(self.cube.size)
        self.scene = self.build_scene()

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

    def build_scene(self) -> Scene:
        """
        Build the scene of the cube as it stands right now.

        Returns:
            The scene of the current state of the cube.

        """
        return build_scene(
            self.cube, self.palette, self.geometry, mask=self.mask,
        )

    def require_stage(self) -> Stage:
        """
        Hand the open window over.

        Returns:
            The stage the viewer draws into.

        Raises:
            GLContextError: When no window is open.

        """
        if self.stage is None:
            msg = 'The viewer has no window open'
            raise GLContextError(msg)

        return self.stage

    def push(self, notation: str) -> bool:
        """
        Queue a move to be played, when the cube can take it.

        A cube refuses what its size makes meaningless, an ``M`` on a
        2x2x2 among others. Such a move is dropped here rather than in
        the middle of the loop, where it would bring the window down.

        Args:
            notation: The move to play, empty for none.

        Returns:
            True when the move was queued.

        """
        if not notation:
            return False

        try:
            self.cube.copy().rotate(notation)
        except InvalidMoveError:
            return False

        self.pending.append(notation)

        return True

    def advance(self, delta: float) -> Scene:
        """
        Let some time pass, and build the scene it leads to.

        Args:
            delta: Seconds gone by since the last call.

        Returns:
            The scene to draw right now.

        """
        if self.animation is None and self.pending:
            self.animation = Animation(
                self.cube, self.pending.popleft(),
                palette=self.palette, mask=self.mask, duration=self.duration,
            )

        if self.animation is not None:
            self.scene = self.animation.advance(delta)

            if self.animation.finished:
                self.cube = self.animation.cube
                self.animation = None

        return self.scene

    def reset_cube(self) -> None:
        """Put the cube back to the state the viewer opened on."""
        self.cube = self.origin.copy(full=True)
        self.animation = None
        self.pending.clear()
        self.scene = self.build_scene()

    def reset_camera(self) -> None:
        """Frame the cube again, as it was framed when the window opened."""
        self.camera = OrbitCamera.from_rotation(
            self.rotation, self.distance,
            self.geometry.radius, self.camera.aspect,
        )

    def resize(self, size: tuple[int, int]) -> None:
        """
        Take the window to a new size.

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

    def screenshot(self, path: str | Path = '') -> Path:
        """
        Write what the window shows to a PNG file.

        Drawn again into an offscreen framebuffer rather than read back
        from the window: a multisampled framebuffer cannot be read from
        directly, and the background comes out transparent this way, as
        it does in every other image of the backend.

        Args:
            path: Where to write the image. A stamped name in the
                temporary directory when left out.

        Returns:
            The path the image was written to.

        """
        stage = self.require_stage()
        target = OffscreenTarget.create(
            stage.context, stage.size, self.look.samples,
        )

        try:
            target.use()
            stage.painter.draw(self.scene, self.camera, self.look)

            written = write_png(
                path or screenshot_path(), target.read(), stage.size,
            )
        finally:
            target.release()

        output(f'Screenshot: { written }')

        return written

    def on_key(
            self,
            window: GLFWWindow,
            key: int,
            _scancode: int,
            action: int,
            mods: int,
    ) -> None:
        """
        React to a key being pressed, or held down.

        Args:
            window: The window the key was pressed in.
            key: The glfw code of the key.
            _scancode: Platform specific code of the key, unused.
            action: Whether the key was pressed, released or repeated.
            mods: The modifier keys held down with it.

        """
        import glfw

        if action == glfw.RELEASE:
            return

        if key in {glfw.KEY_ESCAPE, glfw.KEY_Q}:
            glfw.set_window_should_close(window, glfw.TRUE)
        elif key == glfw.KEY_SPACE:
            self.reset_camera()
        elif key == glfw.KEY_BACKSPACE:
            self.reset_cube()
        elif key == glfw.KEY_F12:
            self.screenshot()
        else:
            self.push(
                key_notation(
                    key,
                    prime=bool(mods & glfw.MOD_SHIFT),
                    double=bool(mods & glfw.MOD_CONTROL),
                    wide=bool(mods & glfw.MOD_ALT),
                ),
            )

    def on_mouse_button(
            self,
            window: GLFWWindow,
            button: int,
            action: int,
            _mods: int,
    ) -> None:
        """
        Start or stop dragging the cube around.

        Args:
            window: The window the button was pressed in.
            button: The glfw code of the button.
            action: Whether the button was pressed or released.
            _mods: The modifier keys held down with it, unused.

        """
        import glfw

        if button != glfw.MOUSE_BUTTON_LEFT:
            return

        self.dragging = action == glfw.PRESS
        self.cursor = glfw.get_cursor_pos(window)

    def on_cursor(self, _window: GLFWWindow, x: float, y: float) -> None:
        """
        Follow the mouse, and orbit the camera while it is dragged.

        The cube turns the way the mouse goes: dragging to the right
        brings the left face in, dragging down brings the top in.

        Args:
            _window: The window the mouse moved over, unused.
            x: Where the cursor stands, in pixels from the left.
            y: Where the cursor stands, in pixels from the top.

        """
        previous_x, previous_y = self.cursor
        self.cursor = (x, y)

        if not self.dragging:
            return

        self.camera.orbit(
            (previous_x - x) * ORBIT_SENSITIVITY,
            (y - previous_y) * ORBIT_SENSITIVITY,
        )

    def on_scroll(self, _window: GLFWWindow, _x: float, y: float) -> None:
        """
        Move the camera closer to the cube, or further away.

        Args:
            _window: The window the wheel was turned over, unused.
            _x: Horizontal scrolling, unused.
            y: Notches the wheel was turned by, forward being positive.

        """
        self.camera.zoom(ZOOM_STEP ** y)

    def on_resize(
            self,
            _window: GLFWWindow,
            width: int,
            height: int,
    ) -> None:
        """
        Follow the window as it is resized.

        Args:
            _window: The window that was resized, unused.
            width: New width of its framebuffer, in pixels.
            height: New height of its framebuffer, in pixels.

        """
        self.resize((width, height))

    def open(self) -> Stage:
        """
        Open the window and listen to what happens in it.

        Returns:
            The stage the viewer draws into.

        """
        import glfw

        stage = Stage.open(self.window_size, self.geometry, self.look)
        self.stage = stage

        glfw.swap_interval(1)
        glfw.set_key_callback(stage.window, self.on_key)
        glfw.set_mouse_button_callback(stage.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(stage.window, self.on_cursor)
        glfw.set_scroll_callback(stage.window, self.on_scroll)
        glfw.set_framebuffer_size_callback(stage.window, self.on_resize)

        self.resize(glfw.get_framebuffer_size(stage.window))
        self.clock = glfw.get_time()

        return stage

    def close(self) -> None:
        """Close the window, if one is open, and forget about it."""
        if self.stage is None:
            return

        self.stage.close()
        self.stage = None

    def draw(self) -> None:
        """Draw the current scene into the window."""
        stage = self.require_stage()

        stage.use()
        stage.painter.draw(self.scene, self.camera, self.look)

    def tick(self) -> None:
        """
        Play one frame: let time pass, draw it, and read the events.

        The elapsed time is measured rather than assumed, so an
        animation lasts as long as it should whatever the frame rate the
        machine holds.
        """
        import glfw

        stage = self.require_stage()

        now = glfw.get_time()
        self.advance(now - self.clock)
        self.clock = now

        self.draw()

        glfw.swap_buffers(stage.window)
        glfw.poll_events()

    def run(self) -> None:
        """
        Open the window and draw the cube until it is closed.

        The window is given back however the loop ends, an interruption
        from the keyboard included.
        """
        import glfw

        stage = self.open()
        output(VIEWER_HELP)

        try:
            while not glfw.window_should_close(stage.window):
                self.tick()
        finally:
            self.close()
