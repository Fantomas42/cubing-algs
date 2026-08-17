"""
Creation of the OpenGL context, headless or attached to a window.

The whole point of using moderngl is that the *same* rendering code runs
against both kinds of context. This module is the only place where the
difference between the two exists.

All imports of the optional dependencies are lazy: importing this module
never pulls moderngl nor glfw in.
"""
import os
from importlib.util import find_spec
from typing import TYPE_CHECKING
from typing import Any

from cubing_algs.display.gl.constants import GL_VERSION_REQUIRED
from cubing_algs.display.gl.constants import GLFW_MISSING
from cubing_algs.display.gl.constants import GLFW_VARIANT_ENVIRONMENT
from cubing_algs.display.gl.constants import GLFW_VARIANT_FALLBACK
from cubing_algs.display.gl.constants import GLFW_WAYLAND_LOCKED
from cubing_algs.display.gl.constants import MODERNGL_MISSING
from cubing_algs.display.gl.constants import STANDALONE_BACKENDS
from cubing_algs.display.gl.constants import WINDOW_LIBRARIES
from cubing_algs.display.gl.constants import WINDOW_TITLE
from cubing_algs.exceptions import CubingAlgsError

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

# A glfw window handle, an opaque pointer we only ever pass around.
type GLFWWindow = Any

# A glfw monitor handle, opaque in the very same way.
type GLFWMonitor = Any


class GLContextError(CubingAlgsError):
    """
    Raised when no usable OpenGL context can be created.

    A library error like any other, so that a caller catching
    ``CubingAlgsError`` - the CLI among them - reports a missing extra
    or a locked Wayland session as plainly as an invalid move.
    """


def has_moderngl() -> bool:
    """
    Tell whether moderngl is importable.

    Returns:
        True when offscreen rendering is available.

    """
    return find_spec('moderngl') is not None


def has_glfw() -> bool:
    """
    Tell whether glfw is importable.

    Returns:
        True when the interactive window is available.

    """
    return find_spec('glfw') is not None


def try_standalone_backend(
        backend: str | None,
        require: int,
) -> "tuple['moderngl.Context | None', str]":
    """
    Create a standalone context on one given backend.

    Failures are returned rather than raised, so that the caller can try
    the next backend and report every attempt at once.

    Args:
        backend: Name of the backend, None letting moderngl choose.
        require: Minimum OpenGL version code, such as 330.

    Returns:
        The context and an empty reason, or None and the failure reason.

    """
    import moderngl

    options: dict[str, Any] = {'standalone': True, 'require': require}
    if backend is not None:
        options['backend'] = backend

    try:
        return moderngl.create_context(**options), ''
    except (moderngl.Error, ValueError, OSError) as error:
        return None, f'{ backend or "default" }: { error }'


def create_standalone_context(
        require: int = GL_VERSION_REQUIRED,
) -> 'moderngl.Context':
    """
    Create a headless context, usable without any display server.

    The backends of STANDALONE_BACKENDS are tried in order, the first one
    answering wins. Failures are gathered into a single error message, as
    an unavailable EGL is by far the most common cause of them all.

    Args:
        require: Minimum OpenGL version code, such as 330.

    Returns:
        A context rendering to an offscreen framebuffer.

    Raises:
        GLContextError: If moderngl is missing or no backend answers.

    """
    if not has_moderngl():
        raise GLContextError(MODERNGL_MISSING)

    failures: list[str] = []

    for backend in STANDALONE_BACKENDS:
        context, failure = try_standalone_backend(backend, require)
        if context is not None:
            return context
        failures.append(failure)

    details = '\n'.join(f'  - { failure }' for failure in failures)
    message = f'No standalone OpenGL context available:\n{ details }'
    raise GLContextError(message)


def select_glfw_variant() -> None:
    """
    Ask pyGLFW for the X11 variant of its library on a Wayland session.

    pyGLFW picks its variant at import time, from the session type, and
    moderngl cannot attach to a Wayland context. Doing nothing here would
    mean a working window holding a context nobody can talk to.
    """
    if os.environ.get('WAYLAND_DISPLAY'):
        os.environ.setdefault(
            GLFW_VARIANT_ENVIRONMENT,
            GLFW_VARIANT_FALLBACK,
        )


# Chosen as this module is imported, and not only when a window is
# asked for: every module of the backend imports this one, so the
# variant is settled before any of them can reach an ``import glfw``,
# whichever one runs first. Leaving it to create_window() alone made a
# viewer importing glfw one line too early hold an unusable context.
select_glfw_variant()


def check_glfw_platform() -> None:
    """
    Refuse a glfw whose platform no context could ever be read from.

    glfw must have been initialized beforehand. moderngl only knows how
    to attach to a context through GLX or WGL, so a Wayland platform
    would give a perfectly working window holding a context nobody can
    talk to, and a puzzling error a few lines further down.

    Raises:
        GLContextError: On a Wayland platform, glfw being shut down
            again first.

    """
    import glfw

    if glfw.get_platform() != glfw.PLATFORM_WAYLAND:
        return

    glfw.terminate()

    raise GLContextError(GLFW_WAYLAND_LOCKED)


def create_window(
        size: tuple[int, int],
        title: str = WINDOW_TITLE,
        *,
        visible: bool = True,
        samples: int = 0,
        require: int = GL_VERSION_REQUIRED,
) -> GLFWWindow:
    """
    Create a glfw window holding a current OpenGL core profile context.

    The window is returned as is: the caller owns its event loop and its
    destruction. Call create_window_context() right after to get the
    moderngl context bound to it.

    Args:
        size: Width and height of the window, in pixels.
        title: Title of the window.
        visible: Whether the window is shown on screen.
        samples: Samples of the multisampled window framebuffer. Zero
            draws without any antialiasing.
        require: Minimum OpenGL version code, such as 330.

    Returns:
        The glfw window handle, made current.

    Raises:
        GLContextError: If glfw is missing, cannot start, runs on a
            platform moderngl cannot attach to, or cannot provide the
            requested OpenGL version.

    """
    if not has_glfw():
        raise GLContextError(GLFW_MISSING)

    select_glfw_variant()

    import glfw

    if not glfw.init():
        msg = 'glfw could not be initialized: no display server?'
        raise GLContextError(msg)

    check_glfw_platform()

    width, height = size

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, require // 100)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, require % 100 // 10)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    glfw.window_hint(glfw.VISIBLE, glfw.TRUE if visible else glfw.FALSE)
    glfw.window_hint(glfw.SAMPLES, samples)

    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        msg = f'glfw could not create an OpenGL { require } window'
        raise GLContextError(msg)

    glfw.make_context_current(window)

    return window


def destroy_window(window: GLFWWindow) -> None:
    """
    Destroy a window and shut glfw down.

    Args:
        window: The handle returned by create_window().

    """
    import glfw

    glfw.destroy_window(window)
    glfw.terminate()


def try_window_library(
        library: str | None,
        require: int,
) -> "tuple['moderngl.Context | None', str]":
    """
    Attach a moderngl context using one given OpenGL library name.

    Failures are returned rather than raised, so that the caller can try
    the next library and report every attempt at once.

    Args:
        library: File name of the library, None letting moderngl choose.
        require: Minimum OpenGL version code, such as 330.

    Returns:
        The context and an empty reason, or None and the failure reason.

    """
    import moderngl

    options: dict[str, Any] = {'require': require}
    if library is not None:
        options['libgl'] = library

    try:
        return moderngl.create_context(**options), ''
    except (moderngl.Error, ValueError, OSError) as error:
        return None, f'{ library or "default" }: { error }'


def create_window_context(
        require: int = GL_VERSION_REQUIRED,
) -> 'moderngl.Context':
    """
    Create a moderngl context bound to the current window context.

    A window context must have been made current beforehand, typically by
    create_window(). The libraries of WINDOW_LIBRARIES are tried in
    order, the first one answering wins.

    Args:
        require: Minimum OpenGL version code, such as 330.

    Returns:
        A context rendering to the window framebuffer.

    Raises:
        GLContextError: If moderngl is missing or no library answers.

    """
    if not has_moderngl():
        raise GLContextError(MODERNGL_MISSING)

    failures: list[str] = []

    for library in WINDOW_LIBRARIES:
        context, failure = try_window_library(library, require)
        if context is not None:
            return context
        failures.append(failure)

    details = '\n'.join(f'  - { failure }' for failure in failures)
    message = f'No windowed OpenGL context available:\n{ details }'
    raise GLContextError(message)


def describe(context: 'moderngl.Context') -> dict[str, str]:
    """
    Summarize the capabilities of a context, for diagnostic purposes.

    Args:
        context: The context to interrogate.

    Returns:
        Mapping of capability names to their values, as strings.

    """
    info = context.info

    return {
        'vendor': str(info.get('GL_VENDOR', 'unknown')),
        'renderer': str(info.get('GL_RENDERER', 'unknown')),
        'version': str(info.get('GL_VERSION', 'unknown')),
        'version_code': str(context.version_code),
        'max_samples': str(info.get('GL_MAX_SAMPLES', 0)),
        'max_texture_size': str(info.get('GL_MAX_TEXTURE_SIZE', 0)),
    }
