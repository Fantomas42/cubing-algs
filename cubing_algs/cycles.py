"""Calculates the cycle order of algorithms on a cube."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


def compute_cycles(algorithm: 'Algorithm') -> int:
    """
    Calculate the number of times an algorithm must be applied
    to return a cube to its solved state.

    This function simulates applying the given sequence of moves
    repeatedly on a solved cube until the cube returns to
    its original solved state, counting how many applications are needed.

    This is also known as the "order" of the algorithm in group theory.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        The number of times the algorithm must be applied to return to
        solved state.

    Note:
        The function has a safety limit of 100 iterations to prevent
        infinite loops for algorithms that may have very high order
        or don't return to solved state.

    """
    from cubing_algs.transform.pause import unpause_moves  # noqa: PLC0415
    from cubing_algs.transform.timing import untime_moves  # noqa: PLC0415
    from cubing_algs.vcube import VCube  # noqa: PLC0415

    algorithm = algorithm.transform(
        unpause_moves,
        untime_moves,
    )

    if len(algorithm) == 0:
        return 0

    cube = VCube()

    cycles = 1
    cube.rotate(algorithm)

    while not cube.is_solved and cycles < 100:
        cube.rotate(algorithm)
        cycles += 1

    return cycles
