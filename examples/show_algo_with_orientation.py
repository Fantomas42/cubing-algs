"""Demonstrate algorithm visualization with different display options."""
import argparse

from cubing_algs.parsing import parse_moves

# IMPORTANT NOTES:
# in Algorithm.show
# Rotate faclets_unique to compensate the final orientation
# could use rorient transformation
# The goal is too still highlight
# the moved facelets from cube pov preserving final user pov

DEFAULT_ALGOS = [
    'R',
    'y R',
    "R U R'",
    "y R U R'",
    "z2 R U R' U' R' F R2 U' R' U' R U R' F'",   # PLL T
    "z2 F R U R' U' R U R' U' R U R' U' F'",  # OLL 21 H
]


def show_algorithm(name: str, algorithm: str, **kw: object) -> None:
    """
    Display algorithm visualization with optional parameters.

    Args:
        name: Name of the algorithm.
        algorithm: Move sequence string.
        **kw: Additional keyword arguments passed to show method.

    """
    algo = parse_moves(algorithm)

    print(f'{ name }: { algo }')

    algo.show(**kw)  # type: ignore[arg-type]


def main() -> None:
    """Run the algorithm visualization demo."""
    parser = argparse.ArgumentParser(
        description='Visualize cube algorithms with orientation display.',
        epilog="""examples:
  %(prog)s                          Show default algorithms on all sizes
  %(prog)s "R U R'"                 Show a custom algorithm on all sizes
  %(prog)s "R U R'" -s 3            Show a custom algorithm on a 3x3x3
  %(prog)s -s 4                     Show default algorithms on a 4x4x4""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'algorithm',
        nargs='?',
        help='Algorithm to visualize (e.g. "R U R\'")',
    )
    parser.add_argument(
        '-s', '--size',
        type=int,
        choices=[2, 3, 4, 5],
        help='Cube size (default: all sizes from 2 to 5)',
    )
    args = parser.parse_args()

    algos = [args.algorithm] if args.algorithm else DEFAULT_ALGOS
    sizes = [args.size] if args.size else [2, 3, 4, 5]

    for algo in algos:
        for size in sizes:
            show_algorithm(
                f'{size}x{size}x{size} Cube',
                algo,
                size=size,
            )


if __name__ == '__main__':
    main()
