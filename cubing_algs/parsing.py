"""
Utilities for parsing and normalizing Rubik's cube algorithm notations.

This module provides functions to clean, validate, and convert
string representations of Rubik's cube algorithms into structured
Algorithm objects.
"""
import logging
import re

from cubing_algs.algorithm import Algorithm
from cubing_algs.commutator_conjugate import expand_commutators_and_conjugates
from cubing_algs.constants import MOVE_SPLIT
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.move import Move

logger = logging.getLogger(__name__)

CLEAN_PATTERNS = [
    (re.compile(r'[`’]'), "'"),  # # noqa RUF001
    (re.compile(r'[():,\[\]]'), ' '),
    (re.compile(r'\s+'), ' '),
    (re.compile(r"2'"), '2'),
]

CASE_FIXES = str.maketrans('mseXYZ', 'MSExyz')


def clean_moves(moves: str) -> str:
    """
    Normalize and clean a string representation of moves.

    This function standardizes move notation by:
    - Removing whitespace and unnecessary characters
    - Converting alternative notations to standard ones
    - Standardizing the casing of slice moves
    """
    moves = moves.strip()

    for pattern, replacement in CLEAN_PATTERNS:
        moves = pattern.sub(replacement, moves)

    return moves.translate(CASE_FIXES)


def split_moves(moves: str) -> list[Move]:
    """
    Split a string of moves into individual Move objects.

    Uses the MOVE_SPLIT pattern from constants to identify boundaries
    between individual moves in the string.
    """
    return [
        Move(x.strip())
        for x in MOVE_SPLIT.split(moves)
        if x.strip()
    ]


def check_moves(moves: list[Move]) -> bool:
    """
    Validate a list of Move objects.

    Checks that each move has a valid base move, layer and modifier.
    Logs errors for invalid moves.
    """
    for move in moves:
        if not (move.is_valid_move
                and move.is_valid_modifier
                and move.is_valid_layer):
            if logger.isEnabledFor(logging.ERROR):  # pragma: no cover
                move_string = ''.join(str(m) for m in moves)
                if not move.is_valid_move:
                    logger.error(
                        '"%s" -> %s is not a valid move',
                        move_string, move,
                    )
                elif not move.is_valid_modifier:
                    logger.error(
                        '"%s" -> %s has an invalid modifier',
                        move_string, move,
                    )
                else:
                    logger.error(
                        '"%s" -> %s has an invalid layer',
                        move_string, move,
                    )
            return False

    return True


def parse_moves(raw_moves: str | list[str] | Algorithm,
                secure: bool = True) -> Algorithm:  # noqa: FBT001, FBT002
    """
    Parse raw move data into an Algorithm object.

    This function handles different input types and performs
    cleaning and validation:
    - If raw_moves is already an Algorithm, it's returned as-is
    - If raw_moves is a list, it's joined into a string
    - Strings are cleaned, split into moves, validated, and converted
      to an Algorithm

    Now supports commutators [A, B] and conjugates [A: B].

    Examples:
        [A, B] becomes A B A' B' (commutator)
        [A: B] becomes A B A' (conjugate)
        [[R: U], D] becomes R U R' D R U' R' D'
        [F: [U, R]] becomes F U R U' R' F'
    """
    if isinstance(raw_moves, Algorithm):
        return raw_moves

    if isinstance(raw_moves, list):
        raw_moves = ''.join(str(m) for m in raw_moves)

    expanded_moves = expand_commutators_and_conjugates(raw_moves)

    if not secure:
        moves = split_moves(clean_moves(expanded_moves))
    else:
        moves = split_moves(expanded_moves)

    if not secure and not check_moves(moves):
        error = f'{ raw_moves } contains invalid move'
        raise InvalidMoveError(error)

    return Algorithm(moves)


def parse_moves_cfop(moves: str) -> Algorithm:
    """
    Parse moves specifically for CFOP method algorithms.

    Similar to parse_moves, but also removes typical setup and restoration
    moves (y and U rotations) from the beginning and end of the algorithm.
    This is useful for standardizing CFOP algorithms, which often include
    such moves for convenience.
    """
    algo = parse_moves(moves, secure=False)

    if algo[0].base_move in {'y', 'U'}:
        algo = algo[1:]

    if algo[-1].base_move in {'y', 'U'}:
        algo = algo[:-1]

    return algo
