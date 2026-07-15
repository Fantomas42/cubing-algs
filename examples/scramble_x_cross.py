"""
Example usage of scramble_x_cross() function.

This demonstrates how to generate x-cross scrambles with solutions
for practicing the x-cross step in CFOP method.

The scramble_x_cross() function returns both a scramble and
the corresponding solution to solve the cross + preserved F2L pairs.

Supports:
- x-cross: 1 preserved slot (cross + 1 F2L pair)
- xx-cross: 2 preserved slots (cross + 2 F2L pairs)
- xxx-cross: 3 preserved slots (cross + 3 F2L pairs)

Usage:
    python scramble_x_cross.py                     # Run with default settings
    python scramble_x_cross.py -d easy             # Easy difficulty
    python scramble_x_cross.py -d normal           # Normal difficulty
    python scramble_x_cross.py -d hard             # Hard difficulty
    python scramble_x_cross.py -s FL               # Target front-left slot
    python scramble_x_cross.py -s FR FL            # xx-cross (two slots)
    python scramble_x_cross.py -s FR FL BR         # xxx-cross (three slots)
    python scramble_x_cross.py --seed 123          # Set random seed
    python scramble_x_cross.py -n 5                # Generate 5 scrambles
    python scramble_x_cross.py -o UF               # Orient with white on top
    python scramble_x_cross.py -o RD               # Orient with red on top
"""

import argparse
from random import Random

from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.constants import ORIENTATIONS
from cubing_algs.scrambler.steps import scramble_x_cross
from cubing_algs.vcube import VCube

DIFFICULTIES = ['easy', 'normal', 'hard']
SLOTS = ['FR', 'FL', 'BR', 'BL']

CROSS_NAMES = {
    1: 'x-cross',
    2: 'xx-cross',
    3: 'xxx-cross',
}


def show_x_cross(
    difficulty: str,
    slots: list[str],
    rng: Random,
    orientation: str,
) -> None:
    """Display an x-cross scramble with cube visualization."""
    scramble, solution = scramble_x_cross(
        difficulty=difficulty, slots=slots, rng=rng,
    )

    rotation = ORIENTATION_FACE_MOVES[orientation]
    prefix = f'{rotation} ' if rotation else ''
    cross_name = CROSS_NAMES.get(len(slots), 'x-cross')

    print(f'\n   Type: {cross_name}')
    print(f'   Difficulty: {difficulty}')
    print(f'   Slots: {", ".join(slots)}')
    print(f'   Scramble: {prefix}{scramble}')
    print(f'   Scramble moves: {len(scramble)}')
    print(f'   Solution: {solution}')
    print(f'   Solution moves: {len(solution)}')

    # Show scrambled state
    cube = VCube()
    cube.rotate(rotation + scramble)
    print('\n   Scrambled state:')
    cube.show(mode='cross')

    # Show state after solution
    cube_solved = VCube()
    cube_solved.rotate(rotation + scramble + solution)
    print(f'\n   After {cross_name} solution:')
    cube_solved.show(mode='f2l')


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
        description='Generate x-cross scrambles with solutions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Default (normal, FR slot)
  %(prog)s -d easy                  Easy difficulty
  %(prog)s -d hard                  Hard difficulty
  %(prog)s -s FL                    Target front-left slot
  %(prog)s -s FR FL                 xx-cross (two slots)
  %(prog)s -s FR FL BR              xxx-cross (three slots)
  %(prog)s --seed 123               Set random seed for reproducibility
  %(prog)s -n 5                     Generate 5 scrambles
  %(prog)s -d easy -s FR FL -n 3    3 easy xx-cross scrambles
""",
    )

    parser.add_argument(
        '-d', '--difficulty',
        choices=DIFFICULTIES,
        default='normal',
        help='Difficulty level: easy, normal, hard (default: normal)',
    )

    parser.add_argument(
        '-s', '--slots',
        choices=SLOTS,
        nargs='+',
        default=['FR'],
        help='F2L slots to preserve: FR, FL, BR, BL (default: FR)',
    )

    parser.add_argument(
        '--seed',
        help='Random seed for reproducibility',
    )

    parser.add_argument(
        '-o', '--orientation',
        choices=ORIENTATIONS,
        default='DF',
        metavar='ORIENTATION',
        help='Cube orientation, e.g. DF, UF, RD (default: DF)',
    )

    parser.add_argument(
        '-n', '--count',
        type=int,
        default=1,
        help='Number of scrambles to generate (default: 1)',
    )

    return parser.parse_args()


def main() -> None:
    """Run the x-cross scramble demo."""
    args = parse_args()

    rng = Random(args.seed)  # noqa: S311

    cross_name = CROSS_NAMES.get(len(args.slots), 'x-cross')
    section(
        f'{cross_name.upper()} Scrambles'
        f' - {args.difficulty.capitalize()} Difficulty'
        f' - Slots {", ".join(args.slots)}',
    )

    print(f'\nGenerates scrambles with solutions for practicing {cross_name}.')

    for i in range(args.count):
        if args.count > 1:
            print(f'\n--- Scramble {i + 1} of {args.count} ---')
        show_x_cross(args.difficulty, args.slots, rng, args.orientation)

    print('\n' + '=' * 60)
    print('Notes:')
    print('  - Solution length scales with number of preserved slots')
    print('  - x-cross: cross + 1 F2L pair')
    print('  - xx-cross: cross + 2 F2L pairs')
    print('  - xxx-cross: cross + 3 F2L pairs')
    print('=' * 60)


if __name__ == '__main__':
    main()
