"""
Play an algorithm in a window with a transparent background.

Written as a **subclass of ``GlfwHost``**, and that is the whole point
of it: the window, the loop, the timing, the vsync, the mouse, the
transparent visual and the offscreen detour it imposes all belong to the
backend, and what is left here is what belongs to this demo alone - an
algorithm that loops, and a camera that turns by itself. Both are
layered on ``frame()``, the one seam a host offers, and nothing else is
written twice.

It used to be a host of its own, some four hundred lines of window,
context, event translation and offscreen resolve, for one reason:
``create_window()`` did not offer the three hints a transparent window
needs. It does now - ``GlfwHost(viewer, transparent=True)`` is the whole
of it - and every line those four hundred held has gone back where it
was already written once.

On some drivers a transparent visual and a multisampled window
framebuffer are mutually exclusive: asking for both gets the
transparency refused. The host therefore draws the cube into an
offscreen multisampled target and copies it to the screen. ``--no-msaa``
draws straight into the window instead, aliased but with nothing in
between.

What the cube shows is said in the vocabulary of the command line:
``--setup``, ``--size``, ``--orientation``, ``--mode``, ``--mask`` and
``--palette`` mean here exactly what they mean in
``python -m cubing_algs apply``, so that a window and a PNG asked for the
same way hold the same picture. The orientation is absorbed on the
``VCube`` side, before the algorithm is played, so that ``R`` turns the
face on the right of whoever holds the cube.

A window with no decoration has no title bar to grab, so **Ctrl and the
left button carry the window** across the screen, where the left button
alone orbits the cube as it does in every window the library opens. X11
lets an application place itself, which is what the backend gives us
here, and what a native Wayland would silently ignore.
"""
import argparse
import logging
import math
import sys
from dataclasses import dataclass

from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.display.gl import Viewer
from cubing_algs.display.gl.host import GlfwHost
from cubing_algs.display.mode import MODE_CONFIGS
from cubing_algs.display.palettes import PALETTES
from cubing_algs.exceptions import CubingAlgsError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

WINDOW_TITLE = 'transparent cube'

FULL_TURN = 2 * math.pi

DEFAULT_MOVES = "R U R' U'"
DEFAULT_CUBE_SIZE = 3
DEFAULT_WINDOW_SIZE = 400
DEFAULT_SPEED = 0.35
DEFAULT_SPIN = 0.25

EPILOG = """\
examples:
  %(prog)s "R U R' U'"
  %(prog)s "R U R' U'" --size 5 --window 700
  %(prog)s "F R U R' U' F'" --setup "F U R U' R' F'" --mode oll
  %(prog)s "R U R' U' R' F R2 U' R' U' R U R' F'" --mode pll
  %(prog)s "M2 E2 S2" --opaque --palette rgb
"""


@dataclass
class LoopingHost(GlfwHost):
    """
    A window playing an algorithm over and over, turning as it goes.

    Everything a window is made of is inherited. What is added is the
    two things this demo is about, and they are both layered on
    ``frame()``: the algorithm pushed again once the cube has finished
    playing it, and the camera walking around the cube while nobody is
    dragging it.
    """

    # The algorithm the cube loops on. A field with a default, as every
    # field of a dataclass subclass must be, the parent carrying
    # defaults of its own.
    moves: str = DEFAULT_MOVES

    # Radians a second the camera drifts by, zero holding it still.
    spin: float = DEFAULT_SPIN

    def replay(self) -> None:
        """
        Push the algorithm again once the cube has finished playing it.

        The viewer picks the cube up where the last run left it, so the
        algorithm loops on the state it leads to rather than on a cube
        put back together behind the scenes.
        """
        viewer = self.viewer

        if viewer.animation.finished and not viewer.pending:
            viewer.push(self.moves)

    def orbit(self, delta: float) -> None:
        """
        Turn the camera around the cube, unless the mouse is holding it.

        Args:
            delta: Seconds gone by since the last frame.

        """
        if not self.spin or self.dragging:
            return

        camera = self.viewer.camera
        camera.yaw = (camera.yaw + self.spin * delta) % FULL_TURN

    def frame(self, delta: float) -> None:
        """
        Draw one frame, the algorithm and the drift brought up to date.

        The seam of the host, and the whole of what this demo writes:
        the loop, the timing, the swap, the events and the offscreen
        resolve are the parent's and are inherited untouched.

        Args:
            delta: Seconds gone by since the last frame.

        """
        self.replay()
        self.orbit(delta)

        super().frame(delta)


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
    # A compositor refusing the transparency says so through the logging
    # of the backend, and a demo about a transparent window is the one
    # place that line has to be readable.
    logging.basicConfig(level=logging.INFO, format='%(message)s')

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

    LoopingHost(
        viewer,
        title=WINDOW_TITLE,
        transparent=not args.opaque,
        msaa=not args.no_msaa,
        moves=str(algo),
        spin=args.spin,
    ).run()

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except CubingAlgsError as error:
        sys.exit(f'Error: { error }')
