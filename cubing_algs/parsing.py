import logging

from cubing_algs.algorithm import Algorithm
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
        if not move.is_valid_move:
            valid = False
            logger.error(
                '"%s" -> %s is not a valid move',
                move_string, move,
            )
        elif not move.is_valid_modifier:
            valid = False
            logger.error(
                '"%s" -> %s has an invalid modifier',
                move_string, move,
            )

    return valid


def parse_moves(raw_moves: str | list[str] | Algorithm) -> Algorithm:
    """
    Clean string moves and return Algorithm
    """
    if isinstance(raw_moves, Algorithm):
        return raw_moves

    if isinstance(raw_moves, list):
        raw_moves = ''.join(str(m) for m in raw_moves)

    moves = split_moves(clean_moves(raw_moves))

    if not check_moves(moves):
        error = f'{ raw_moves } contains invalid move'
        raise InvalidMoveError(error)

    return Algorithm(moves)


def parse_moves_cfop(moves: str) -> Algorithm:
    """
    Same as parse_moves, but remove head/tail re-orientations
    """
    algo = parse_moves(moves)

    if algo.moves[0].base_move in {'y', 'U'}:
        algo.moves = algo.moves[1:]

    if algo.moves[-1].base_move in {'y', 'U'}:
        algo.moves = algo.moves[:-1]

    return algo
