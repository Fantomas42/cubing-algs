import math
import re
from random import choice
from random import randint

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

EXCLUDE_ODD_FACES = {'D', 'L', 'B'}


def build_cube_move_set(cube_size: int, *,
                        inner_layers: bool = False) -> list[str]:
    moves = []

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

            if cube_size > 4 or face not in EXCLUDE_ODD_FACES:
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
                        and face in EXCLUDE_ODD_FACES
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
                            and face in EXCLUDE_ODD_FACES
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
                 iterations: int = 0) -> Algorithm:
    value = choice(move_set)
    moves = [value]
    previous = value

    if not iterations:
        iterations_range = ITERATIONS_BY_CUBE_SIZE[min(cube_size, 7)]
        iterations = randint(*iterations_range)

    while len(moves) < iterations:
        while not is_valid_next_move(value, previous):
            value = choice(move_set)

        previous = value
        moves.append(value)

    return parse_moves(moves)


def scramble(cube_size: int, iterations: int = 0, *,
             inner_layers: bool = False) -> Algorithm:
    move_set = build_cube_move_set(
        cube_size,
        inner_layers=inner_layers,
    )

    return random_moves(cube_size, move_set, iterations)


def scramble_easy_cross() -> Algorithm:
    return random_moves(3, MOVES_EASY_CROSS, 10)
