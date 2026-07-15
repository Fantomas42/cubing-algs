"""
Example usage of scramble_f2l() function.

This demonstrates how to generate F2L scrambles for practicing
individual F2L slots in the CFOP method.

The scramble_f2l() function returns a scramble that keeps the cross
solved while scrambling the specified F2L slot(s).

Supports:
- Single slot: scramble one F2L pair (e.g., FR)
- Multiple slots: scramble several F2L pairs (e.g., FR, FL)

Usage:
    python scramble_f2l.py                     # Run with default settings
    python scramble_f2l.py -s FL               # Target front-left slot
    python scramble_f2l.py -s FR FL            # Scramble two slots
    python scramble_f2l.py -s FR FL BR         # Scramble three slots
    python scramble_f2l.py -s FR FL BR BL      # Scramble all four slots
    python scramble_f2l.py --seed 123          # Set random seed
    python scramble_f2l.py -n 5                # Generate 5 scrambles
    python scramble_f2l.py -o UF               # Orient with white on top
    python scramble_f2l.py -o RD               # Orient with red on top
"""

import argparse
from random import Random

from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.constants import ORIENTATIONS
from cubing_algs.scrambler.steps import scramble_f2l
from cubing_algs.vcube import VCube

SLOTS = ['FR', 'FL', 'BR', 'BL']


def show_f2l(slots: list[str], rng: Random, orientation: str) -> None:
    """Display an F2L scramble with cube visualization."""
    scramble = scramble_f2l(slots=slots, rng=rng)

    slot_count = len(slots)
    rotation = ORIENTATION_FACE_MOVES[orientation]

    suffix = 's' if slot_count > 1 else ''
    print(f'\n   Slots: {", ".join(slots)} ({slot_count} pair{suffix})')
    prefix = f'{rotation} ' if rotation else ''
    print(f'   Scramble: {prefix}{scramble}')
    print(f'   Scramble moves: {len(scramble)}')

    # Show scrambled state
    cube = VCube()
    cube.rotate(rotation + scramble)
    print('\n   Scrambled state:')
    cube.show(mode='f2l')


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
        description='Generate F2L scrambles for practicing individual slots.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s                          Default (FR slot, DF orientation)
  %(prog)s -s FL                    Target front-left slot
  %(prog)s -s FR FL                 Scramble two slots
  %(prog)s -s FR FL BR              Scramble three slots
  %(prog)s -s FR FL BR BL           Scramble all four slots
  %(prog)s --seed 123               Set random seed for reproducibility
  %(prog)s -n 5                     Generate 5 scrambles
  %(prog)s -s FR FL -n 3            3 scrambles for FR and FL slots
  %(prog)s -o UF                    Orient with white on top (UF)
  %(prog)s -o RD                    Orient with red on top
""",
    )

    parser.add_argument(
        '-s', '--slots',
        choices=SLOTS,
        nargs='+',
        default=['FR'],
        help='F2L slots to scramble: FR, FL, BR, BL (default: FR)',
    )

    parser.add_argument(
        '-o', '--orientation',
        choices=ORIENTATIONS,
        default='DF',
        metavar='ORIENTATION',
        help='Cube orientation, e.g. DF, UF, RD (default: DF)',
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

    return parser.parse_args()


def main() -> None:
    """Run the F2L scramble demo."""
    args = parse_args()

    rng = Random(args.seed)  # noqa: S311

    section(
        f'F2L Scrambles - Slots {", ".join(args.slots)}',
    )

    suffix = 's' if len(args.slots) > 1 else ''
    print(f'\nGenerates scrambles for practicing F2L slot{suffix}.')
    print('Cross remains solved; only the specified slot(s) are scrambled.')

    for i in range(args.count):
        if args.count > 1:
            print(f'\n--- Scramble {i + 1} of {args.count} ---')
        show_f2l(args.slots, rng, args.orientation)

    print('\n' + '=' * 60)
    print('Notes:')
    print('  - Cross stays solved, only specified F2L pairs are scrambled')
    print('  - Valid slots: FR (front-right), FL (front-left),')
    print('                 BR (back-right), BL (back-left)')
    print('  - Default orientation is DF (white on bottom); use -o to change')
    print('=' * 60)


if __name__ == '__main__':
    main()
