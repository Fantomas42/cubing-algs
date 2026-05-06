"""Demonstrate F2L visualization with different cube orientations."""
# ruff: noqa: T201
import argparse

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

DEFAULT_ALGORITHM = "R U' R' U R' F R F' U"


def show_f2l_oriented(
        faces: str,
        orientation: str,
        algorithm: Algorithm,
) -> None:
    """Display F2L visualization with a specific cube orientation."""
    print(f'{ faces }: { orientation or "--" } ====>')

    c = VCube()
    c.rotate(f'{ orientation } { algorithm }'.strip())
    c.show(mode='f2l')


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace.

    """
    parser = argparse.ArgumentParser(
        description='F2L visualization with cube orientations',
    )
    parser.add_argument(
        '--algorithm', '-a',
        default=DEFAULT_ALGORITHM,
        help=f'Algorithm to apply (default: "{ DEFAULT_ALGORITHM }")',
    )
    parser.add_argument(
        'orientations',
        nargs='*',
        help='Orientation faces to display (e.g. UF DF RF). Defaults to all.',
    )

    return parser.parse_args()


def main() -> None:
    """Run the F2L oriented visualization."""
    args = parse_args()

    if args.orientations:
        orientations = {
            face: ORIENTATION_FACE_MOVES[face]
            for face in args.orientations
            if face in ORIENTATION_FACE_MOVES
        }
        unknown = [
            f
            for f in args.orientations
            if f not in ORIENTATION_FACE_MOVES
        ]
        if unknown:
            print(f'Unknown orientation(s): { ", ".join(unknown) }')
            print(f'Valid orientations: { ", ".join(ORIENTATION_FACE_MOVES) }')
    else:
        orientations = ORIENTATION_FACE_MOVES

    for faces, orientation in orientations.items():
        show_f2l_oriented(faces, orientation, parse_moves(args.algorithm))


main()
