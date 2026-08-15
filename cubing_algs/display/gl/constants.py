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

# Default square size, in pixels, of an offscreen render.
RENDER_SIZE = 512

# Samples of the multisampled framebuffer an offscreen render draws to.
# Zero renders without any antialiasing. Eight is where the staircase of
# the silhouette stops showing at the sizes a cube is rendered at.
RENDER_SAMPLES = 8

# How long a single move of an animation lasts, in seconds. Fast enough
# to read as a turn rather than as a slideshow, slow enough to follow.
MOVE_DURATION = 0.28

# Frames rendered per second of animation. Twenty five is where a GIF
# stops flickering without doubling the weight of the file.
FRAME_RATE = 25.0

# How many times an animation plays: zero loops forever, as a GIF of an
# algorithm is meant to.
ANIMATION_LOOP = 0

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

    # Amplitude of the noise breaking the flatness of a sticker, as a
    # fraction of its color. Sticks to the piece rather than to the
    # screen, so it does not crawl when the cube turns.
    sticker_grain: float = 0.03

    # Contact shadow cast on the ground plane: how dark it is at the
    # foot of the cube, how far its solid core reaches, and over what
    # distance it fades out. A null opacity draws no shadow at all.
    shadow_opacity: float = 0.40
    shadow_inner: float = 1.05
    shadow_softness: float = 0.70

    # Half extent of the ground quad, wide enough to hold the whole
    # fade whatever the framing.
    shadow_extent: float = 2.5

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
# a window has no alpha channel to hand back, and the contact shadow
# needs something to fall on to be seen at all.
VIEWER_BACKGROUND: tuple[float, float, float, float] = (0.16, 0.17, 0.19, 1.0)

# How far the camera turns for one pixel of mouse drag, in radians.
ORBIT_SENSITIVITY = 0.008

# What one notch of the wheel multiplies the distance to the cube by.
ZOOM_STEP = 0.9

# Name of a screenshot, stamped with the moment it was taken so that
# two of them never overwrite one another.
SCREENSHOT_NAME = 'cubing-algs-%Y%m%d-%H%M%S.png'

# The shortcuts of the viewer, shown when its window opens.
VIEWER_HELP = """\
cubing-algs viewer
  drag             orbit the cube
  wheel            zoom in and out
  R U F L D B      turn a face, shift primes it, ctrl doubles it
  M E S            turn a slice
  X Y Z            turn the whole cube
  alt              widen a face turn, as in Rw
  space            frame the cube again
  backspace        put the cube back as it was
  F12              write a screenshot
  escape, Q        close the window\
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
