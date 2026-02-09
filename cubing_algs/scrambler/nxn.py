"""NxNxN scramble generation for Rubik's cubes of various sizes."""
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.scrambler.moves import build_cube_move_set
from cubing_algs.scrambler.moves import random_moves


def scramble(cube_size: int, iterations: int = 0, *,
             inner_layers: bool = False,
             right_handed: bool = True,
             rng: Random | None = None) -> Algorithm:
    """
    Generate a random scramble for a cube of the specified size.

    Creates an appropriate move set for the cube size and generates
    a random sequence to scramble the cube.

    Args:
        cube_size: Size of the cube (e.g., 3 for 3x3x3).
        iterations: Number of moves in the scramble (0 for automatic).
        inner_layers: Whether to include inner layer moves.
        right_handed: Whether to optimize for right-handed solving.
        rng: Optional random number generator.

    Returns:
        Algorithm containing the scramble sequence.

    """
    move_set = build_cube_move_set(
        cube_size,
        inner_layers=inner_layers,
        right_handed=right_handed,
    )

    return random_moves(cube_size, move_set, iterations, rng)
