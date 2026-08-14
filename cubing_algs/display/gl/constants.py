"""Constants of the GPU rendering backend."""
import math

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

# Default square size, in pixels, of an offscreen render.
RENDER_SIZE = 512

# Samples of the multisampled framebuffer an offscreen render draws to.
# Zero renders without any antialiasing.
RENDER_SAMPLES = 4

# Color the framebuffer is cleared with, the alpha channel included:
# fully transparent, as the SVG backend leaves its background empty.
BACKGROUND_COLOR: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)

# Direction the light shines from, in world coordinates, normalized by
# the renderer. Above, slightly to the right and to the front, which
# lights the three faces the default framing shows.
LIGHT_DIRECTION = (0.35, 0.85, 0.45)

# Share of the lighting a face gets whatever its orientation. Kept high
# on purpose: a sticker must keep the color of its palette, the diffuse
# part being only there to tell the three visible faces apart.
AMBIENT_LIGHT = 0.72

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
