"""Demonstrate facelet piece types for different cube sizes."""
# ruff: noqa: T201
import argparse
from collections import Counter

from cubing_algs.vcube import VCube

DEFAULT_SIZES = (2, 3, 4, 5, 7)


def show_piece_types(size: int) -> None:
    """
    Display the piece types summary and cube for a given size.

    Args:
        size: The cube size (2 for 2x2x2, 3 for 3x3x3, etc.).

    """
    cube = VCube(size=size)
    piece_types = cube.facelet_piece_types

    print(f'{size}x{size}x{size}')
    print('=' * 40)

    counts: Counter[str] = Counter()
    families: dict[str, list[str]] = {}
    for types in piece_types.values():
        counts[types[0]] += 1
        if len(types) > 1:
            family = types[-1]
            families.setdefault(family, [])
            if types[0] not in families[family]:
                families[family].append(types[0])

    def print_row(name: str, count: int, indent: int = 0) -> None:
        """Print a formatted row with piece type counts."""
        prefix = '    ' * indent
        total = count * 6
        print(f'  {prefix}{name:<16} {count:>3} per face, {total:>4} total')

    members_set = {m for members in families.values() for m in members}
    for family, members in families.items():
        family_total = sum(counts[m] for m in members)
        print_row(family, family_total)
        for member in sorted(members, key=lambda m: -counts[m]):
            print_row(member, counts[member], indent=1)
    for piece_type, count in counts.most_common():
        if piece_type not in members_set:
            print_row(piece_type, count)

    cube.show(mode='linear', style='detailed')
    print()


parser = argparse.ArgumentParser(
    description='Display facelet piece types for different cube sizes',
)
parser.add_argument(
    'sizes',
    nargs='*',
    type=int,
    default=DEFAULT_SIZES,
    help='Cube sizes to display (default: 2 3 4 5 7)',
)

args = parser.parse_args()

for size in args.sizes:
    show_piece_types(size)
