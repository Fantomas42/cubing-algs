"""Demonstrate cube visualization for different cube sizes."""
# ruff: noqa: T201
from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube


def show_cube_size(size: int, name: str, algorithm: str = '') -> None:
    """
    Display a cube of specified size with optional algorithm applied.

    Args:
        size: The cube size (2 for 2x2x2, 3 for 3x3x3, etc.).
        name: Description of what's being shown.
        algorithm: Optional move sequence to apply.

    """
    print(f"\n{'=' * 60}")
    print(f'{name} ({size}x{size}x{size})')
    print('=' * 60)

    cube = VCube(size=size)

    if algorithm:
        algo = parse_moves(algorithm)
        print(f'Algorithm: {algo}')
        cube.rotate(algo)
    else:
        print('Solved state')

    cube.show()


# Show solved cubes of different sizes
show_cube_size(2, '2x2x2 Pocket Cube - Solved')
show_cube_size(3, '3x3x3 Standard Cube - Solved')
show_cube_size(4, "4x4x4 Rubik's Revenge - Solved")
show_cube_size(5, "5x5x5 Professor's Cube - Solved")

# Show cubes with moves applied
print('\n\n' + '=' * 60)
print('CUBES WITH MOVES APPLIED')
print('=' * 60)

show_cube_size(
    2,
    '2x2x2 - Sexy Move',
    "R U R' U'",
)
show_cube_size(
    3,
    '3x3x3 - T-Perm',
    "R U R' U' R' F R2 U' R' U' R U R' F'",
)
show_cube_size(
    4,
    '4x4x4 - Wide Moves',
    "Rw U Rw' U' Rw' F Rw2 U' Rw' U' Rw U Rw' F'",
)
show_cube_size(
    5,
    '5x5x5 - Center Rotation',
    "R U R' U' M' U R U' r'",
)

# Show scrambled states
print('\n\n' + '=' * 60)
print('SCRAMBLED CUBES')
print('=' * 60)

show_cube_size(
    2,
    '2x2x2 - Scrambled',
    "R U' R' F2 U F U2 R U2 R'",
)

show_cube_size(
    3,
    '3x3x3 - Scrambled',
    "D' L2 B L2 B' U2 R2 F U2 F' D2 F2 R' F2 U B' D2 F2 D F2",
)

show_cube_size(
    4,
    '4x4x4 - Scrambled',
    "Rw U2 Rw' U' Rw U Rw' F2 Rw U Rw' U' F2",
)

print('\n')
