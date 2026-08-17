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
from dataclasses import replace
from typing import TYPE_CHECKING

from cubing_algs.display.gl.constants import VIEWER_HELP
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.context import GLFWWindow
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.metrics import RenderProfile
from cubing_algs.display.gl.metrics import debug_report
from cubing_algs.display.gl.metrics import debug_title
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


def screen_refresh() -> float:
    """
    Read how fast the screen the window opens on refreshes.

    This is the ceiling a vsynced frame rate can never pass, and it is
    therefore the budget a frame is given: on a hundred hertz screen a
    frame has ten milliseconds, whatever a counter shows.

    Returns:
        The refresh rate in hertz, zero when no screen says.

    """
    import glfw

    monitor = glfw.get_primary_monitor()

    if not monitor:
        return 0.0

    mode = glfw.get_video_mode(monitor)

    if not mode:
        return 0.0

    return float(mode.refresh_rate)


@dataclass
class GlfwHost:
    """
    A window, an event loop, and a viewer drawing into it.

    Everything glfw of the backend lives here: the window, the timing of
    the frames, the performance written in the title, the vsync, and the
    translation of the keyboard and the mouse into the neutral
    vocabulary the viewer speaks.

    Nothing is opened until ``run()`` — or ``open()`` — is called, and
    everything it opened is given back when it returns, however it
    returns.

    **Written to be subclassed**, which is the one reason it carries no
    ``slots=True`` where the rest of the backend does: a plain
    ``@dataclass`` subclass of a slotted dataclass generates an
    ``__init__`` of its own and leaves every inherited ``init=False``
    default unset, and a ``slots=True`` one rebuilds the class under its
    methods, breaking every zero-argument ``super()`` in them. A host is
    built once per process, so the memory a slot saves buys nothing that
    the extension point costs.

    A consumer layering effects on the cube overrides ``frame()``, and
    inherits the loop, the timing and the counter untouched.
    """

    viewer: Viewer
    title: str = WINDOW_TITLE
    vsync: bool = True

    window: GLFWWindow = field(init=False, default=None)
    context: 'moderngl.Context | None' = field(init=False, default=None)
    clock: float = field(init=False, default=0.0)
    refresh: float = field(init=False, default=0.0)
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

        # What a frame is given comes from the screen it is shown on: a
        # frame rate held by the vsync says nothing on its own, the
        # budget it leaves says everything.
        self.refresh = screen_refresh()
        if self.refresh:
            viewer.monitor.budget = 1 / self.refresh

        self.set_vsync(enabled=self.vsync)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_cursor_pos_callback(self.window, self.on_cursor)
        glfw.set_scroll_callback(self.window, self.on_scroll)
        glfw.set_framebuffer_size_callback(self.window, self.on_resize)

        self.clock = glfw.get_time()
        viewer.monitor.restart(self.clock)

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

    def set_vsync(self, *, enabled: bool) -> None:
        """
        Wait for the screen between two frames, or stop waiting for it.

        Turning it off is what tells a rendering apart from a screen: a
        vsynced window draws at the refresh rate whatever the cube
        costs, and only a free running one shows what the machine truly
        holds. The processor and GPU times mean the same thing either
        way.

        Args:
            enabled: Whether a frame waits for the next refresh.

        """
        import glfw

        self.vsync = enabled

        glfw.swap_interval(1 if enabled else 0)

    def profile(self) -> RenderProfile:
        """
        Tell what a frame draws, the share of the window included.

        Returns:
            The profile of the viewer, completed with what only a window
            knows: the screen it is shown on and the vsync it waits for.

        """
        return replace(
            self.viewer.profile(),
            refresh=self.refresh,
            vsync=self.vsync,
        )

    def update_title(self, now: float) -> None:
        """
        Show what the frames cost, once a period has gone by.

        The numbers go to the title of the window, drawing text in the
        scene taking a font and a program of its own. Only three fit
        there; ``F4`` writes the rest to standard output.

        The period is measured on the monitor and never on ``clock``:
        the latter is the moment the last frame was drawn, which
        ``tick()`` moves forward on every single frame, and a rate
        averaged over that would always be averaged over nothing.

        Args:
            now: The moment the frame was drawn, in seconds.

        """
        import glfw

        monitor = self.viewer.monitor

        if not monitor.due(now):
            return

        glfw.set_window_title(
            self.window,
            debug_title(monitor, now, self.title, vsync=self.vsync),
        )

        monitor.restart(now)

    def reset_title(self, now: float) -> None:
        """
        Put the plain title back, and start counting frames afresh.

        Called whenever the monitor is turned on or off: turned on, the
        first period starts now instead of covering all the time it
        spent asleep; turned off, the last numbers leave the title.

        Args:
            now: The moment the new period starts, in seconds.

        """
        import glfw

        glfw.set_window_title(self.window, self.title)

        self.viewer.monitor.restart(now)

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
        performance in its title, the vsync it waits for — and
        everything else is handed to the viewer in its own vocabulary.

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
            viewer.debug = not viewer.debug
            self.reset_title(self.clock)
        elif key == glfw.KEY_F4:
            output(debug_report(viewer.monitor, self.profile(), self.title))
        elif key == glfw.KEY_F5:
            self.set_vsync(enabled=not self.vsync)
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

    def frame(self, delta: float) -> None:
        """
        Draw one frame, and nothing of the window around it.

        The seam of the host, and the one method a consumer layering
        effects on the cube writes again: everything a window takes —
        the timing, the swap, the events, the counter — stays in
        ``tick()``, so an effect never has to copy a loop to slip
        between ``advance()`` and ``draw()``.

        Args:
            delta: Seconds gone by since the last frame.

        """
        self.viewer.frame(delta)

    def tick(self) -> None:
        """
        Play one frame: let time pass, draw it, and read the events.

        The elapsed time is measured rather than assumed, so an
        animation lasts as long as it should whatever the frame rate the
        machine holds.

        The work and the swap are timed apart, and that separation is
        the whole point: under a vsync the swap holds everything a frame
        does not spend, so it is the one number that says how much room
        is left.

        **A monitored vsync waits for the GPU right after the swap**,
        and there alone: a driver does not block where one would expect
        it to. Swapping merely queues the frame, and the wait for the
        screen falls on the next call that fills the queue — the first
        draw of the frame after, which came out at fifteen milliseconds
        of "processor time" the processor never spent. One ``finish()``
        puts that wait back where it belongs.

        It is asked for **only when the vsync is on**, which is the only
        time there is a wait to move: a free running window has nothing
        to wait for, and making it wait all the same divided its rate by
        fifty — which is the very measure ``F5`` exists to take.
        """
        import glfw

        now = glfw.get_time()
        self.frame(now - self.clock)
        self.clock = now

        drawn = glfw.get_time()
        glfw.swap_buffers(self.window)

        if self.viewer.debug and self.vsync and self.context is not None:
            self.context.finish()

        swapped = glfw.get_time()

        glfw.poll_events()

        monitor = self.viewer.monitor
        monitor.swap.add(swapped - drawn)
        monitor.count_frame(swapped - now)

        if self.viewer.debug:
            self.update_title(swapped)

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
