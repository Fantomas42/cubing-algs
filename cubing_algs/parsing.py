import logging

from cubing_algs.constants import MOVE_SPLIT
from cubing_algs.move import Move

logger = logging.getLogger(__name__)


def split_moves(move_string: str) -> list[Move]:
    moves = [
        Move(x.strip())
        for x in MOVE_SPLIT.split(move_string)
        if x.strip()
    ]

    check_moves(moves)

    return moves


def check_moves(moves: list[Move]) -> bool:
    move_string = ''.join(moves)

    for move in moves:
        if not move.is_valid:
            logger.error('"%s" -> %s is not known', move_string, move)

        elif len(move) > 1:
            if move.is_japanese:
                if len(move) > 2 and (
                        not move.is_double
                        and not move.is_counter_clockwise
                ):
                    logger.error(
                        '"%s" -> %s is an invalid modificator',
                        move_string, move,
                    )
                elif len(move) > 3:
                    logger.error(
                        '"%s" -> %s is an invalid move',
                        move_string, move,
                    )
            elif not move.is_double and not move.is_counter_clockwise:
                logger.error(
                    '"%s" -> %s is an invalid modificator',
                    move_string, move,
                )
            elif len(move) > 2:
                logger.error(
                    '"%s" -> %s is an invalid move',
                    move_string, move,
                )


def clean_moves(algo: str) -> list[Move]:
    """
    Clean string moves and return list of Move
    """
    algo = algo.strip()

    algo = algo.replace(
        '’', "'",  # noqa RUF001
    ).replace(
        '`', "'",
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

    return split_moves(algo)


def full_clean_moves(algo: str) -> list[Move]:
    """
    Clean string moves and remove final head/tail orientations.
    """
    clean_algo = clean_moves(algo)

    if clean_algo[0][0] in {'y', 'U'}:
        clean_algo = clean_algo[1:]

    if clean_algo[-1][0] in {'y', 'U'}:
        clean_algo = clean_algo[:-1]

    return clean_algo
