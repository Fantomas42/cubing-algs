# ruff: noqa: PLC0415
"""
Play an algorithm in a window with a transparent background.

Written as a **host**, and that is the whole point of it. The backend
owns the cube, the camera, the animation and the drawing; this file owns
only what makes this window special — a transparent visual, no
decoration, always on top — and reaches everything else through
``Stage.attach()``, ``viewer.frame()`` and ``viewer.drag()``. It is the
second host of the backend, next to ``GlfwHost``, and a Qt widget would
call exactly the same four methods.

On this driver a transparent visual and a multisampled window
framebuffer are mutually exclusive: asking for both gets the
transparency refused. The cube is therefore drawn into an offscreen
multisampled target and copied to the screen — ``stage.target`` is the
one field that switches between the two. ``--no-msaa`` draws straight
into the window instead, aliased but with nothing in between.

What the cube shows is said in the vocabulary of the command line:
``--setup``, ``--size``, ``--orientation``, ``--mode``, ``--mask`` and
``--palette`` mean here exactly what they mean in
``python -m cubing_algs apply``, so that a window and a PNG asked for the
same way hold the same picture. The orientation is absorbed on the
``VCube`` side, before the algorithm is played, so that ``R`` turns the
face on the right of whoever holds the cube.

glfw is imported inside the methods reaching for it, and never at the
top of the file: pyGLFW picks the library it loads at import time, and
``cubing_algs.display.gl.context`` settles that choice as it is itself
imported. Importing the backend first is therefore all a host has to do.

A window with no decoration has no title bar to grab, so the left button
drags the *window* across the screen — X11 lets an application place
itself, which is what ``select_glfw_variant()`` gives us here, and what a
native Wayland would silently ignore. The right button orbits the cube,
and the wheel zooms.
"""
import argparse
import math
import sys
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.display.gl import Stage
from cubing_algs.display.gl import Viewer
from cubing_algs.display.gl.constants import GLFW_MISSING
from cubing_algs.display.gl.constants import VIEWER_BACKGROUND
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import GLFWWindow
from cubing_algs.display.gl.context import check_glfw_platform
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.context import has_glfw
from cubing_algs.display.gl.renderer import OffscreenTarget
from cubing_algs.display.mode import MODE_CONFIGS
from cubing_algs.display.palettes import PALETTES
from cubing_algs.exceptions import CubingAlgsError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

if TYPE_CHECKING:  # pragma: no cover
    import moderngl


# The background of a window whose compositor is asked to let the desktop
# through, against the opaque grey of the viewer.
TRANSPARENT = (0.0, 0.0, 0.0, 0.0)

WINDOW_TITLE = 'transparent cube'

# What the left and the right button do while held down.
DRAG_MOVE = 'move'
DRAG_ORBIT = 'orbit'

FULL_TURN = 2 * math.pi

DEFAULT_MOVES = "R U R' U'"
DEFAULT_CUBE_SIZE = 3
DEFAULT_WINDOW_SIZE = 400
DEFAULT_SPEED = 0.35
DEFAULT_SPIN = 0.25

CONTROLS = """\
  left drag    carry the window across the screen
  right drag   orbit the cube
  wheel        zoom in and out
  escape, Q    close the window\
"""

EPILOG = f"""\
examples:
  %(prog)s "R U R' U'"
  %(prog)s "R U R' U'" --size 5 --window 700
  %(prog)s "F R U R' U' F'" --setup "F U R U' R' F'" --mode oll
  %(prog)s "R U R' U' R' F R2 U' R' U' R U R' F'" --mode pll
  %(prog)s "M2 E2 S2" --opaque --palette rgb

controls:
{ CONTROLS }
"""


def open_window(
        size: tuple[int, int],
        samples: int,
        *,
        transparent: bool,
) -> GLFWWindow:
    """
    Open a window, asking for a transparent framebuffer.

    The three hints ``create_window()`` does not offer are the reason
    this demo opens a window of its own rather than driving a
    ``GlfwHost``. A compositor is free to refuse any of them, hence the
    read-back reported on standard output.

    Args:
        size: Width and height of the window, in pixels.
        samples: Samples of the window framebuffer. Zero draws without
            any antialiasing, which a transparent visual imposes here.
        transparent: Whether the desktop is asked to show through, the
            window then losing its decoration and floating on top.

    Returns:
        The glfw window handle, made current.

    Raises:
        GLContextError: If glfw is missing, cannot start, or cannot open
            the window.

    """
    if not has_glfw():
        raise GLContextError(GLFW_MISSING)

    import glfw

    if not glfw.init():
        msg = 'glfw could not be initialized: no display server?'
        raise GLContextError(msg)

    check_glfw_platform()

    width, height = size

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    glfw.window_hint(glfw.SAMPLES, samples)

    if transparent:
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
        glfw.window_hint(glfw.DECORATED, glfw.FALSE)
        glfw.window_hint(glfw.FLOATING, glfw.TRUE)

    window = glfw.create_window(width, height, WINDOW_TITLE, None, None)
    if not window:
        glfw.terminate()
        msg = 'glfw could not create the window'
        raise GLContextError(msg)

    glfw.make_context_current(window)

    granted = glfw.get_window_attrib(window, glfw.TRANSPARENT_FRAMEBUFFER)
    print(
        f'transparent framebuffer asked: { transparent }, '
        f'granted: { bool(granted) }',
    )

    return window


@dataclass
class TransparentWindow:
    """
    A window of its own, driving a viewer through the host contract.

    Nothing of the cube is held here: the viewer owns it, and this host
    owes it four things only — a ``Stage`` built on a current context, a
    ``frame(delta)`` per frame, its own input translated into the neutral
    vocabulary, and a ``detach()`` before the context goes.

    What it does hold is what belongs to a window: the glfw handle, the
    context it opened, the offscreen target a transparent visual imposes,
    and which button is being dragged.
    """

    viewer: Viewer
    moves: str
    spin: float = DEFAULT_SPIN
    transparent: bool = True
    msaa: bool = True

    window: GLFWWindow = field(init=False, default=None)
    context: 'moderngl.Context | None' = field(init=False, default=None)
    target: OffscreenTarget | None = field(init=False, default=None)
    dragging: str = field(init=False, default='')
    anchor: tuple[float, float] = field(init=False, default=(0.0, 0.0))
    clock: float = field(init=False, default=0.0)

    @property
    def offscreen(self) -> bool:
        """
        Tell whether the cube is drawn aside and copied to the window.

        Returns:
            True when the frame goes through a multisampled target,
            which a transparent visual leaves as the only way to
            antialias it.

        """
        return self.transparent and self.msaa

    def open(self) -> Stage:
        """
        Open the window, hand it to the viewer, and listen to it.

        Returns:
            The stage the viewer now draws into.

        """
        viewer = self.viewer

        # A transparent visual comes without multisampling here, so the
        # window is asked for none and the antialiasing happens offscreen.
        self.window = open_window(
            viewer.window_size,
            0 if self.transparent else viewer.look.samples,
            transparent=self.transparent,
        )
        context = create_window_context()
        self.context = context

        import glfw

        # Everything the backend needs to draw here, on a context this
        # file opened and keeps: the stage releases its renderers, never
        # that.
        width, height = glfw.get_framebuffer_size(self.window)
        stage = Stage.attach(context, viewer.geometry, (width, height))
        stage.background = (
            TRANSPARENT if self.transparent else VIEWER_BACKGROUND
        )
        viewer.attach(stage)

        glfw.swap_interval(1)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_mouse_button_callback(self.window, self.on_button)
        glfw.set_cursor_pos_callback(self.window, self.on_cursor)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_framebuffer_size_callback(self.window, self.on_resize)

        self.clock = glfw.get_time()

        return stage

    def close(self) -> None:
        """
        Give back the target, the stage, the context and the window.

        The context stands for the pair: ``open()`` sets both or neither,
        so testing it alone leaves no unreachable branch behind.
        """
        context = self.context

        if context is None:
            return

        self.viewer.detach()

        if self.target is not None:
            self.target.release()
            self.target = None

        context.release()
        self.context = None

        destroy_window(self.window)
        self.window = None

    def on_key(
            self,
            _window: GLFWWindow,
            key: int,
            _scancode: int,
            action: int,
            _mods: int,
    ) -> None:
        """
        Close the window on escape, and leave the rest alone.

        The algorithm plays on its own here, so the keyboard of the
        viewer is deliberately not wired: what this demo shows is a
        window, not a cube being turned by hand.

        Args:
            _window: The window the key was pressed in, unused: the host
                closes the one it opened.
            key: The glfw code of the key.
            _scancode: Platform specific code of the key, unused.
            action: Whether the key was pressed, released or repeated.
            _mods: The modifier keys held down with it, unused.

        """
        import glfw

        if action == glfw.PRESS and key in {glfw.KEY_ESCAPE, glfw.KEY_Q}:
            glfw.set_window_should_close(self.window, glfw.TRUE)

    def on_button(
            self,
            window: GLFWWindow,
            button: int,
            action: int,
            _mods: int,
    ) -> None:
        """
        Take hold of the window, or of the cube, until the button goes.

        The anchor is the cursor at the moment of the click, held still
        while the window is carried and followed while the cube orbits.

        Args:
            window: The window the button was pressed in.
            button: The glfw code of the button.
            action: Whether the button was pressed or released.
            _mods: The modifier keys held down with it, unused.

        """
        import glfw

        if button not in {glfw.MOUSE_BUTTON_LEFT, glfw.MOUSE_BUTTON_RIGHT}:
            return

        if action != glfw.PRESS:
            self.dragging = ''
            return

        self.dragging = (
            DRAG_MOVE if button == glfw.MOUSE_BUTTON_LEFT else DRAG_ORBIT
        )
        self.anchor = glfw.get_cursor_pos(window)

    def carry(self, window: GLFWWindow, x: float, y: float) -> None:
        """
        Move the window by what the cursor gained on its anchor.

        The cursor is reported inside the window, so moving the window by
        that gain puts the cursor back on its anchor: the offset is
        measured afresh at every event, and nothing drifts. Accumulating
        deltas from the previous position would count the movement twice.

        Args:
            window: The window being carried.
            x: Where the cursor stands, in pixels from the left.
            y: Where the cursor stands, in pixels from the top.

        """
        import glfw

        anchor_x, anchor_y = self.anchor
        window_x, window_y = glfw.get_window_pos(window)

        glfw.set_window_pos(
            window,
            int(window_x + x - anchor_x),
            int(window_y + y - anchor_y),
        )

    def on_cursor(self, window: GLFWWindow, x: float, y: float) -> None:
        """
        Carry the window, or orbit the cube, as the mouse moves.

        Args:
            window: The window the mouse moved over.
            x: Where the cursor stands, in pixels from the left.
            y: Where the cursor stands, in pixels from the top.

        """
        if self.dragging == DRAG_MOVE:
            self.carry(window, x, y)
        elif self.dragging == DRAG_ORBIT:
            anchor_x, anchor_y = self.anchor
            self.viewer.drag(x - anchor_x, y - anchor_y)
            self.anchor = (x, y)

    def on_scroll(self, _window: GLFWWindow, _x: float, y: float) -> None:
        """
        Move the camera closer to the cube, or further away.

        Args:
            _window: The window the wheel was turned over, unused.
            _x: Horizontal scrolling, unused.
            y: Notches the wheel was turned by, forward being positive.

        """
        self.viewer.scroll(y)

    def on_resize(self, _window: GLFWWindow, width: int, height: int) -> None:
        """
        Follow the window as it is resized.

        Args:
            _window: The window that was resized, unused.
            width: New width of its framebuffer, in pixels.
            height: New height of its framebuffer, in pixels.

        """
        self.viewer.resize((width, height))

    def replay(self) -> None:
        """
        Push the algorithm again once the cube has finished playing it.

        The viewer picks the cube up where the last run left it, so the
        algorithm loops on the state it leads to rather than on a cube
        put back together behind the scenes.
        """
        viewer = self.viewer

        if viewer.animation is None and not viewer.pending:
            viewer.push(self.moves)

    def orbit(self, delta: float) -> None:
        """
        Turn the camera around the cube, unless the mouse is holding it.

        Args:
            delta: Seconds gone by since the last frame.

        """
        if not self.spin or self.dragging == DRAG_ORBIT:
            return

        camera = self.viewer.camera
        camera.yaw = (camera.yaw + self.spin * delta) % FULL_TURN

    def refresh_target(self) -> None:
        """
        Keep the offscreen target the size of the window it is copied to.

        The whole offscreen detour, in one field: the stage draws into
        the multisampled target instead of the window, and ``resolve()``
        brings it back, alpha and all.
        """
        if not self.offscreen:
            return

        stage = self.viewer.require_stage()

        if self.target is not None and self.target.size == stage.size:
            return

        if self.target is not None:
            self.target.release()

        self.target = OffscreenTarget.create(
            stage.context, stage.size, self.viewer.look.samples,
        )
        stage.target = self.target.framebuffer

    def resolve(self) -> None:
        """
        Copy the offscreen frame to the window, samples resolved first.

        Nothing to do when the cube was drawn into the window itself: no
        target was ever built, and the frame is already where it belongs.
        """
        target = self.target

        if target is None:
            return

        context = self.viewer.require_stage().context

        context.copy_framebuffer(target.resolved, target.framebuffer)
        context.copy_framebuffer(context.screen, target.resolved)

    def frame(self, delta: float) -> None:
        """
        Draw one frame, and bring it to the window.

        Args:
            delta: Seconds gone by since the last frame.

        """
        self.replay()
        self.orbit(delta)
        self.refresh_target()

        self.viewer.frame(delta)

        self.resolve()

    def tick(self) -> None:
        """
        Play one frame: let time pass, draw it, and read the events.

        The elapsed time is measured rather than assumed, so a move lasts
        as long as it should whatever frame rate the machine holds.
        """
        import glfw

        now = glfw.get_time()
        self.frame(now - self.clock)
        self.clock = now

        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def run(self) -> None:
        """
        Open the window and play the algorithm until it is closed.

        The window is given back however the loop ends, an interruption
        from the keyboard included.
        """
        self.open()

        import glfw

        print(CONTROLS)

        try:
            while not glfw.window_should_close(self.window):
                self.tick()
        finally:
            self.close()


def build_cube(args: argparse.Namespace) -> VCube:
    """
    Build the cube the algorithm is played on.

    The cube is turned the way ``--orientation`` says it is held before
    ``--setup`` is played on it, exactly as the command line does it, so
    that the setup is made from there and the algorithm after it.

    Args:
        args: The parsed command line, holding the size, the orientation
            and the setup moves.

    Returns:
        The cube, held and set up, ready for the algorithm.

    """
    cube = VCube(size=args.size)

    if args.orientation:
        cube = cube.oriented_copy(args.orientation, full=True)

    if args.setup:
        cube.rotate(parse_moves(args.setup, trust_input=False))

    return cube


def parse_arguments() -> argparse.Namespace:
    """
    Read what the demo is asked to show.

    Returns:
        The options the demo was called with.

    """
    parser = argparse.ArgumentParser(
        description=__doc__.split('\n\n')[0] if __doc__ else '',
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'moves',
        nargs='?',
        default=DEFAULT_MOVES,
        help=f'Algorithm to play, looping (default: "{ DEFAULT_MOVES }")',
    )
    parser.add_argument(
        '--setup',
        default='',
        help='Moves applied before the algorithm',
    )
    parser.add_argument(
        '--size',
        type=int,
        default=DEFAULT_CUBE_SIZE,
        help=f'Cube size (default: { DEFAULT_CUBE_SIZE })',
    )
    parser.add_argument(
        '--orientation',
        default='',
        choices=sorted(ORIENTATION_FACE_MOVES),
        metavar='FACES',
        help='Orientation the cube is held in, e.g. DF',
    )
    parser.add_argument(
        '--mode',
        default='',
        choices=sorted(MODE_CONFIGS),
        metavar='MODE',
        help='Display mode, e.g. oll, pll, f2l',
    )
    parser.add_argument(
        '--mask',
        default='',
        help='Display mask, one code per facelet',
    )
    parser.add_argument(
        '--palette',
        default='',
        choices=sorted(PALETTES),
        metavar='NAME',
        help='Color palette the cube is painted with, e.g. rgb',
    )
    parser.add_argument(
        '--window',
        type=int,
        default=DEFAULT_WINDOW_SIZE,
        metavar='PIXELS',
        help=f'Width and height of the window '
             f'(default: { DEFAULT_WINDOW_SIZE })',
    )
    parser.add_argument(
        '--speed',
        type=float,
        default=DEFAULT_SPEED,
        metavar='SECONDS',
        help=f'Seconds a quarter turn takes (default: { DEFAULT_SPEED })',
    )
    parser.add_argument(
        '--spin',
        type=float,
        default=DEFAULT_SPIN,
        metavar='RADIANS',
        help=f'Radians per second of automatic orbit, zero to hold the '
             f'cube still (default: { DEFAULT_SPIN })',
    )
    parser.add_argument(
        '--opaque',
        action='store_true',
        help='Keep the grey background of the viewer',
    )
    parser.add_argument(
        '--no-msaa',
        action='store_true',
        help='Draw into the window, aliased but with nothing in between',
    )

    return parser.parse_args()


def main() -> int:
    """
    Open the window, and play the algorithm in it until it closes.

    Returns:
        Process exit code.

    Raises:
        InvalidMoveError: If the cube asked for cannot play the
            algorithm, an ``M`` on a 2x2x2 among others.

    """
    args = parse_arguments()

    algo = parse_moves(args.moves, trust_input=False)

    viewer = Viewer(
        build_cube(args),
        mode=args.mode,
        mask=args.mask,
        palette=args.palette,
        window_size=(args.window, args.window),
        duration=args.speed,
    )

    if not viewer.push(str(algo)):
        message = f'a { args.size }x{ args.size } cannot play { algo }'
        raise InvalidMoveError(message)

    TransparentWindow(
        viewer,
        str(algo),
        spin=args.spin,
        transparent=not args.opaque,
        msaa=not args.no_msaa,
    ).run()

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except CubingAlgsError as error:
        sys.exit(f'Error: { error }')
