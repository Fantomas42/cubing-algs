"""
Diagnostic of the GPU rendering backend.

Answers a single question: can this machine render, and how?

    python -m cubing_algs.display.gl.doctor

It reports the availability of the optional dependencies, the
capabilities of every context it manages to create, and writes a
gradient PNG rendered by the GPU, so that the whole chain is checked, up
to the encoded file.
"""
import argparse
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from cubing_algs.display.gl.constants import OPENGL_EXTRA
from cubing_algs.display.gl.constants import RENDER_SIZE
from cubing_algs.display.gl.context import GLContextError
from cubing_algs.display.gl.context import create_standalone_context
from cubing_algs.display.gl.context import create_window
from cubing_algs.display.gl.context import create_window_context
from cubing_algs.display.gl.context import describe
from cubing_algs.display.gl.context import destroy_window
from cubing_algs.display.gl.context import has_glfw
from cubing_algs.display.gl.context import has_moderngl
from cubing_algs.display.gl.encode import write_png

if TYPE_CHECKING:  # pragma: no cover
    import moderngl

DOCTOR_OUTPUT = str(Path(tempfile.gettempdir()) / 'gl-doctor.png')

GRADIENT_VERTEX_SHADER = """
#version 330

out vec2 v_uv;

void main() {
    // Fullscreen triangle generated from the vertex index alone,
    // so the check needs no vertex buffer at all.
    vec2 corner = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
    v_uv = corner;
    gl_Position = vec4(corner * 2.0 - 1.0, 0.0, 1.0);
}
"""

GRADIENT_FRAGMENT_SHADER = """
#version 330

in vec2 v_uv;
out vec4 f_color;

void main() {
    f_color = vec4(v_uv.x, v_uv.y, 1.0 - v_uv.x * v_uv.y, 1.0);
}
"""


def output(text: str = '') -> None:
    """Write a line to standard output."""
    sys.stdout.write(text + '\n')


def report(label: str, context: 'moderngl.Context') -> None:
    """
    Print the capabilities of a context under a given label.

    Args:
        label: Heading naming the kind of context.
        context: The context to interrogate.

    """
    output(label)
    for key, value in describe(context).items():
        output(f'  {key:<18}: { value }')


def render_gradient(context: 'moderngl.Context', size: int) -> bytes:
    """
    Render a fullscreen gradient offscreen and read the pixels back.

    Args:
        context: The context to render with.
        size: Side of the square image, in pixels.

    Returns:
        The RGBA bytes of the framebuffer, bottom row first.

    """
    import moderngl

    program = context.program(
        vertex_shader=GRADIENT_VERTEX_SHADER,
        fragment_shader=GRADIENT_FRAGMENT_SHADER,
    )

    texture = context.texture((size, size), 4)
    framebuffer = context.framebuffer(color_attachments=[texture])
    framebuffer.use()
    framebuffer.clear(0.0, 0.0, 0.0, 1.0)

    vertex_array = context.vertex_array(program, [])
    vertex_array.render(moderngl.TRIANGLES, vertices=3)

    pixels = bytes(framebuffer.read(components=4))

    vertex_array.release()
    framebuffer.release()
    texture.release()
    program.release()

    return pixels


def check_dependencies() -> None:
    """Print the availability of the optional dependencies."""
    output(f'Dependencies (extra: { OPENGL_EXTRA })')

    for module, available in (
            ('moderngl', has_moderngl()),
            ('glfw', has_glfw()),
    ):
        state = 'available' if available else 'MISSING'
        output(f'  {module:<18}: { state }')

    output()


def check_standalone(destination: str, size: int) -> bool:
    """
    Check the headless context and write the gradient it renders.

    Args:
        destination: Where to write the gradient PNG.
        size: Side of the square image, in pixels.

    Returns:
        True when offscreen rendering works end to end.

    """
    try:
        context = create_standalone_context()
    except GLContextError as error:
        output(f'Standalone context (headless): UNAVAILABLE\n  { error }')
        output()
        return False

    report('Standalone context (headless)', context)

    written = write_png(
        destination,
        render_gradient(context, size),
        (size, size),
    )
    output(f'  {"gradient":<18}: { written } ({ size }x{ size })')
    output()

    context.release()

    return True


def check_window(size: int) -> bool:
    """
    Check that a windowed context can be created, without showing it.

    Args:
        size: Side of the square window, in pixels.

    Returns:
        True when the interactive viewer can run here.

    """
    try:
        window = create_window((size, size), visible=False)
        context = create_window_context()
    except GLContextError as error:
        output(f'Window context (glfw): UNAVAILABLE\n  { error }')
        output()
        return False

    report('Window context (glfw)', context)
    output()

    context.release()
    destroy_window(window)

    return True


def build_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser of the doctor command.

    Returns:
        The parser of the command line options.

    """
    parser = argparse.ArgumentParser(
        prog='python -m cubing_algs.display.gl.doctor',
        description='Diagnose the GPU rendering backend of cubing-algs.',
    )
    parser.add_argument(
        '--out',
        default=DOCTOR_OUTPUT,
        help=f'where to write the gradient PNG (default: { DOCTOR_OUTPUT })',
    )
    parser.add_argument(
        '--size',
        type=int,
        default=RENDER_SIZE,
        help=f'size in pixels of the gradient (default: { RENDER_SIZE })',
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run the diagnostic.

    Args:
        argv: Command line arguments, defaulting to those of the process.

    Returns:
        The shell exit code, 0 when offscreen rendering works.

    """
    options = build_parser().parse_args(argv)

    output('cubing-algs GPU doctor')
    output()

    check_dependencies()

    standalone = check_standalone(options.out, options.size)
    window = check_window(options.size)

    if not standalone:
        output(
            'No OpenGL context at all.'
            if not window
            else 'Offscreen rendering is unavailable on this machine.',
        )
        return 1

    if not window:
        output('The interactive viewer is unavailable on this machine.')

    return 0


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
