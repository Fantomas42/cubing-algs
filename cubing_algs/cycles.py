"""Calculates the cycle order of algorithms on a cube."""
from typing import TYPE_CHECKING

from cubing_algs.exceptions import InvalidMoveError

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


MAX_ORDER_3x3x3 = 2520


def compute_cycles(algorithm: 'Algorithm') -> int:
    """
    Calculate the number of times an algorithm must be applied
    to return a 3x3x3 cube to its solved state.

    This function simulates applying the given sequence of moves
    repeatedly on a solved cube until the cube returns to
    its original solved state, counting how many applications are needed.

    This is also known as the "order" of the algorithm in group theory.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        The number of times the algorithm must be applied to return to
        solved state. -1 if the algorithm cannot be applied on 3x3x3 cube.

    Note:
        The function has a safety limit of 2520 iterations, which is the
        maximum possible order of any element in the 3x3x3 Rubik's cube
        group (including wide and slice moves).

        https://en.wikipedia.org/wiki/Rubik's_Cube_group#Group_structure
        https://www.jaapsch.net/puzzles/cubic3.htm#p34
        https://www.mzrg.com/rubik/orders.shtml

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

    cube = VCube(size=3)

    try:
        cube.rotate(algorithm)
    except InvalidMoveError:
        return -1

    cycles = 1
    while not cube.is_solved and cycles < MAX_ORDER_3x3x3:
        cube.rotate(algorithm)
        cycles += 1

    return cycles
