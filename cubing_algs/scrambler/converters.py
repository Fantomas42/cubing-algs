"""Converters utilities for cubing_algs.scrambler."""
from kociemba import solve

from cubing_algs.algorithm import Algorithm
from cubing_algs.annotations import CubeCubies
from cubing_algs.annotations import CubeFacelets
from cubing_algs.constants import SOLVED_SO
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.initial_state import INITIAL_STATE_3x3x3
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.mirror import mirror_moves


def facelets_to_algorithm(
        source: CubeFacelets,
        destination: CubeFacelets = INITIAL_STATE_3x3x3,
) -> Algorithm:
    """
    Return algorithm to reach a certain state.

    Args:
        source: state of the cube.
        destination: state of the cube to reach.

    Returns:
        Algorithm that transforms cube from solved to given state.

    """
    solution: str = solve(source, destination)

    return parse_moves(solution).transform(mirror_moves)


def cubies_to_algorithm(
        source: CubeCubies,
        destination: CubeCubies | None = None,
) -> Algorithm:
    """
    Return algorithm to reach a certain state.

    Args:
        source: state of the cube.
        destination: state of the cube to reach.

    Returns:
        Algorithm that transforms cube from solved to given state.

    """
    source_facelets = cubies_to_facelets(
        *source,
        SOLVED_SO,
    )

    if destination is not None:
        destination_facelets = cubies_to_facelets(
            *destination,
            SOLVED_SO,
        )

        return facelets_to_algorithm(
            source_facelets,
            destination_facelets,
        )

    return facelets_to_algorithm(
        source_facelets,
    )
