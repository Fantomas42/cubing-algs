"""Solve utilities for cubing_algs."""
from kociemba import solve

from cubing_algs.algorithm import Algorithm
from cubing_algs.annotations import CubeCubies
from cubing_algs.annotations import CubeFacelets
from cubing_algs.constants import SOLVED_SO
from cubing_algs.exceptions import InvalidFaceletsSolveError
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.parsing import parse_moves

# Kociemba returns this non-empty sequence instead of an empty string
# when solving from a solved cube to itself.
KOCIEMBA_SOLVED_SPECIAL_CASE = "R L U2 R L' B2 U2 R2 F2 L2 D2 L2 F2"


def facelets_to_facelets_algorithm(
        source: CubeFacelets,
        destination: CubeFacelets,
) -> Algorithm:
    """
    Return algorithm to reach a certain state from facelets.

    Args:
        source: state of the cube.
        destination: state of the cube to reach.

    Returns:
        Algorithm that transforms cube from solved to given state.

    Raises:
        InvalidFaceletsSolveError: When Kociemba solver fails.

    """
    try:
        solution: str = solve(source, destination)
    except ValueError as e:
        msg = (
            'Solver encountered an error, '
            'probably the facelets are not UF oriented.'
        )
        raise InvalidFaceletsSolveError(msg) from e

    algorithm = parse_moves(solution)

    if str(algorithm) == KOCIEMBA_SOLVED_SPECIAL_CASE:
        return Algorithm()

    return algorithm


def cubies_to_cubies_algorithm(
        source: CubeCubies,
        destination: CubeCubies,
) -> Algorithm:
    """
    Return algorithm to reach a certain state from cubies.

    Args:
        source: state of the cube.
        destination: state of the cube to reach.

    Returns:
        Algorithm that transforms cube from solved to given state.

    Note:
        Raises InvalidFaceletsSolveError when the Kociemba solver fails
        (propagated from facelets_to_facelets_algorithm).

    """
    source_facelets = cubies_to_facelets(
        *source,
        SOLVED_SO,
    )

    destination_facelets = cubies_to_facelets(
        *destination,
        SOLVED_SO,
    )

    return facelets_to_facelets_algorithm(
        source_facelets,
        destination_facelets,
    )
