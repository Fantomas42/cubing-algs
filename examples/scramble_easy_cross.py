"""
Example usage of scramble_easy_cross() function.

This demonstrates how to generate easy cross scrambles with solutions
for practicing the cross step in CFOP method.

The scramble_easy_cross() function returns both a scramble and
the corresponding solution to solve the cross.

Usage:
    python scramble_easy_cross.py                 # Run with default settings
    python scramble_easy_cross.py -d easy         # Easy difficulty (5 moves)
    python scramble_easy_cross.py -d normal       # Normal difficulty (10 moves)
    python scramble_easy_cross.py -d hard         # Hard difficulty (15 moves)
    python scramble_easy_cross.py --seed 123      # Set random seed
    python scramble_easy_cross.py -n 5            # Generate 5 scrambles
    python scramble_easy_cross.py -o UF           # Orient with white on top
    python scramble_easy_cross.py -o RD           # Orient with red on top
"""

import argparse
from random import Random

from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.constants import ORIENTATIONS
from cubing_algs.scrambler.steps import scramble_easy_cross
from cubing_algs.vcube import VCube

DIFFICULTIES = ['easy', 'normal', 'hard']


def show_easy_cross(difficulty: str, rng: Random, orientation: str) -> None:
    """Display an easy cross scramble with cube visualization."""
    scramble, solution = scramble_easy_cross(difficulty=difficulty, rng=rng)

    rotation = ORIENTATION_FACE_MOVES[orientation]
    prefix = f'{rotation} ' if rotation else ''

    print(f'\n   Difficulty: {difficulty}')
    print(f'   Scramble: {prefix}{scramble}')
    print(f'   Scramble moves: {len(scramble)}')
    print(f'   Solution: {solution}')
    print(f'   Solution moves: {len(solution)}')

    # Show scrambled state
    cube = VCube()
    cube.rotate(rotation + scramble)
    print('\n   Scrambled state:')
    cube.show(mode='cross')

    # Show state after cross solution
    # (only cross is solved, rest still scrambled)
    cube_solved = VCube()
    cube_solved.rotate(rotation + scramble + solution)
    print('\n   After cross solution (cross edges solved):')
    cube_solved.show(mode='cross')


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
        description='Generate easy cross scrambles with solutions.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      Run with default settings (normal difficulty)
  %(prog)s -d easy              Easy difficulty (5 moves)
  %(prog)s -d normal            Normal difficulty (10 moves)
  %(prog)s -d hard              Hard difficulty (15 moves)
  %(prog)s --seed 123           Set random seed for reproducibility
  %(prog)s -n 5                 Generate 5 scrambles
  %(prog)s -d easy -n 3         3 easy scrambles
""",
    )

    parser.add_argument(
        '-d', '--difficulty',
        choices=DIFFICULTIES,
        default='normal',
        help='Difficulty level: easy (5 moves), normal (10), hard (15)',
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
    """Run the easy cross scramble demo."""
    args = parse_args()

    rng = Random(args.seed)  # noqa: S311

    section(f'Easy Cross Scrambles - {args.difficulty.capitalize()} Difficulty')

    print('\nGenerates scrambles with solutions for practicing cross.')
    print(
        'The solution shows the moves to solve the cross '
        'from the scrambled state.',
    )

    for i in range(args.count):
        if args.count > 1:
            print(f'\n--- Scramble {i + 1} of {args.count} ---')
        show_easy_cross(args.difficulty, rng, args.orientation)

    print('\n' + '=' * 60)
    print('Notes:')
    print('  - Easy: 3 move scrambles (beginner practice)')
    print('  - Normal: 5 move scrambles (intermediate)')
    print('  - Hard: 7 move scrambles (advanced)')
    print('  - Solution solves the cross (4 bottom edges)')
    print('=' * 60)


if __name__ == '__main__':
    main()
