"""
The glfw host of the interactive viewer.

A ``Viewer`` holds a cube, a camera and an animation, and knows how to
draw one frame; it owns neither a window nor a loop. This module is what
gives it both under glfw, and it is a module of its own for one reason:
``viewer.py`` names glfw nowhere, so another host - a ``QOpenGLWidget``,
a pygame surface, anything already owning an event loop - plugs the very
same viewer into it by writing the same handful of methods.

What a host owes a viewer is short: attach a ``Stage`` built on a current
context, call ``frame()`` once per frame, and translate its own input
into ``press()``, ``drag()``, ``scroll()`` and ``resize()``.

glfw is imported lazily, and never before ``create_window()``, the one
place naming the extra a missing glfw asks for.
"""
import logging
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from typing import TYPE_CHECKING

from cubing_algs.display.gl.constants import TRANSPARENCY_REFUSED
from cubing_algs.display.gl.constants import VIEWER_HELP
from cubing_algs.display.gl.constants import VIEWER_TRANSPARENT
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.display.gl.context import GLFWMonitor
from cubing_algs.display.gl.context import GLFWWindow
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.context import transparency_granted
from cubing_algs.display.gl.metrics import RenderProfile
from cubing_algs.display.gl.metrics import debug_report
from cubing_algs.display.gl.metrics import debug_title
from cubing_algs.display.gl.renderer import OffscreenTarget
from cubing_algs.display.gl.viewer import Stage
from cubing_algs.display.gl.viewer import Viewer
from cubing_algs.display.gl.viewer import output

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

logger = logging.getLogger(__name__)


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


def window_screen(window: GLFWWindow) -> GLFWMonitor:
    """
    Find the screen a window is shown on.

    glfw names the monitor of a fullscreen window and of no other, so a
    windowed one is placed by hand: the screens of a desk are laid out
    side by side in one coordinate space, and the one holding the
    center of the window is the one showing it.

    Args:
        window: The window to place.

    Returns:
        The screen showing the window, the primary one when no screen
        holds it, and nothing at all when the machine has none.

    """
    import glfw

    left, top = glfw.get_window_pos(window)
    width, height = glfw.get_window_size(window)

    x = left + width // 2
    y = top + height // 2

    for screen in glfw.get_monitors():
        mode = glfw.get_video_mode(screen)

        if not mode:
            continue

        origin_x, origin_y = glfw.get_monitor_pos(screen)

        if (origin_x <= x < origin_x + mode.size.width
                and origin_y <= y < origin_y + mode.size.height):
            return screen

    return glfw.get_primary_monitor()


def screen_refresh(window: GLFWWindow) -> float:
    """
    Read how fast the screen showing a window refreshes.

    This is the ceiling a vsynced frame rate can never pass, and it is
    therefore the budget a frame is given: on a hundred hertz screen a
    frame has ten milliseconds, whatever a counter shows.

    It is read off the screen the window truly sits on, and not off the
    primary one: a desk mixing a sixty hertz screen with a hundred
    hertz one gives a frame two very different budgets, and the window
    is not always where the primary is.

    Args:
        window: The window whose screen is to be read.

    Returns:
        The refresh rate in hertz, zero when no screen says.

    """
    import glfw

    screen = window_screen(window)

    if not screen:
        return 0.0

    mode = glfw.get_video_mode(screen)

    if not mode:
        return 0.0

    return float(mode.refresh_rate)


@dataclass  # noqa: PLR0904
class GlfwHost:
    """
    A window, an event loop, and a viewer drawing into it.

    Everything glfw of the backend lives here: the window, the timing of
    the frames, the performance written in the title, the vsync, the
    transparent visual and the carry it needs, and the translation of
    the keyboard and the mouse into the neutral vocabulary the viewer
    speaks. That is what the count of public methods is spent on, and
    why it is over the limit: this class is the one place naming glfw,
    and splitting it would be splitting a window in two.

    Nothing is opened until ``run()`` - or ``open()`` - is called, and
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

    # A cube laid on the desktop: no background, no decoration, and
    # floating above everything. It is one mode rather than three
    # options because the three hold together - a window letting the
    # desktop through while keeping its bar would show it through a
    # frame, and one free to drop behind another would be lost. What it
    # costs is the title: a window without a bar has nowhere to show it.
    transparent: bool = False

    # What the cube is antialiased by. Turning it off is a way out of
    # the offscreen detour a transparent window imposes: the cube is
    # then drawn into the window itself, aliased but with nothing in
    # between.
    msaa: bool = True

    # What ``run()`` writes when the window opens. A host answering
    # fewer keys than the viewer does - one showing a cube it is not
    # the one turning, among others - hands its own list here rather
    # than reprinting a loop to correct a line of it.
    shortcuts: str = VIEWER_HELP

    window: GLFWWindow = field(init=False, default=None)
    context: 'moderngl.Context | None' = field(init=False, default=None)
    clock: float = field(init=False, default=0.0)
    refresh: float = field(init=False, default=0.0)
    dragging: bool = field(init=False, default=False)
    cursor: tuple[float, float] = field(init=False, default=(0.0, 0.0))

    # Where the cube is drawn when the window itself cannot hold the
    # samples: it belongs to the transparent mode alone, and stays None
    # without it.
    target: OffscreenTarget | None = field(init=False, default=None)

    # What the window is carried by, and where the cursor took hold of
    # it. A window is free to place itself on every platform a window is
    # opened on here: a Wayland session is given the X11 variant of
    # glfw, moderngl having no way to read a context off the other one,
    # and a platform that stayed Wayland is refused a window long before
    # the mouse is of any interest.
    carrying: bool = field(init=False, default=False)
    anchor: tuple[float, float] = field(init=False, default=(0.0, 0.0))

    @property
    def offscreen(self) -> bool:
        """
        Tell whether the cube is drawn aside and copied to the window.

        Returns:
            True when the frame goes through a multisampled target,
            which a transparent visual leaves as the only way to
            antialias the cube.

        """
        return self.transparent and self.msaa

    @property
    def samples(self) -> int:
        """
        Tell how many samples the window itself is asked for.

        A transparent visual and a multisampled window are mutually
        exclusive on this driver - asking for both gets the transparency
        refused - so a transparent window is asked for none of them and
        the cube is antialiased offscreen instead. ``msaa`` off asks for
        no antialiasing at all, in the window as anywhere else.

        Returns:
            The samples of the look, or none of them.

        """
        if self.transparent or not self.msaa:
            return 0

        return self.viewer.look.samples

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
            viewer.window_size,
            self.title,
            samples=self.samples,
            transparent=self.transparent,
        )
        context = create_window_context()
        self.context = context

        import glfw

        # The size asked for and the one truly given apart on a scaled
        # display, and the cube is framed on what there is to draw into.
        width, height = glfw.get_framebuffer_size(self.window)
        stage = Stage.attach(context, viewer.geometry, (width, height))
        self.clear_ground(stage)
        viewer.attach(stage)

        # What a frame is given comes from the screen it is shown on: a
        # frame rate held by the vsync says nothing on its own, the
        # budget it leaves says everything. Read once, on the screen the
        # window opened on - a window dragged onto another screen keeps
        # the budget of the first, and it is `drops`, measured on the
        # pace truly held, that stays right whatever it is dragged onto.
        self.refresh = screen_refresh(self.window)
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

    def clear_ground(self, stage: Stage) -> None:
        """
        Give the stage the ground this window is cleared to.

        A compositor is free to refuse a transparent visual, and the
        ground of the viewer is what a refused one falls back on: a
        background cleared to nothing on an opaque window shows whatever
        the driver happened to leave there. So the answer is read back
        rather than assumed, and a refusal is worth a line - the flag
        was passed and the window will not look like it.

        An opaque window is left with the ground the stage was built
        with, which is the one every window of the library is cleared
        to.

        Args:
            stage: The stage the viewer is about to draw into.

        """
        if not self.transparent:
            return

        if transparency_granted(self.window):
            stage.background = VIEWER_TRANSPARENT
        else:
            logger.warning(TRANSPARENCY_REFUSED)

    def refresh_target(self) -> None:
        """
        Keep the offscreen target the size of the window it lands in.

        The whole detour, in one field: the stage draws into a
        multisampled target instead of the window, and ``resolve()``
        brings it back, alpha and all. A window that can hold its own
        samples - or is asked for no antialiasing at all - needs none of
        it, and builds no target.
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
        target was ever built, and the frame is already where it
        belongs.
        """
        target = self.target

        if target is None:
            return

        context = self.viewer.require_stage().context

        context.copy_framebuffer(target.resolved, target.framebuffer)
        context.copy_framebuffer(context.screen, target.resolved)

    def close(self) -> None:
        """
        Close the window, if one is open, and forget about it.

        The context stands for the pair: ``open()`` sets both or
        neither, so testing it alone leaves no unreachable branch behind.
        The offscreen target is given back first, while the context it
        was built on is still alive.
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

    def write_title(self, text: str) -> None:
        """
        Write a text in the bar of the window, whatever the title says.

        What the debug counter shows is not the name of the window: it
        is the title with the numbers of the moment appended, replaced
        several times a second and gone the moment F3 is pressed again.
        So it is written here, and ``title`` is left where it stands.

        A window that is not open yet is written to all the same, and
        costs the call alone: ``open()`` hands the title over to glfw
        itself.

        Args:
            text: What to show in the bar of the window.

        """
        if self.window is None:
            return

        import glfw

        glfw.set_window_title(self.window, text)

    def set_title(self, title: str) -> None:
        """
        Rename the window, now and for the debug numbers to come.

        The name of a window is not always known when it opens: a
        consumer showing what it is connected to learns it from
        whatever it listens to, and says so afterwards. It is written
        into ``title`` rather than into the bar alone, so that the
        debug counter appends its numbers to the new name rather than
        putting the old one back on its next period.

        Nothing is written when the name has not changed, a title being
        pushed at the cadence of the frames by a consumer that has no
        cheaper way to tell.

        Args:
            title: The name of the window.

        """
        if title == self.title:
            return

        self.title = title

        self.write_title(title)

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
        monitor = self.viewer.monitor

        if not monitor.due(now):
            return

        self.write_title(
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
        self.write_title(self.title)

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

        What belongs to the window is answered here - closing it, the
        performance in its title, the vsync it waits for - and
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
        elif key == glfw.KEY_F3:
            viewer.debug = not viewer.debug
            self.reset_title(self.clock)
        elif key == glfw.KEY_F4:
            output(debug_report(viewer.monitor, self.profile(), self.title))
        elif key == glfw.KEY_F5:
            self.set_vsync(enabled=not self.vsync)
        elif not self.on_viewer_key(key):
            viewer.press(
                key_letter(key),
                prime=bool(mods & glfw.MOD_SHIFT),
                double=bool(mods & glfw.MOD_CONTROL),
                wide=bool(mods & glfw.MOD_ALT),
            )

    def on_viewer_key(self, key: int) -> bool:
        """
        Answer a key the viewer holds the state of.

        The other half of ``on_key()``: what a window answers itself -
        closing, the title, the vsync - stays there, and everything
        reaching no further than the viewer is settled here.

        Args:
            key: The glfw code of the key.

        Returns:
            Whether the key was one of them. A key nobody answers here
            is a move waiting to be read as one.

        """
        import glfw

        viewer = self.viewer

        if key == glfw.KEY_SPACE:
            viewer.reset_camera()
        elif key == glfw.KEY_BACKSPACE:
            viewer.reset_cube()
        elif key == glfw.KEY_TAB:
            viewer.exploded = not viewer.exploded
        elif key == glfw.KEY_F2:
            viewer.show_axes = not viewer.show_axes
        elif key == glfw.KEY_F12:
            viewer.screenshot()
        else:
            return False

        return True

    def carry(self, x: float, y: float) -> None:
        """
        Move the window by what the cursor gained on its anchor.

        The cursor is reported inside the window, so moving the window
        by that gain puts the cursor back on its anchor: the offset is
        measured afresh at every event, and nothing drifts. Counting the
        distance from the previous position instead would move the
        window twice.

        Args:
            x: Where the cursor stands, in pixels from the left.
            y: Where the cursor stands, in pixels from the top.

        """
        import glfw

        anchor_x, anchor_y = self.anchor
        window_x, window_y = glfw.get_window_pos(self.window)

        glfw.set_window_pos(
            self.window,
            int(window_x + x - anchor_x),
            int(window_y + y - anchor_y),
        )

    def on_mouse_button(
            self,
            window: GLFWWindow,
            button: int,
            action: int,
            mods: int,
    ) -> None:
        """
        Take hold of the window, or of the cube, until the button goes.

        Which button orbits is what no mode may change: the drag is the
        one gesture a viewer is made of, and a window looking different
        is no reason to go and find it elsewhere. So the carry a window
        with no bar needs is Ctrl held down at the moment of the press,
        and a decorated window answers it too, where it merely doubles
        the bar it still has - which is what makes the gesture learnable
        before ``transparent`` is ever passed.

        Ctrl let go halfway through carries the window all the same:
        glfw says nothing of a modifier changing, and the carry belongs
        to the button that began it.

        Args:
            window: The window the button was pressed in.
            button: The glfw code of the button.
            action: Whether the button was pressed or released.
            mods: The modifier keys held down with it.

        """
        import glfw

        if button != glfw.MOUSE_BUTTON_LEFT:
            return

        self.cursor = glfw.get_cursor_pos(window)

        if action == glfw.PRESS and mods & glfw.MOD_CONTROL:
            self.carrying = True
            self.anchor = self.cursor
            return

        if self.carrying:
            self.carrying = False
            return

        self.dragging = action == glfw.PRESS

    def on_cursor(self, _window: GLFWWindow, x: float, y: float) -> None:
        """
        Carry the window, or orbit the camera, as the mouse moves.

        Where the cursor stands is written down whatever happens: the
        orbit reads its next move from there even when the window is the
        thing that moved.

        Args:
            _window: The window the mouse moved over, unused.
            x: Where the cursor stands, in pixels from the left.
            y: Where the cursor stands, in pixels from the top.

        """
        previous_x, previous_y = self.cursor
        self.cursor = (x, y)

        if self.carrying:
            self.carry(x, y)
            return

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
        effects on the cube writes again: everything a window takes -
        the timing, the swap, the events, the counter - stays in
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
        screen falls on the next call that fills the queue - the first
        draw of the frame after, which came out at fifteen milliseconds
        of "processor time" the processor never spent. One ``finish()``
        puts that wait back where it belongs.

        It is asked for **only when the vsync is on**, which is the only
        time there is a wait to move: a free running window has nothing
        to wait for, and making it wait all the same divided its rate by
        fifty - which is the very measure ``F5`` exists to take.
        """
        import glfw

        now = glfw.get_time()

        self.refresh_target()
        self.frame(now - self.clock)
        self.resolve()

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

        The shortcuts written here are the ones the host answers, and
        not the ones the viewer knows: a host is free to hold back some
        of them, and ``shortcuts`` is where it says so.

        The window is given back however the loop ends, an interruption
        from the keyboard included.
        """
        self.open()

        import glfw

        output(self.shortcuts)

        try:
            while not glfw.window_should_close(self.window):
                self.tick()
        finally:
            self.close()
