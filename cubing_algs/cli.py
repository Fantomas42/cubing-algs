"""
Command line interface for cubing_algs.

Exposes the most common library operations as subcommands of
``python -m cubing_algs``:

- ``parse``: validate and normalize an algorithm
- ``metrics``: compute algorithm metrics (HTM, QTM, STM, ...)
- ``apply``: apply an algorithm on a virtual cube and display it
- ``transform``: apply named transforms to an algorithm
- ``compress``: rewrite an algorithm in commutator/conjugate notation
- ``cases``: list case collections or the cases of a collection
- ``case``: show the details of a single case
- ``info``: export the complete analysis of an algorithm as JSON
"""
import argparse
import json
import logging
import sys
from collections.abc import Callable
from collections.abc import Sequence

from cubing_algs.algorithm import Algorithm
from cubing_algs.cases import get_case
from cubing_algs.cases import get_collection
from cubing_algs.cases import list_collections
from cubing_algs.constants import DEFAULT_CUBE_SIZE
from cubing_algs.exceptions import CubingAlgsError
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

    Returns:
        Process exit code.

    """
    cube = VCube()

    if args.setup:
        cube.rotate(parse_moves(args.setup, trust_input=False))

    cube.rotate(parse_moves(args.moves, trust_input=False))

    sys.stdout.write(
        cube.display(
            mode=args.mode,
            orientation=args.orientation,
            mask=args.mask,
            palette=args.palette,
        ),
    )

    if args.state:
        output(f'Facelets: { cube.state }')
        output(f'Solved:   { "yes" if cube.is_solved else "no" }')

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

    Returns:
        Process exit code.

    """
    case = get_case(args.collection, args.name)

    output(f'Name:        { case.pretty_name }')
    output(f'Probability: { case.probability_label }')
    output(f'Optimal:     htm={ case.optimal_htm } '
           f'stm={ case.optimal_stm } '
           f'cycles={ case.optimal_cycles }')
    output('Algorithms:')
    for algo in case.algorithms:
        output(f'  { algo }')
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
    apply_parser.add_argument('moves', help='Algorithm to apply')
    apply_parser.add_argument(
        '--setup',
        default='',
        help='Moves applied before the algorithm',
    )
    apply_parser.add_argument(
        '--mode',
        default='',
        help='Display mode, e.g. oll, pll, f2l',
    )
    apply_parser.add_argument(
        '--orientation',
        default='',
        help='Display orientation, e.g. DF',
    )
    apply_parser.add_argument('--mask', default='', help='Display mask')
    apply_parser.add_argument('--palette', default='', help='Color palette')
    apply_parser.add_argument(
        '--state',
        action='store_true',
        help='Also print the facelets string and solved status',
    )
    apply_parser.set_defaults(handler=run_apply)

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
    case_parser.set_defaults(handler=run_case)

    info_parser = subparsers.add_parser(
        'info',
        help='Export the complete analysis of an algorithm as JSON',
    )
    info_parser.add_argument('moves', help='Algorithm to analyze')
    info_parser.add_argument(
        '-s', '--size',
        type=int,
        default=DEFAULT_CUBE_SIZE,
        help=f'Cube size (default: { DEFAULT_CUBE_SIZE })',
    )
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
