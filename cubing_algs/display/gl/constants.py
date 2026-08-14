"""Constants of the GPU rendering backend."""

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
