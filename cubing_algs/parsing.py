import logging

from cubing_algs.constants import MOVE_SPLIT
from cubing_algs.move import InvalidMoveError
from cubing_algs.move import Move

logger = logging.getLogger(__name__)


def clean_moves(moves: str) -> str:
    moves = moves.strip()

    return moves.replace(
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
        '1', '',
    ).replace(
        'm', 'M',
    ).replace(
        's', 'S',
    ).replace(
        'e', 'E',
    ).replace(
        'X', 'x',
    ).replace(
        'Y', 'y',
    ).replace(
        'Z', 'z',
    )


def split_moves(moves: str) -> list[Move]:
    return [
        Move(x.strip())
        for x in MOVE_SPLIT.split(moves)
        if x.strip()
    ]


def check_moves(moves: list[Move]) -> bool:
    valid = True
    move_string = ''.join([str(m) for m in moves])

    for move in moves:
        if not move.is_valid:
            valid = False
            logger.error('"%s" -> %s is not known', move_string, move)
        elif len(move) > 1:
            if move.is_japanese:
                if len(move) > 2 and (
                        not move.is_double
                        and not move.is_counter_clockwise
                ):
                    valid = False
                    logger.error(
                        '"%s" -> %s is an invalid modificator',
                        move_string, move,
                    )
                elif len(move) > 3:
                    valid = False
                    logger.error(
                        '"%s" -> %s is an invalid move',
                        move_string, move,
                    )
            elif not move.is_double and not move.is_counter_clockwise:
                valid = False
                logger.error(
                    '"%s" -> %s is an invalid modificator',
                    move_string, move,
                )
            elif len(move) > 2:
                valid = False
                logger.error(
                    '"%s" -> %s is an invalid move',
                    move_string, move,
                )

    return valid


def parse_moves(moves: str) -> list[Move]:
    """
    Clean string moves and return list of Move
    """
    moves = clean_moves(moves)
    moves = split_moves(moves)

    if not check_moves(moves):
        error = f'{ moves } contains invalid move'
        raise InvalidMoveError(error)

    return moves


def parse_moves_cfop(moves: str) -> list[Move]:
    """
    Same as parse_moves, but remove head/tail re-orientations
    """
    moves = parse_moves(moves)

    if moves[0][0] in {'y', 'U'}:
        moves = moves[1:]

    if moves[-1][0] in {'y', 'U'}:
        moves = moves[:-1]

    return moves
