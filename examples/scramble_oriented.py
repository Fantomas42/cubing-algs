# ruff: noqa: T201
"""
Example usage of scramble_edges_oriented() function.

This demonstrates how to generate scrambles for a 3x3x3 cube
with all edges oriented (ZZ/EO-first method practice).

Usage:
    python scramble_oriented.py                 # Run with default settings
    python scramble_oriented.py --seed 123      # Set random seed
    python scramble_oriented.py -n 5            # Generate 5 scrambles
    python scramble_oriented.py -i 20           # 20-move scramble
"""

import argparse
from random import Random

from cubing_algs.constants import EDGE_NAMES
from cubing_algs.scrambler.steps import scramble_edges_oriented
from cubing_algs.vcube import VCube

RESET = '\x1b[0m'
BOLD = '\x1b[1m'

FG_RED = '\x1b[38;5;203m'
FG_GREEN = '\x1b[38;5;77m'
FG_GREY = '\x1b[38;5;244m'


def colorize(text: str, color: str) -> str:
    """
    Wrap text with an ANSI color code and reset.

    Returns:
        ANSI-colored string.

    """
    return f'{color}{text}{RESET}'


def format_eo_bar(eo: list[int]) -> str:
    """
    Build a compact edge-orientation bar.

    Each edge slot shows its name in green (oriented) or red+bold
    (flipped), followed by a bad-edge count summary.

    Returns:
        Formatted string with colored edge names and a count summary.

    """
    parts: list[str] = []
    bad = 0
    for i, val in enumerate(eo):
        name = EDGE_NAMES[i]
        if val == 0:
            parts.append(colorize(name, FG_GREEN))
        else:
            parts.append(colorize(name, FG_RED + BOLD))
            bad += 1

    groups = [' '.join(parts[:4]), ' '.join(parts[4:8]), ' '.join(parts[8:])]
    bar = colorize(' │ ', FG_GREY).join(groups)

    count_color = FG_GREEN if bad == 0 else FG_RED
    summary = colorize(f'{bad}/12 bad', count_color + BOLD)
    return f'{bar}  {summary}'


def show_scramble(iterations: int | None, rng: Random) -> None:
    """Display an edges-oriented scramble with EO status."""
    scramble = scramble_edges_oriented(iterations=iterations, rng=rng)

    print(f'\n   Scramble: {scramble}')
    print(f'   Moves: {len(scramble)}')

    cube = VCube(size=3)
    cube.rotate(scramble)
    _, _, _, eo, *_ = cube.cubies

    eo_label = colorize(f'   {"EO":<14}', FG_GREY)
    print(f'{eo_label} {format_eo_bar(list(eo))}')


def section(title: str) -> None:
    """Print a section header."""
    print('=' * 60)
    print(title)
    print('=' * 60)


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace.

    """
    parser = argparse.ArgumentParser(
        description='Generate scrambles with all edges oriented.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      Run with default settings
  %(prog)s --seed 123           Set random seed for reproducibility
  %(prog)s -n 5                 Generate 5 scrambles
  %(prog)s -i 20                Use 20-move scrambles
""",
    )

    parser.add_argument(
        '--seed',
        help='Random seed for reproducibility',
    )

    parser.add_argument(
        '-n', '--count',
        type=int,
        default=1,
        help='Number of scrambles to generate (default: 1)',
    )

    parser.add_argument(
        '-i', '--iterations',
        type=int,
        default=None,
        help='Number of moves in the scramble (default: automatic)',
    )

    return parser.parse_args()


def main() -> None:
    """Run the edges-oriented scramble demo."""
    args = parse_args()

    rng = Random(args.seed)  # noqa: S311

    section('Edges Oriented Scrambles')
    print('\nAll edges are oriented (good for ZZ / EO-first practice).')
    print('Green = oriented, Red = flipped.')

    for i in range(args.count):
        if args.count > 1:
            print(f'\n--- Scramble {i + 1} of {args.count} ---')
        show_scramble(args.iterations, rng)

    print('\n' + '=' * 60)
    print('Notes:')
    print('  - All 12 edges are oriented relative to the F/B axis')
    print('  - Only R, U, L, D, F2, B2 moves preserve edge orientation')
    print('=' * 60)


if __name__ == '__main__':
    main()
