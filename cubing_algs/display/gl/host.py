"""
The glfw host of the interactive viewer.

A ``Viewer`` holds a cube, a camera and an animation, and knows how to
draw one frame; it owns neither a window nor a loop. This module is what
gives it both under glfw, and it is a module of its own for one reason:
``viewer.py`` names glfw nowhere, so another host — a ``QOpenGLWidget``,
a pygame surface, anything already owning an event loop — plugs the very
same viewer into it by writing the same handful of methods.

What a host owes a viewer is short: attach a ``Stage`` built on a current
context, call ``frame()`` once per frame, and translate its own input
into ``press()``, ``drag()``, ``scroll()`` and ``resize()``.

glfw is imported lazily, and never before ``create_window()``, the one
place naming the extra a missing glfw asks for.
"""
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

from cubing_algs.display.gl.constants import FPS_INTERVAL
from cubing_algs.display.gl.constants import VIEWER_HELP
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.context import GLFWWindow
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.viewer import Stage
from cubing_algs.display.gl.viewer import Viewer
from cubing_algs.display.gl.viewer import output

if TYPE_CHECKING:  # pragma: no cover
    import moderngl


def key_letter(key: int) -> str:
    """
    Read the letter a glfw key code stands for.

    glfw numbers letter keys on their uppercase ASCII code, so the
    letter it gives back *is* the notation of the move, and no table
    maps the two. The key glfw could not name is numbered -1, and names
    no letter at all.

    Args:
        key: The glfw code of the key.

    Returns:
        The letter of the key, empty when it names none.

    """
    if key < 0:
        return ''

    return chr(key)


def fps_title(frames: int, elapsed: float, title: str = WINDOW_TITLE) -> str:
    """
    Write the frame rate of a window in its own title.

    Args:
        frames: Frames drawn over the period.
        elapsed: How long that period lasted, in seconds.
        title: Title of the window, kept ahead of the rate.

    Returns:
        The title to give the window.

    """
    rate = frames / elapsed

    return f'{ title } — {rate:.0f} fps'


@dataclass(slots=True)
class GlfwHost:
    """
    A window, an event loop, and a viewer drawing into it.

    Everything glfw of the backend lives here: the window, the timing of
    the frames, the frame rate in the title, and the translation of the
    keyboard and the mouse into the neutral vocabulary the viewer
    speaks.

    Nothing is opened until ``run()`` — or ``open()`` — is called, and
    everything it opened is given back when it returns, however it
    returns.
    """

    viewer: Viewer
    title: str = WINDOW_TITLE

    window: GLFWWindow = field(init=False, default=None)
    context: 'moderngl.Context | None' = field(init=False, default=None)
    frames: int = field(init=False, default=0)
    clock: float = field(init=False, default=0.0)
    dragging: bool = field(init=False, default=False)
    cursor: tuple[float, float] = field(init=False, default=(0.0, 0.0))

    def open(self) -> Stage:
        """
        Open the window, hand it to the viewer, and listen to it.

        Returns:
            The stage the viewer now draws into.

        """
        viewer = self.viewer

        # The window is opened before glfw is reached for, and not
        # after: create_window() is the one place naming the extra a
        # missing glfw asks for, and an import raising first would
        # replace that with a bare ModuleNotFoundError.
        self.window = create_window(
            viewer.window_size, self.title, samples=viewer.look.samples,
        )
        context = create_window_context()
        self.context = context

        import glfw

        # The size asked for and the one truly given apart on a scaled
        # display, and the cube is framed on what there is to draw into.
        width, height = glfw.get_framebuffer_size(self.window)
        stage = Stage.attach(context, viewer.geometry, (width, height))
        viewer.attach(stage)

        glfw.swap_interval(1)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_cursor)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_framebuffer_size_callback(self.window, self.on_resize)

        self.clock = glfw.get_time()

        return stage

    def close(self) -> None:
        """
        Close the window, if one is open, and forget about it.

        The context stands for the pair: ``open()`` sets both or
        neither, so testing it alone leaves no unreachable branch behind.
        """
        context = self.context

        if context is None:
            return

        self.viewer.detach()

        context.release()
        self.context = None

        destroy_window(self.window)
        self.window = None

    def count_frame(self, now: float) -> None:
        """
        Count a drawn frame, and show the rate it holds once a second.

        The rate goes to the title of the window: telling a slowdown
        from a steady sixty is all that is asked of it, and drawing a
        text in the scene would take a font and a program of its own.

        Args:
            now: The moment the frame was drawn, in seconds.

        """
        import glfw

        self.frames += 1
        elapsed = now - self.clock

        if elapsed < FPS_INTERVAL:
            return

        glfw.set_window_title(
            self.window,
            fps_title(self.frames, elapsed, self.title),
        )

        self.frames = 0
        self.clock = now

    def reset_title(self, now: float) -> None:
        """
        Put the plain title back, and start counting frames afresh.

        Called whenever the rate is turned on or off: turned on, the
        first period starts now instead of covering all the time the
        counter spent asleep; turned off, the last rate leaves the title.

        Args:
            now: The moment the new period starts, in seconds.

        """
        import glfw

        glfw.set_window_title(self.window, self.title)

        self.frames = 0
        self.clock = now

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

        What belongs to the window is answered here — closing it, the
        frame rate in its title — and everything else is handed to the
        viewer in its own vocabulary.

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

        viewer = self.viewer

        if key in {glfw.KEY_ESCAPE, glfw.KEY_Q}:
            glfw.set_window_should_close(window, glfw.TRUE)
        elif key == glfw.KEY_SPACE:
            viewer.reset_camera()
        elif key == glfw.KEY_BACKSPACE:
            viewer.reset_cube()
        elif key == glfw.KEY_F2:
            viewer.show_axes = not viewer.show_axes
        elif key == glfw.KEY_F3:
            viewer.show_fps = not viewer.show_fps
            self.reset_title(self.clock)
        elif key == glfw.KEY_F12:
            viewer.screenshot()
        else:
            viewer.press(
                key_letter(key),
                prime=bool(mods & glfw.MOD_SHIFT),
                double=bool(mods & glfw.MOD_CONTROL),
                wide=bool(mods & glfw.MOD_ALT),
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

        Args:
            _window: The window the mouse moved over, unused.
            x: Where the cursor stands, in pixels from the left.
            y: Where the cursor stands, in pixels from the top.

        """
        previous_x, previous_y = self.cursor
        self.cursor = (x, y)

        if not self.dragging:
            return

        self.viewer.drag(x - previous_x, y - previous_y)

    def on_scroll(self, _window: GLFWWindow, _x: float, y: float) -> None:
        """
        Move the camera closer to the cube, or further away.

        Args:
            _window: The window the wheel was turned over, unused.
            _x: Horizontal scrolling, unused.
            y: Notches the wheel was turned by, forward being positive.

        """
        self.viewer.scroll(y)

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
        self.viewer.resize((width, height))

    def tick(self) -> None:
        """
        Play one frame: let time pass, draw it, and read the events.

        The elapsed time is measured rather than assumed, so an
        animation lasts as long as it should whatever the frame rate the
        machine holds.
        """
        import glfw

        now = glfw.get_time()
        self.viewer.frame(now - self.clock)
        self.clock = now

        glfw.swap_buffers(self.window)
        glfw.poll_events()

        if self.viewer.show_fps:
            self.count_frame(now)

    def run(self) -> None:
        """
        Open the window and draw the cube until it is closed.

        The window is given back however the loop ends, an interruption
        from the keyboard included.
        """
        self.open()

        import glfw

        output(VIEWER_HELP)

        try:
            while not glfw.window_should_close(self.window):
                self.tick()
        finally:
            self.close()
