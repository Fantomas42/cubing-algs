"""Random scramble generation for Rubik's cubes of various sizes."""

import math
import re
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import ITERATIONS_BY_CUBE_SIZE
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.constants import OUTER_BASIC_MOVES
from cubing_algs.parsing import parse_moves

FACE_REGEXP = re.compile(rf"({ '|'.join(FACE_ORDER) })")

MOVES_EASY_CROSS = [
    'F',
    'R',
    'B',
    'L',
]

EXCLUDE_ODD_FACES_RH = {'D', 'L', 'B'}
EXCLUDE_ODD_FACES_LH = {'D', 'R', 'B'}

DEFAULT_RNG = Random()  # noqa: S311


def build_cube_move_set(cube_size: int, *,
                        inner_layers: bool = False,
                        right_handed: bool = True) -> list[str]:
    """
    Generate a set of moves appropriate for a given cube size.

    Creates basic face moves and wide moves suitable for scrambling
    cubes of different sizes.

    Args:
        cube_size: Size of the cube (e.g., 3 for 3x3x3).
        inner_layers: Whether to include inner layer moves.
        right_handed: Whether to exclude certain moves for right-handed solving.

    Returns:
        List of move notation strings for the specified cube size.

    """
    moves = []

    exclude_odd_faces = EXCLUDE_ODD_FACES_RH
    if not right_handed:
        exclude_odd_faces = EXCLUDE_ODD_FACES_LH

    for face in OUTER_BASIC_MOVES:
        moves.extend(
            [
                face,
                f"{ face }'",
                f'{ face }2',
            ],
        )
        if cube_size > 3:
            center_ceil = math.ceil(cube_size / 2)
            center_floor = math.floor(cube_size / 2)
            odd_cube = bool(cube_size % 2)
            even_cube = not odd_cube

            if cube_size > 4 or face not in exclude_odd_faces:
                moves.extend(
                    [
                        f'{ face }w',
                        f"{ face }w'",
                        f'{ face }w2',
                    ],
                )

            for i in range(3, center_floor + 1):
                if (
                        even_cube
                        and face in exclude_odd_faces
                        and i == center_floor
                ):
                    continue
                moves.extend(
                    [
                        f'{ i }{ face }w',
                        f"{ i }{ face }w'",
                        f'{ i }{ face }w2',
                    ],
                )

            if inner_layers:
                for i in range(2, center_ceil + 1):
                    if (
                            odd_cube
                            and face in exclude_odd_faces
                            and i == center_ceil
                    ):
                        continue

                    moves.extend(
                        [
                            f'{ i }{ face }',
                            f"{ i }{ face }'",
                            f'{ i }{ face }2',
                        ],
                    )

    return moves


def is_valid_next_move(current: str, previous: str) -> bool:
    """
    Check if a move is valid to follow another move in a scramble.

    Prevents consecutive moves on the same face or opposite faces
    to ensure efficient scrambles.

    Args:
        current: The current move being considered.
        previous: The previous move in the sequence.

    Returns:
        True if the current move can validly follow the previous move.

    """
    current_move_search = FACE_REGEXP.search(current)
    previous_move_search = FACE_REGEXP.search(previous)

    if not current_move_search or not previous_move_search:
        return False

    current_move = current_move_search[0]
    previous_move = previous_move_search[0]

    if current_move == previous_move:
        return False

    return OPPOSITE_FACES[current_move] != previous_move


def random_moves(cube_size: int,
                 move_set: list[str],
                 iterations: int = 0,
                 rng: Random | None = None) -> Algorithm:
    """
    Generate a random sequence of moves from a given move set.

    Creates a scramble by randomly selecting moves while avoiding
    consecutive moves on the same or opposite faces.

    Args:
        cube_size: Size of the cube.
        move_set: List of available moves to choose from.
        iterations: Number of moves to generate (0 for automatic).
        rng: Optional random number generator.

    Returns:
        Algorithm containing the random move sequence.

    """
    if rng is None:
        rng = DEFAULT_RNG

    value = rng.choice(move_set)
    moves = [value]
    previous = value

    if not iterations:
        iterations_range = ITERATIONS_BY_CUBE_SIZE[min(cube_size, 7)]
        iterations = rng.randint(*iterations_range)

    while len(moves) < iterations:
        while not is_valid_next_move(value, previous):
            value = rng.choice(move_set)

        previous = value
        moves.append(value)

    return parse_moves(moves)


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


def scramble_easy_cross(rng: Random | None = None) -> Algorithm:
    """
    Generate an easy cross scramble using only basic face moves.

    Creates a simple scramble suitable for practicing cross patterns
    in speedcubing methods like CFOP.

    Args:
        rng: Optional random number generator.

    Returns:
        Algorithm with 10 random moves from F, R, B, L faces.

    """
    return random_moves(3, MOVES_EASY_CROSS, 10, rng)
