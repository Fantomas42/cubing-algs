import logging

from cubing_algs.constants import ALL_BASIC_MOVES
from cubing_algs.constants import MOVE_SPLIT

logger = logging.getLogger(__name__)


def split_moves(move_string: str) -> list[str]:
    moves = [x.strip() for x in MOVE_SPLIT.split(move_string) if x.strip()]

    check_moves(moves)

    return moves


def check_moves(moves: list[str]) -> None:
    move_string = ''.join(moves)

    for move in moves:
        if move[0] not in ALL_BASIC_MOVES:
            logger.error('"%s" -> %s is not known', move_string, move)

        elif len(move) > 1:
            if move[1] == 'w':
                if len(move) > 2 and move[2] not in {'2', "'"}:
                    logger.error(
                        '"%s" -> %s is an invalid modificator',
                        move_string, move,
                    )
                elif len(move) > 3:
                    logger.error(
                        '"%s" -> %s is an invalid move',
                        move_string, move,
                    )
            elif move[1] not in {'2', "'"}:
                logger.error(
                    '"%s" -> %s is an invalid modificator',
                    move_string, move,
                )
            elif len(move) > 2:
                logger.error(
                    '"%s" -> %s is an invalid move',
                    move_string, move,
                )


def clean_moves(algo: str, keep_rotations: bool) -> list[str]:
    algo = algo.strip()

    algo = algo.replace(
        '’', "'",  # noqa RUF001
    ).replace(
        '[', '',
    ).replace(
        ']', '',
    ).replace(
        '(', '',
    ).replace(
        ')', '',
    ).replace(
        ':', '',
    ).replace(
        ' ', '',
    ).replace(
        "2'", '2',
    ).replace(
        '3', "'",
    ).replace(
        'm', 'M',
    ).replace(
        's', 'S',
    ).replace(
        'e', 'E',
    )

    for face in ['F', 'R', 'U', 'B', 'L', 'D']:
        algo = algo.replace('%sw' % face, face.lower())

    clean_algo = split_moves(algo)

    if not keep_rotations:
        if clean_algo[0][0] in {'y', 'U'}:
            clean_algo = clean_algo[1:]

        if clean_algo[-1][0] in {'y', 'U'}:
            clean_algo = clean_algo[:-1]

    return clean_algo
