"""NxNxN scramble generation for Rubik's cubes of various sizes."""
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidCubeSizeError
from cubing_algs.scrambler.moves import build_cube_move_set
from cubing_algs.scrambler.moves import random_moves


def scramble(cube_size: int, iterations: int | None = None, *,
             inner_layers: bool = False,
             right_handed: bool = True,
             rng: Random | None = None) -> Algorithm:
    """
    Generate a random scramble for a cube of the specified size.

    Creates an appropriate move set for the cube size and generates
    a random sequence to scramble the cube.

    Args:
        cube_size: Size of the cube (minimum 2).
        iterations: Number of moves in the scramble (None for automatic).
        inner_layers: Whether to include inner layer moves.
        right_handed: Whether to optimize for right-handed solving.
        rng: Optional random number generator.

    Returns:
        Algorithm containing the scramble sequence.

    Raises:
        InvalidCubeSizeError: If cube_size is less than 2.

    Example::

        >>> scramble(3, 5, rng=Random(42))
        Algorithm("F R D2 F' U")

    """
    if cube_size < 2:
        msg = f'cube_size must be at least 2, got { cube_size }'
        raise InvalidCubeSizeError(msg)

    move_set = build_cube_move_set(
        cube_size,
        inner_layers=inner_layers,
        right_handed=right_handed,
    )

    return random_moves(cube_size, move_set, iterations, rng)
