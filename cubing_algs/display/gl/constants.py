"""Constants of the GPU rendering backend."""
import math
from dataclasses import dataclass

# Minimum OpenGL version required by the shaders, as a version code
# (3.3 core). Chosen because it is the lowest version supporting
# instanced rendering everywhere we care about.
GL_VERSION_REQUIRED = 330

# Backends tried in order when creating a standalone (headless) context.
# ``None`` lets moderngl pick its own default for the platform.
STANDALONE_BACKENDS: tuple[str | None, ...] = (None, 'egl')

# OpenGL libraries tried in order when attaching to a window context.
# ``None`` lets moderngl load its own default, ``libGL.so`` , which only
# ships with the development package of Mesa. The versioned name is
# always there, so it is worth a second try before giving up.
WINDOW_LIBRARIES: tuple[str | None, ...] = (None, 'libGL.so.1')

# glcontext, the loader behind moderngl, can only attach to a context
# through GLX or WGL: it has no way to detect a Wayland one. On a
# Wayland session, glfw is therefore asked for its X11 variant, which
# goes through XWayland. Set PYGLFW_LIBRARY_VARIANT yourself to override.
GLFW_VARIANT_ENVIRONMENT = 'PYGLFW_LIBRARY_VARIANT'
GLFW_VARIANT_FALLBACK = 'x11'

# pyGLFW reads that variant once, when it is first imported. A caller
# importing glfw before the backend had a say locks the Wayland one in,
# and every window then holds a context nobody can attach to. Saying so
# plainly is the whole cure: nothing can be done about it afterwards.
GLFW_WAYLAND_LOCKED = (
    'glfw is running on Wayland, which moderngl cannot attach to.\n'
    'pyGLFW chooses its variant when it is first imported, and something '
    'imported it before cubing_algs could ask for the X11 one.\n'
    f'Set { GLFW_VARIANT_ENVIRONMENT }={ GLFW_VARIANT_FALLBACK } in the '
    'environment, or import cubing_algs.display.gl before glfw.'
)

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

# Default square size, in pixels, of an offscreen render.
RENDER_SIZE = 512

# Samples of the multisampled framebuffer an offscreen render draws to.
# Zero renders without any antialiasing. Eight is where the staircase of
# the silhouette stops showing at the sizes a cube is rendered at.
RENDER_SAMPLES = 8

# How long a single quarter turn of an animation lasts, in seconds. Fast
# enough to read as a turn rather than as a slideshow, slow enough to
# follow.
MOVE_DURATION = 0.28

# Floor of the duration of a turn, in seconds: what a move keeps when
# the dates it carries would have it shorter still. Below it a turn is
# no longer read as one, and a burst of moves stamped at the very same
# moment would flash by.
MINIMUM_MOVE_DURATION = 0.06

# How long a pause holds the cube still, in seconds. A pause says a
# hesitation, so it is given the time one takes rather than none at all.
# It is a beat, not a rule: what follows a pause starts at the later of
# that beat and its own date, so a rest a stream already carries in its
# timestamps is never shortened by it.
PAUSE_DURATION = 1.0

# What a half turn multiplies that duration by. Given the same beat as a
# quarter turn it covers twice the angle, hence goes twice as fast, which
# reads as a jolt in the middle of an algorithm. Doubling the beat is the
# other extreme: a hand does not take twice as long to flick a face round
# twice. This sits between the two, nearer the hand.
HALF_TURN_FACTOR = 1.4

# Frames rendered per second of animation. Twenty five is where a GIF
# stops flickering without doubling the weight of the file.
FRAME_RATE = 25.0

# How many times an animation plays: zero loops forever, as a GIF of an
# algorithm is meant to.
ANIMATION_LOOP = 0

# How long the state an animation starts from and the one it ends on are
# held, in seconds. An animation shows each of them for a single frame,
# forty milliseconds at twenty five images per second: the two states
# carrying the information, the case to recognize and what the algorithm
# leads to, then go by without ever being seen.
HOLD_START = 1.0
HOLD_END = 1.0

# Color the framebuffer is cleared with, the alpha channel included:
# fully transparent, as the SVG backend leaves its background empty.
BACKGROUND_COLOR: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

# Radius of the bounding sphere of the cube, whose body spans
# [-1, 1] on each axis whatever its size, as in display/image.py.
BOUNDING_RADIUS = math.sqrt(3)

# Shape of a cubie, as fractions of its own half extent, so that a cube
# keeps the same proportions whatever its size.

# Space left between two neighbouring cubies, which is what draws the
# black grooves running across the cube.
CUBIE_GAP = 0.04

# Width of the chamfer cutting the edges and the corners of a cubie.
CUBIE_BEVEL = 0.12

# Inset of a sticker from the border of the beveled face it sits on.
STICKER_MARGIN = 0.08

# How far a sticker floats above the plastic: enough to win the depth
# test at any distance, too little to show on the silhouette.
STICKER_LIFT = 0.01

# How far the ball core swells past the cavity the outer layer leaves
# around it, as a fraction of the half extent of a cubie. Sinking it into
# the pieces is what makes it show at all: a hole dug by the mask is a
# square shaft as deep as a piece is thick, and seen from the default
# framing its own wall hides whatever sits at the bottom. Three quarters
# of the way up the shaft, which is what this fraction buys, is where the
# core starts reading as the inside of the cube.
CORE_BULGE = 1.3

# Parallels and meridians of the ball core. Its normals are interpolated,
# so this only decides how round its silhouette is, and it is only ever
# seen through a hole or a groove.
CORE_RINGS = 16
CORE_SEGMENTS = 32

# Color of the ball core. Not a palette entry: the SVG backend has no
# inside to draw, and one value is enough for a piece nothing else is
# compared to. Blue green, which no palette gives a sticker, so a hole
# reads as the inside of the cube rather than as another piece.
CORE_COLOR: tuple[float, float, float] = (0.18, 0.62, 0.62)

# Gain of the two-tone gradient the fake environment of a metal core is
# read off, top and bottom, as a share of the core's own color. A metal
# with no texture and no cubemap still has to reflect *something*, and a
# flat color reflected back is indistinguishable from no reflection at
# all - the gradient is the cheapest thing that still tells the ball it
# is curved. Built off ``core_color`` itself, low and high, rather than
# as a color of their own: a consumer changing the core never has to
# touch a second constant to keep the reflection matching it.
CORE_ENV_LOW_GAIN = 0.12
CORE_ENV_HIGH_GAIN = 2.2


@dataclass(frozen=True, slots=True)
class Look:
    """
    Every knob shaping how the light falls on the cube.

    No color is decided here: the stickers keep the ones their palette
    gives them, exactly as in the SVG backend. What follows only says
    how they are lit, which is the whole difference between a solid and
    a flat drawing.

    A ``Look`` is immutable, so passing one around costs nothing and the
    default one can safely be a default argument.
    """

    # Direction the light shines from, in world coordinates, normalized
    # by the renderer. Above, slightly to the right and to the front,
    # which lights the three faces the default framing shows.
    light_direction: tuple[float, float, float] = (0.35, 0.85, 0.45)

    # Share of the lighting a face gets whatever its orientation. Kept
    # high on purpose: a sticker must keep the color of its palette, the
    # diffuse part being only there to tell the visible faces apart.
    ambient: float = 0.74

    # Exponent the palette color is raised to before being lit, and its
    # inverse afterwards: 2.2 shades in linear space, as the physics
    # wants it, 1.0 shades the sRGB color as it comes.
    gamma: float = 2.2

    # How much darker a fragment gets as it sinks into a groove, and how
    # tightly that darkening hugs the edges of a cubie. This is the
    # ambient occlusion of the backend: no buffer, no sampling, just the
    # place of a fragment inside its own piece.
    #
    # The falloff is what keeps the shadow of a groove inside it: a
    # gentle one spreads over the whole sticker, which reads as a color
    # drifting away from its palette rather than as a relief.
    groove_occlusion: float = 0.75
    groove_falloff: float = 6.0

    # Light catching the silhouette of the cube, tinted by the color it
    # grazes. Detaches the piece from the background without any of the
    # glare a specular highlight would bring.
    rim_strength: float = 0.25
    rim_power: float = 3.0

    # The one highlight of the look, kept narrow and weak: enough to
    # tell that a sticker is glossy, never enough to wash its color.
    # Reaches the stickers alone, the plastic being matte.
    specular_strength: float = 0.06
    specular_power: float = 32.0

    # Color of the ball core. Here rather than in a palette, which
    # paints stickers alone, and here rather than as the constant it
    # defaults to: a consumer drawing the inside of a cube may have
    # something to say about it - a core that goes dull when nothing is
    # driving the cube any more - and ``draw()`` takes a look of its
    # own for exactly that.
    core_color: tuple[float, float, float] = CORE_COLOR

    # The highlight of the ball core, which is not the one of a sticker.
    # A sticker is a flat printed patch seen next to twenty-five others,
    # so its gloss must stay a hint; the core is a molded ball seen alone
    # at the bottom of a hole, and a broad bright spot on it is what
    # tells a sphere from a disc. Hence knobs of its own, stronger and
    # wider, rather than the ones of the pieces.
    core_specular_strength: float = 0.45
    core_specular_power: float = 18.0

    # Light catching the silhouette of the core, as the rim of the cube
    # does for a piece: it separates the ball from the wall of the shaft
    # it is seen through, which is the only place its outline shows.
    core_rim_strength: float = 0.25
    core_rim_power: float = 3.0

    # How much of the core is metal rather than plastic, from none of it
    # to all of it. A metal reflects light in its own color and a
    # dielectric in the color of the lamp, which is the one number a
    # metalness workflow is built on: it tints the highlight, fades the
    # diffuse term out - a metal has no sub-surface term to speak of, its
    # color coming entirely from what it reflects - and, past zero, turns
    # on a cheap Fresnel-weighted reflection of a fake environment built
    # off the ball's own color. Zero reproduces the plastic ball exactly,
    # term for term, which is why it is the default: nothing here changes
    # the look of a core nobody has asked to be metal.
    core_metalness: float = 0.0

    # Amplitude of the noise breaking the flatness of a sticker, as a
    # fraction of its color. Sticks to the piece rather than to the
    # screen, so it does not crawl when the cube turns.
    sticker_grain: float = 0.03

    # Samples of the multisampled framebuffer a render draws to, clamped
    # to what the context supports. Zero renders without antialiasing.
    samples: int = RENDER_SAMPLES


# The look every rendering uses unless told otherwise.
DEFAULT_LOOK = Look()

# Clipping planes of the camera, wide enough for any framing of a cube
# without wasting depth precision.
CAMERA_NEAR = 0.1
CAMERA_FAR = 100.0

# How far the camera can be tilted before its up direction becomes
# parallel to its line of sight, which no view matrix survives.
PITCH_LIMIT = math.radians(89.9)

# Bounds of the orbit distance, from just outside the cube to a view
# where it is a speck.
CAMERA_MIN_DISTANCE = 2.5
CAMERA_MAX_DISTANCE = 40.0

# Default title of the interactive window.
WINDOW_TITLE = 'cubing-algs'

# Default width and height of the interactive window, in pixels.
VIEWER_SIZE = (720, 720)

# Color the window is cleared with. Opaque, unlike an offscreen render:
# a window has no alpha channel to hand back. A cold slate, and the one
# color here that is a taste rather than a measurement: a mid grey is
# the neutral a look is *judged* against, which is not the same as the
# ground it is best seen on, and a window is left open for the length of
# a session where an image is looked at once.
#
# It costs the silhouette of the plastic, which does melt into anything
# this dark, and that is measured rather than assumed: the rim light is
# ``pow(1 - dot(normal, view), rim_power)``, so it reaches the chamfers
# of the outline alone - a few pixels wide - and raising it to compensate
# changes nothing an eye can find. What draws a cube against a dark
# ground is the outer stickers, and they gain from it: a palette reads
# more saturated here than it ever did on the grey.
#
# Never darker than the ball core, which is the one thing a window may be
# left showing on its own: ``Look.core_color`` is a field precisely so a
# consumer can dim it while nothing drives the cube, and a ground taken
# down with it would swallow the only thing left in the window.
VIEWER_BACKGROUND: tuple[float, float, float, float] = (0.12, 0.13, 0.15, 1.0)

# The background of a window whose compositor is asked to let the desktop
# through, against the opaque ground above. A cube laid on the desktop is
# what is left when nothing at all is drawn behind it.
VIEWER_TRANSPARENT: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

# What is said when a compositor hands back an ordinary window: the hint
# is a request, and a background cleared to nothing on an opaque window
# shows whatever the driver happened to leave there. So the ground of the
# viewer is kept, and the refusal is worth a line - the flag was passed
# and the window does not look like it.
TRANSPARENCY_REFUSED = (
    'The compositor refused a transparent window: '
    'the cube is drawn on the ground of the viewer'
)

# How long the performance of the rendering is averaged over before
# being shown, in seconds: short enough to follow a slowdown, long enough
# not to flicker. It is shown in the title of the window rather than in
# the scene, drawing text taking a font, an atlas and a second program,
# which is exactly what this backend exists to do without.
MONITOR_INTERVAL = 1.0

# How many frames the sliding window of the monitor keeps, which is what
# a minimum, an average and a percentile are read on. Two seconds and a
# half of a hundred hertz screen: long enough for a percentile to mean
# something, short enough to forget a slowdown once it is over.
MONITOR_WINDOW = 240

# What a frame has to exceed the budget by to be counted as dropped.
# Half again is past any jitter of the swap and short of a second frame.
DROP_FACTOR = 1.5

# How long a frame is given when no screen says how fast it refreshes,
# in seconds. Sixty hertz, the one rate every machine holds.
DEFAULT_BUDGET = 1 / 60

# Colors of the three axes of the grid, in the conventional order: X
# red, Y green, Z blue. Nothing labels them, drawing text taking a font,
# an atlas and a program of its own, so the color is the name.
AXES_COLORS: tuple[tuple[float, float, float], ...] = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)

# How far an axis reaches from the center of the cube, as a fraction of
# the sphere the cube fits in. Leaving the surface of a cube is not
# enough to be seen: in perspective an axis keeps running over the
# silhouette long after it has come out of it, and a red line over the
# red stickers of a face reads as nothing at all. A fifth past the
# bounding sphere is where the three of them clear the cube at the
# default framing, at the price of a tip the border of the window may cut
# on the flattest views, which costs a few pixels of a line and no
# information at all.
AXES_REACH = 1.2

# How far the camera turns for one pixel of mouse drag, in radians.
ORBIT_SENSITIVITY = 0.008

# What one notch of the wheel multiplies the distance to the cube by.
ZOOM_STEP = 0.9

# How far a cubie flies when the cube is opened, as a share of the
# distance from its center to the one of the cube. The camera does not
# follow: a cube pushed this far apart leaves the window at the default
# framing - measured, 0.10 is already all it holds - and the wheel is
# what a look inside costs.
EXPLODE_SPREAD = 0.7

# How fast the cube reaches the state it is asked for, per second. An
# exponential approach, so the same second of elapsed time carries the
# same share of the distance whatever the frame rate.
EXPLODE_SPEED = 6.0

# Below this the cube has arrived, and the spread is snapped onto what
# it aims at: an approach never quite lands, and a cube still moving by
# a thousandth would rebuild its scene on every frame forever.
SPREAD_SETTLED = 0.001

# How fast the displayed orientation catches up with the last one a
# gyroscope reported, per second. A sensor speaks tens of times a
# second at best, well under the frame rate of a vsynced window, and
# reading it straight into the render turns every arrival into a
# visible snap. The same exponential approach as EXPLODE_SPEED fixes
# it: the same second of elapsed time closes the same share of the
# arc, whatever the frame rate, and it is tuned faster than the
# opening of the cube because a hand turning it is not a slow effect -
# the point is to erase the stepping the sensor's own rate leaves,
# not to add a trail of its own.
ORIENTATION_SETTLE_SPEED = 25.0

# Below this the tracker has arrived, and the orientation is snapped
# onto what it aims at - measured as one minus the absolute dot
# product of the two quaternions, which reads as an angle regardless
# of which side of the double cover either one is written on.
ORIENTATION_SETTLED = 1e-5

# Name of a screenshot, stamped with the moment it was taken so that
# two of them never overwrite one another.
SCREENSHOT_NAME = 'cubing-algs-%Y%m%d-%H%M%S.png'

# The shortcuts of the viewer, shown when its window opens.
VIEWER_HELP = """\
cubing-algs viewer
  Drag             Orbit the cube
  Ctrl Drag        Carry the window across the screen
  Wheel            Zoom in and out
  R U F L D B      Turn a face
  M E S            Turn a slice
  X Y Z            Turn the whole cube
  Shift            Primes a face turn as in R'
  Ctrl             Doubles a face turn as in R2
  Alt              Widen a face turn, as in Rw
  Space            Frame the cube again
  Backspace        Put the cube back as it was
  Tab              Open the cube up, and put it back together
  F2               Show the X/Y/Z axes, red green blue
  F3               Monitor the rendering performance
  F4               Print a performance report
  F5               Turn the vsync on and off
  F12              Write a screenshot
  Esc, Q           Close the window\
"""

# Name of the extra shipping moderngl and glfw together, and the error
# messages shown when either is missing: one extra, so the same cure.
OPENGL_EXTRA = 'opengl'

OPENGL_EXTRA_INSTALL = (
    f"Install it with: pip install 'cubing-algs[{ OPENGL_EXTRA }]'"
)

MODERNGL_MISSING = (
    f'The GPU rendering backend requires moderngl.\n{ OPENGL_EXTRA_INSTALL }'
)

GLFW_MISSING = (
    f'The interactive viewer requires glfw.\n{ OPENGL_EXTRA_INSTALL }'
)

# Pillow belongs to no extra: it only encodes the GIF of an animation,
# and its absence costs a series of PNG frames rather than a failure.
PILLOW_MISSING = (
    'Encoding a GIF requires Pillow.\nInstall it with: pip install Pillow'
)
