"""
Command line interface for cubing_algs.

Exposes the most common library operations as subcommands of
``python -m cubing_algs``:

- ``parse``: validate and normalize an algorithm
- ``metrics``: compute algorithm metrics (HTM, QTM, STM, ...)
- ``apply``: apply an algorithm on a virtual cube and display it
- ``animate``: write an algorithm playing on a cube as a GIF
- ``transform``: apply named transforms to an algorithm
- ``compress``: rewrite an algorithm in commutator/conjugate notation
- ``cases``: list case collections or the cases of a collection
- ``case``: show the details of a single case
- ``info``: export the complete analysis of an algorithm as JSON

``apply`` and ``case`` also draw on the GPU rendering backend, which the
``opengl`` extra ships: ``--view`` opens an interactive window, and
``--render`` writes a PNG. Both say so plainly when the extra is missing.
"""
import argparse
import json
import logging
import sys
from collections.abc import Callable
from collections.abc import Sequence
from pathlib import Path

from cubing_algs.algorithm import Algorithm
from cubing_algs.annotations import CubeOrientation
from cubing_algs.cases import get_case
from cubing_algs.cases import get_collection
from cubing_algs.cases import list_collections
from cubing_algs.constants import DEFAULT_CUBE_SIZE
from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.exceptions import CubingAlgsError
from cubing_algs.exceptions import InvalidOrientationError
from cubing_algs.parsing import parse_moves
from cubing_algs.structure import compress
from cubing_algs.transform.auf import remove_auf_moves
from cubing_algs.transform.invert import invert_moves
from cubing_algs.transform.size import compress_moves
from cubing_algs.transform.size import expand_moves
from cubing_algs.transform.symmetry import symmetry_m_moves
from cubing_algs.vcube import VCube

TRANSFORMS: dict[str, Callable[[Algorithm], Algorithm]] = {
    'compress': compress_moves,
    'expand': expand_moves,
    'invert': invert_moves,
    'mirror': symmetry_m_moves,
    'remove-auf': remove_auf_moves,
}

# Nested analysis blocks of Algorithm.to_dict(); the overview scalars
# surrounding them are always emitted as the algorithm identity header.
INFO_SECTIONS: tuple[str, ...] = (
    'metrics',
    'ergonomics',
    'structure',
    'memory',
    'impacts',
)


def output(text: str) -> None:
    """Write a line to standard output."""
    sys.stdout.write(text + '\n')


def window_size(image_size: int) -> tuple[int, int] | None:
    """
    Read the size a window is asked to open at.

    Args:
        image_size: Pixels asked for on the command line, zero for the
            default size of the viewer.

    Returns:
        The width and height of the window, or None to leave the
        default one alone.

    """
    if not image_size:
        return None

    return (image_size, image_size)


def hold_cube(cube: VCube, orientation: CubeOrientation) -> None:
    """
    Turn a cube the way it is held, before anything is played on it.

    An orientation says how the cube is held while the algorithm is
    played, not how the result is looked at: its rotations therefore
    come first, so that ``R`` turns the face on the right of whoever
    holds it. The backends are then handed an already turned cube, and
    no orientation of their own.

    Args:
        cube: The cube to turn, in place.
        orientation: The top and front faces, e.g. ``DF``.

    Raises:
        InvalidOrientationError: If the orientation is not one of the 24.

    """
    if not orientation:
        return

    try:
        moves = ORIENTATION_FACE_MOVES[orientation]
    except KeyError as error:
        msg = f'Invalid orientation "{ orientation }"'
        raise InvalidOrientationError(msg) from error

    if moves:
        cube.rotate(parse_moves(moves))


def setup_cube(args: argparse.Namespace) -> VCube:
    """
    Build the cube a subcommand plays its algorithm on.

    The cube is turned the way ``--orientation`` says it is held before
    ``--setup`` is played on it, so that the setup is made from there.

    Args:
        args: The parsed command line, holding the size, the orientation
            and the setup moves.

    Returns:
        The cube, held and set up, ready for the algorithm.

    """
    cube = VCube(size=args.size)

    hold_cube(cube, args.orientation)

    if args.setup:
        cube.rotate(parse_moves(args.setup, trust_input=False))

    return cube


def view_cube(
        cube: VCube,
        args: argparse.Namespace,
) -> None:
    """
    Open an interactive window on a cube.

    Args:
        cube: The cube to show, already turned the way it is held.
        args: The parsed command line, holding the display options.

    """
    cube.view(
        mode=args.mode,
        mask=args.mask,
        palette=args.palette,
        window_size=window_size(args.image_size),
        rotation=args.rotation,
        distance=args.distance,
    )


def render_cube(
        cube: VCube,
        args: argparse.Namespace,
) -> None:
    """
    Write a PNG of a cube where the command line asks for it.

    Args:
        cube: The cube to draw, already turned the way it is held.
        args: The parsed command line, holding the target and the
            display options.

    """
    path = Path(args.render)
    path.write_bytes(
        cube.render(
            mode=args.mode,
            mask=args.mask,
            palette=args.palette,
            image_size=args.image_size,
            rotation=args.rotation,
            distance=args.distance,
        ),
    )

    output(f'Rendered: { path }')


def animate_cube(
        cube: VCube,
        moves: Algorithm,
        args: argparse.Namespace,
) -> None:
    """
    Write an algorithm playing on a cube where the command line says.

    Args:
        cube: The cube to play the algorithm on, already turned the way
            it is held.
        moves: The algorithm to play.
        args: The parsed command line, holding the target and the
            display options.

    """
    written = cube.animate(
        moves, args.animate,
        mode=args.mode,
        mask=args.mask,
        palette=args.palette,
        image_size=args.image_size,
        rotation=args.rotation,
        distance=args.distance,
    )

    if len(written) == 1:
        output(f'Animated: { written[0] }')
        return

    # Without Pillow around, a whole series of frames comes out rather
    # than a GIF: naming every one of them would bury the point.
    output(
        f'Animated: { len(written) } frames, '
        f'{ written[0] } to { written[-1] }',
    )


def run_parse(args: argparse.Namespace) -> int:
    """
    Validate and normalize an algorithm string.

    Returns:
        Process exit code.

    """
    algo = parse_moves(args.moves, trust_input=False)
    output(str(algo))
    return 0


def run_metrics(args: argparse.Namespace) -> int:
    """
    Compute and display the metrics of an algorithm.

    Returns:
        Process exit code.

    """
    algo = parse_moves(args.moves, trust_input=False)
    metrics = algo.metrics

    output(f'htm:         { metrics.htm }')
    output(f'qtm:         { metrics.qtm }')
    output(f'stm:         { metrics.stm }')
    output(f'etm:         { metrics.etm }')
    output(f'qstm:        { metrics.qstm }')
    output(f'rtm:         { metrics.rtm }')
    output(f'rotations:   { metrics.rotations }')
    output(f'outer_moves: { metrics.outer_moves }')
    output(f'inner_moves: { metrics.inner_moves }')
    output(f'pauses:      { metrics.pauses }')
    output(f'generators:  { " ".join(metrics.generators) }')
    return 0


def run_apply(args: argparse.Namespace) -> int:
    """
    Apply an algorithm on a solved cube and display the result.

    The cube goes to the terminal, unless ``--render`` or ``--view``
    asks the GPU backend for it instead. It is first turned the way
    ``--orientation`` says it is held, so that both the setup and the
    algorithm are played from there.

    Returns:
        Process exit code.

    """
    cube = setup_cube(args)

    cube.rotate(parse_moves(args.moves, trust_input=False))

    if args.render or args.view:
        if args.render:
            render_cube(cube, args)
        if args.view:
            view_cube(cube, args)
    else:
        sys.stdout.write(
            cube.display(
                mode=args.mode,
                mask=args.mask,
                palette=args.palette,
            ),
        )

    if args.state:
        output(f'Facelets: { cube.state }')
        output(f'Solved:   { "yes" if cube.is_solved else "no" }')

    return 0


def run_animate(args: argparse.Namespace) -> int:
    """
    Write an algorithm playing on a cube as an animation.

    A GIF is written when Pillow is around, a numbered PNG frame per
    image otherwise. The cube is first turned the way ``--orientation``
    says it is held, so that both the setup and the algorithm are
    played from there.

    Returns:
        Process exit code.

    """
    animate_cube(
        setup_cube(args),
        parse_moves(args.moves, trust_input=False),
        args,
    )

    return 0


def run_transform(args: argparse.Namespace) -> int:
    """
    Apply a chain of named transforms to an algorithm.

    Returns:
        Process exit code.

    """
    unknown = [name for name in args.names if name not in TRANSFORMS]
    if unknown:
        available = ', '.join(sorted(TRANSFORMS))
        sys.stderr.write(
            f'Error: unknown transform(s): { ", ".join(unknown) }. '
            f'Available: { available }\n',
        )
        return 1

    algo = parse_moves(args.moves, trust_input=False)
    result = algo.transform(
        *[TRANSFORMS[name] for name in args.names],
    )
    output(str(result))
    return 0


def run_compress(args: argparse.Namespace) -> int:
    """
    Rewrite an algorithm using commutator and conjugate notation.

    Detects conjugate [A: B] and commutator [A, B] patterns and prints the
    compressed bracket notation illustrating the algorithm's structure.

    Returns:
        Process exit code.

    """
    algo = parse_moves(args.moves, trust_input=False)
    output(compress(algo))
    return 0


def run_cases(args: argparse.Namespace) -> int:
    """
    List collections, or the cases of one collection.

    Returns:
        Process exit code.

    """
    if not args.collection:
        for name in list_collections():
            collection = get_collection(name)
            output(f'{ name } ({ collection.size } cases)')
        return 0

    collection = get_collection(args.collection)
    for case in collection.cases.values():
        output(f'{ case.pretty_name }: { case.main_algorithm }')
    return 0


def run_case(args: argparse.Namespace) -> int:
    """
    Show the details of a single case.

    A case is drawn on a cube set up to it, which is the main algorithm
    played backwards, under the display mode of the step it belongs to.
    ``--animate`` then plays the main algorithm from there, which is the
    case being solved. The cube is first turned the way
    ``--orientation`` says it is held, so that the case is set up, and
    solved back, from there.

    Returns:
        Process exit code.

    """
    case = get_case(args.collection, args.name)

    output(f'Name:        { case.pretty_name }')
    output(f'Probability: { case.probability_label }')
    output(f'Optimal:     htm={ case.optimal_htm } '
           f'stm={ case.optimal_stm } '
           f'cycles={ case.optimal_cycles }')
    output(f'Main:        { case.main_algorithm }')
    output('Algorithms:')
    for algo in case.algorithms:
        output(f'  { algo }')

    if args.render or args.animate or args.view:
        cube = VCube()

        hold_cube(cube, args.orientation)

        cube.rotate(case.main_algorithm.transform(invert_moves))

        # A case carries no display mode of its own on the command line:
        # it is drawn under the mode of the step it belongs to.
        args.mode = case.step.lower()

        if args.render:
            render_cube(cube, args)
        if args.animate:
            animate_cube(cube, case.main_algorithm, args)
        if args.view:
            view_cube(cube, args)

    return 0


def run_info(args: argparse.Namespace) -> int:
    """
    Export the complete analysis of an algorithm as JSON.

    The output is the full ``Algorithm.to_dict()`` payload. When one or
    more sections are requested, only those analysis blocks are kept while
    the overview scalars are always emitted as the identity header.

    Returns:
        Process exit code.

    """
    algo = parse_moves(args.moves, trust_input=False)
    data = algo.to_dict(args.size)

    if args.section:
        requested = [
            name.strip()
            for name in args.section.split(',')
            if name.strip()
        ]
        unknown = [name for name in requested if name not in INFO_SECTIONS]
        if unknown:
            available = ', '.join(INFO_SECTIONS)
            sys.stderr.write(
                f'Error: unknown section(s): { ", ".join(unknown) }. '
                f'Available: { available }\n',
            )
            return 1
        data = {
            key: value
            for key, value in data.items()
            if key not in INFO_SECTIONS or key in requested
        }

    output(json.dumps(data, indent=2))
    return 0


def add_orientation_argument(parser: argparse.ArgumentParser) -> None:
    """
    Add the orientation a cube is held in to a subcommand.

    Args:
        parser: The subcommand parser to add it to.

    """
    parser.add_argument(
        '--orientation',
        default='',
        help='Orientation the cube is held in, e.g. DF',
    )


def add_palette_argument(parser: argparse.ArgumentParser) -> None:
    """
    Add the colors a cube is painted with to a subcommand.

    Args:
        parser: The subcommand parser to add it to.

    """
    parser.add_argument('--palette', default='', help='Color palette')


def add_size_argument(parser: argparse.ArgumentParser) -> None:
    """
    Add the number of cubies an edge counts to a subcommand.

    Args:
        parser: The subcommand parser to add it to.

    """
    parser.add_argument(
        '-s', '--size',
        type=int,
        default=DEFAULT_CUBE_SIZE,
        help=f'Cube size (default: { DEFAULT_CUBE_SIZE })',
    )


def add_cube_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add the options describing the cube an algorithm is played on.

    They say which cube is built, how it is held, and how it is looked
    at, whichever backend ends up drawing it.

    Args:
        parser: The subcommand parser to add them to.

    """
    parser.add_argument(
        '--setup',
        default='',
        help='Moves applied before the algorithm',
    )
    add_size_argument(parser)
    parser.add_argument(
        '--mode',
        default='',
        help='Display mode, e.g. oll, pll, f2l',
    )
    add_orientation_argument(parser)
    parser.add_argument('--mask', default='', help='Display mask')
    add_palette_argument(parser)


def add_framing_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add the options framing a GPU rendering to a subcommand.

    ``--image-size`` counts pixels, where ``--size`` counts the cubies
    of an edge: the two never mean the same thing anywhere in the CLI.

    Args:
        parser: The subcommand parser to add them to.

    """
    parser.add_argument(
        '--image-size',
        type=int,
        default=0,
        metavar='PIXELS',
        help='Width and height of the image, or of the window',
    )
    parser.add_argument(
        '--rotation',
        default='',
        help="Camera rotation string, e.g. 'y45x-34'",
    )
    parser.add_argument(
        '--distance',
        type=float,
        default=0.0,
        help='Camera distance from the cube center',
    )


def add_gl_arguments(
        parser: argparse.ArgumentParser,
        *,
        animate: bool = False,
) -> None:
    """
    Add the GPU rendering options to a subcommand.

    The backend they reach lives in the ``opengl`` extra, which nothing
    else in the CLI needs: without it, these options are the only ones
    to fail, and they say what to install.

    Args:
        parser: The subcommand parser to add them to.
        animate: Whether the subcommand can also write an animation.

    """
    parser.add_argument(
        '--view',
        action='store_true',
        help='Open an interactive 3D window on the cube',
    )
    parser.add_argument(
        '--render',
        default='',
        metavar='PATH',
        help='Write a 3D rendering of the cube as a PNG file',
    )

    if animate:
        parser.add_argument(
            '--animate',
            default='',
            metavar='PATH',
            help='Write the algorithm playing on the cube as a GIF',
        )

    add_framing_arguments(parser)


def add_apply_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Add the options of the apply subcommand to its parser.

    Args:
        parser: The subcommand parser to add them to.

    """
    parser.add_argument('moves', help='Algorithm to apply')
    add_cube_arguments(parser)
    parser.add_argument(
        '--state',
        action='store_true',
        help='Also print the facelets string and solved status',
    )
    add_gl_arguments(parser)


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command line argument parser.

    Returns:
        The configured argument parser.

    """
    parser = argparse.ArgumentParser(
        prog='python -m cubing_algs',
        description="Inspect and manipulate Rubik's cube algorithms.",
    )
    subparsers = parser.add_subparsers(required=True)

    parse_parser = subparsers.add_parser(
        'parse',
        help='Validate and normalize an algorithm',
    )
    parse_parser.add_argument('moves', help='Algorithm, e.g. "R U R\' U\'"')
    parse_parser.set_defaults(handler=run_parse)

    metrics_parser = subparsers.add_parser(
        'metrics',
        help='Compute algorithm metrics (HTM, QTM, STM, ...)',
    )
    metrics_parser.add_argument('moves', help='Algorithm to analyze')
    metrics_parser.set_defaults(handler=run_metrics)

    apply_parser = subparsers.add_parser(
        'apply',
        help='Apply an algorithm on a solved cube and display it',
    )
    add_apply_arguments(apply_parser)
    apply_parser.set_defaults(handler=run_apply)

    animate_parser = subparsers.add_parser(
        'animate',
        help='Write an algorithm playing on a cube as a GIF',
    )
    animate_parser.add_argument('moves', help='Algorithm to play')
    # Where an animation lands is spelled --out here and --animate on a
    # case: one destination, so that animate_cube reads it in one place.
    animate_parser.add_argument(
        '--out',
        dest='animate',
        required=True,
        metavar='PATH',
        help='Where the animation is written',
    )
    add_cube_arguments(animate_parser)
    add_framing_arguments(animate_parser)
    animate_parser.set_defaults(handler=run_animate)

    transform_parser = subparsers.add_parser(
        'transform',
        help='Apply named transforms to an algorithm',
    )
    transform_parser.add_argument('moves', help='Algorithm to transform')
    transform_parser.add_argument(
        'names',
        nargs='+',
        metavar='transform',
        help=f'Transforms to chain: { ", ".join(sorted(TRANSFORMS)) }',
    )
    transform_parser.set_defaults(handler=run_transform)

    compress_parser = subparsers.add_parser(
        'compress',
        help='Rewrite an algorithm in commutator/conjugate notation',
    )
    compress_parser.add_argument('moves', help='Algorithm to compress')
    compress_parser.set_defaults(handler=run_compress)

    cases_parser = subparsers.add_parser(
        'cases',
        help='List collections, or the cases of one collection',
    )
    cases_parser.add_argument(
        'collection',
        nargs='?',
        default='',
        help='Collection name, e.g. OLL or CFOP/OLL',
    )
    cases_parser.set_defaults(handler=run_cases)

    case_parser = subparsers.add_parser(
        'case',
        help='Show the details of a single case',
    )
    case_parser.add_argument('collection', help='Collection name, e.g. OLL')
    case_parser.add_argument('name', help='Case name or code, e.g. 27')
    add_orientation_argument(case_parser)
    add_palette_argument(case_parser)
    add_gl_arguments(case_parser, animate=True)
    # A case is drawn under the mode of its own step, which run_case
    # fills in, and through no mask of its own: those two display
    # options the GPU helpers read are therefore defaulted here.
    case_parser.set_defaults(
        handler=run_case,
        mode='',
        mask='',
    )

    info_parser = subparsers.add_parser(
        'info',
        help='Export the complete analysis of an algorithm as JSON',
    )
    info_parser.add_argument('moves', help='Algorithm to analyze')
    add_size_argument(info_parser)
    info_parser.add_argument(
        '--section',
        default='',
        help=(
            'Comma-separated analysis sections to keep '
            f'({ ", ".join(INFO_SECTIONS) }); '
            'overview fields are always present'
        ),
    )
    info_parser.set_defaults(handler=run_info)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run the command line interface.

    Returns:
        Process exit code.

    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # The CLI reports errors itself; silence the library's log duplicate
    logging.getLogger('cubing_algs').setLevel(logging.CRITICAL)

    try:
        return int(args.handler(args))
    except CubingAlgsError as error:
        sys.stderr.write(f'Error: { error }\n')
        return 1
