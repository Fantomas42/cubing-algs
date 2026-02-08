# ruff: noqa: T201
"""
Example usage of scramble_x_cross() function.

This demonstrates how to generate x-cross scrambles with solutions
for practicing the x-cross step in CFOP method.

The scramble_x_cross() function returns both a scramble and
the corresponding solution to solve the x-cross (cross + one F2L pair).

Usage:
    python scramble_x_cross.py                 # Run with default settings
    python scramble_x_cross.py -d easy         # Easy difficulty (5 moves)
    python scramble_x_cross.py -d normal       # Normal difficulty (10 moves)
    python scramble_x_cross.py -d hard         # Hard difficulty (15 moves)
    python scramble_x_cross.py -s FL            # Target front-left slot
    python scramble_x_cross.py --seed 123      # Set random seed
    python scramble_x_cross.py -n 5            # Generate 5 scrambles
"""

import argparse
from random import Random

from cubing_algs.scrambler.steps import scramble_x_cross
from cubing_algs.vcube import VCube

DIFFICULTIES = ['easy', 'normal', 'hard']
SLOTS = ['FR', 'FL', 'BR', 'BL']


def show_x_cross(difficulty: str, slot: str, rng: Random) -> None:
    """Display an x-cross scramble with cube visualization."""
    scramble, solution = scramble_x_cross(
        difficulty=difficulty, slot=slot, rng=rng,
    )

    print(f'\n   Difficulty: {difficulty}')
    print(f'   Slot: {slot}')
    print(f'   Scramble: z2 {scramble}')
    print(f'   Scramble moves: {len(scramble)}')
    print(f'   Solution: {solution}')
    print(f'   Solution moves: {len(solution)}')

    # Show scrambled state
    cube = VCube()
    cube.rotate('z2' + scramble)
    print('\n   Scrambled state:')
    cube.show(mode='cross')

    # Show state after x-cross solution
    # (cross + one F2L pair solved, rest still scrambled)
    cube_solved = VCube()
    cube_solved.rotate('z2' + scramble + solution)
    print('\n   After x-cross solution (cross + one F2L pair solved):')
    cube_solved.show(mode='f2l')


def section(title: str) -> None:
    """Print a section header."""
    print('\n' + '=' * 60)
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
  %(prog)s                      Run with default settings (normal difficulty)
  %(prog)s -d easy              Easy difficulty (5 moves)
  %(prog)s -d normal            Normal difficulty (10 moves)
  %(prog)s -d hard              Hard difficulty (15 moves)
  %(prog)s -s FL                Target front-left F2L slot
  %(prog)s --seed 123           Set random seed for reproducibility
  %(prog)s -n 5                 Generate 5 scrambles
  %(prog)s -d easy -s BL -n 3   3 easy scrambles targeting back-left slot
""",
    )

    parser.add_argument(
        '-d', '--difficulty',
        choices=DIFFICULTIES,
        default='normal',
        help='Difficulty level: easy (5 moves), normal (10), hard (15)',
    )

    parser.add_argument(
        '-s', '--slot',
        choices=SLOTS,
        default='FR',
        help='F2L slot to solve: FR (front-right), FL, BR, BL (default: FR)',
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
    """Run the x-cross scramble demo."""
    args = parse_args()

    rng = Random(args.seed)  # noqa: S311

    section(
        f'X-Cross Scrambles - {args.difficulty.capitalize()} Difficulty'
        f' - Slot {args.slot}',
    )

    print('\nGenerates scrambles with solutions for practicing x-cross.')
    print(
        'The solution shows the moves to solve the x-cross '
        '(cross + one F2L pair) from the scrambled state.',
    )

    for i in range(args.count):
        if args.count > 1:
            print(f'\n--- Scramble {i + 1} of {args.count} ---')
        show_x_cross(args.difficulty, args.slot, rng)

    print('\n' + '=' * 60)
    print('Notes:')
    print('  - Easy: 5 move scrambles (beginner practice)')
    print('  - Normal: 7 move scrambles (intermediate)')
    print('  - Hard: 9 move scrambles (advanced)')
    print('  - Solution solves cross + one F2L pair')
    print('=' * 60)


if __name__ == '__main__':
    main()
