"""
Move set generation and random move selection for cube scrambling.

Provides `build_cube_move_set` to generate the moves valid for a given
cube size, `build_valid_next_moves` to precompute which moves may
follow each other (avoiding repeated or opposite-face moves), and
`random_moves` to generate a random scramble from a move set.
"""
import math
import string
from collections import defaultdict
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import ITERATIONS_BY_CUBE_SIZE
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.constants import OUTER_BASIC_MOVES
from cubing_algs.parsing import parse_moves
from cubing_algs.scrambler.constants import DEFAULT_RNG
from cubing_algs.scrambler.constants import EXCLUDE_ODD_FACES_LH
from cubing_algs.scrambler.constants import EXCLUDE_ODD_FACES_RH


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

            # WCA 4x4x4 scrambles only use wide moves on half of the outer
            # faces (U/R/F for right-handed) since a wide move on the
            # opposite face is redundant with a wide move on this one
            # followed by a whole-cube rotation.
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


def build_valid_next_moves(move_set: list[str]) -> dict[str, list[str]]:
    """
    Precompute valid follow-up moves for each move in the set.

    Groups moves by face, then for each move builds a list of all moves
    whose face is neither the same nor opposite. This eliminates the need
    for rejection sampling in random_moves.

    Args:
        move_set: List of available moves.

    Returns:
        Dictionary mapping each move to its list of valid next moves.

    """
    by_face: dict[str, list[str]] = defaultdict(list)
    move_face: dict[str, str] = {}

    for move in move_set:
        face = move.lstrip(string.digits)[0]
        move_face[move] = face
        by_face[face].append(move)

    valid_by_face: dict[str, list[str]] = {
        face: [
            m
            for other_face, face_moves in by_face.items()
            if other_face != face and OPPOSITE_FACES[other_face] != face
            for m in face_moves
        ]
        for face in by_face
    }

    return {
        move: valid_by_face[face]
        for move, face in move_face.items()
    }


def random_moves(cube_size: int,
                 move_set: list[str],
                 iterations: int | None = None,
                 rng: Random | None = None) -> Algorithm:
    """
    Generate a random sequence of moves from a given move set.

    Creates a scramble by randomly selecting moves while avoiding
    consecutive moves on the same or opposite faces.

    Args:
        cube_size: Size of the cube.
        move_set: List of available moves to choose from.
        iterations: Number of moves to generate (None for automatic).
        rng: Optional random number generator.

    Returns:
        Algorithm containing the random move sequence.

    """
    if rng is None:
        rng = DEFAULT_RNG

    valid_next = build_valid_next_moves(move_set)

    value = rng.choice(move_set)
    moves = [value]

    if iterations is None:
        iterations_range = ITERATIONS_BY_CUBE_SIZE[min(cube_size, 7)]
        iterations = rng.randint(*iterations_range)

    for _ in range(iterations - 1):
        value = rng.choice(valid_next[value])
        moves.append(value)

    return parse_moves(moves)
