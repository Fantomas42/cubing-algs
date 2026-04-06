"""Compare the evolution of piece types across different cube sizes."""
# ruff: noqa: T201
import argparse
from collections import Counter

from cubing_algs.vcube import VCube

DEFAULT_SIZES = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11)

PIECE_TYPE_ORDER = [
    'corner',
    'midge',
    'wing',
    'fixed_center',
    't_center',
    'x_center',
    'oblique_center',
]

FAMILY_LABELS = {
    'corner': 'corner',
    'midge': 'edge',
    'wing': 'edge',
    'fixed_center': 'center',
    't_center': 'center',
    'x_center': 'center',
    'oblique_center': 'center',
}

PIECE_TYPE_LABELS = {
    'corner': 'Corner',
    'midge': 'Midge',
    'wing': 'Wing',
    'fixed_center': 'Fixed center',
    't_center': 'T-center',
    'x_center': 'X-center',
    'oblique_center': 'Oblique center',
}


def extract_counts(size: int) -> Counter[str]:
    """
    Extract per-face piece type counts for a given cube size.

    Returns:
        The piece counter.

    """
    cube = VCube(size=size)
    counts: Counter[str] = Counter()
    for types in cube.facelet_piece_types.values():
        counts[types[0]] += 1
    return counts


def build_table(sizes: tuple[int, ...],
                all_counts: dict[int, Counter[str]]) -> None:
    """
    Print a comparison table of piece type counts
    per face across cube sizes.
    """
    # Determine which piece types actually appear across all sizes
    present_types = [
        t for t in PIECE_TYPE_ORDER
        if any(all_counts[s][t] for s in sizes)
    ]

    col_width = 16
    size_width = max(  # noqa: PLW3301
        max(len(f'{s}x{s}x{s}') for s in sizes),
        max(len(str(6 * s * s)) for s in sizes),
    ) + 2

    header = f'{"Piece type":<{col_width}}' + ''.join(
        f'{f"{s}x{s}x{s}":>{size_width}}' for s in sizes
    )
    separator = '-' * len(header)

    print(separator)
    print(header)
    print(separator)

    current_family = None
    for piece_type in present_types:
        family = FAMILY_LABELS[piece_type]
        if family != current_family:
            if current_family is not None:
                print()
            current_family = family

        label = PIECE_TYPE_LABELS[piece_type]
        row = f'{label:<{col_width}}'
        for size in sizes:
            count = all_counts[size][piece_type]
            cell = str(count) if count else '-'
            row += f'{cell:>{size_width}}'
        print(row)

    print(separator)

    # Total facelets per face
    row = f'{"Total per face":<{col_width}}'
    for size in sizes:
        row += f'{size * size:>{size_width}}'
    print(row)

    # Total facelets overall
    row = f'{"Total":<{col_width}}'
    for size in sizes:
        row += f'{6 * size * size:>{size_width}}'
    print(row)

    print(separator)


def show_first_appearance(sizes: tuple[int, ...],
                          all_counts: dict[int, Counter[str]]) -> None:
    """Show at which cube size each piece type first appears."""
    print('\nFirst appearance by cube size:')
    current_family = None
    for piece_type in PIECE_TYPE_ORDER:
        family = FAMILY_LABELS[piece_type]
        if family != current_family:
            if current_family is not None:
                print()
            current_family = family

        first = next((s for s in sizes if all_counts[s][piece_type] > 0), None)
        if first is None:
            continue
        label = PIECE_TYPE_LABELS[piece_type]
        print(f'  {label:<16} first appears on {first}x{first}x{first}')


parser = argparse.ArgumentParser(
    description='Compare piece type evolution across cube sizes',
)
parser.add_argument(
    'sizes',
    nargs='*',
    type=int,
    default=list(DEFAULT_SIZES),
    help='Cube sizes to compare (default: 2 3 4 5 6 7)',
)

args = parser.parse_args()
sizes = tuple(args.sizes)

print(
    '\nPiece type counts per face — sizes:'
    f'{", ".join(f"{s}x{s}x{s}" for s in sizes)}\n',
)
all_counts = {size: extract_counts(size) for size in sizes}
build_table(sizes, all_counts)
show_first_appearance(sizes, all_counts)
print()
