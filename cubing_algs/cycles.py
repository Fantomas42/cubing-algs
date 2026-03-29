"""Calculates the cycle order of algorithms on a cube."""
from math import lcm
from typing import TYPE_CHECKING

from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.solved_state import UNIQUE_FACELETS_3x3x3

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


def permutation_order(permutation: list[int]) -> int:
    """
    Compute the order of a permutation (LCM of cycle lengths).

    Args:
        permutation: Permutation array where permutation[i] is the
            destination of element i.

    Returns:
        The order of the permutation. Returns 1 for the identity.

    """
    visited = [False] * len(permutation)
    order = 1

    for i in range(len(permutation)):
        if visited[i] or permutation[i] == i:
            continue

        cycle_len = 0
        current = i
        while not visited[current]:
            visited[current] = True
            current = permutation[current]
            cycle_len += 1

        order = lcm(order, cycle_len)

    return order


def compute_cycles(algorithm: 'Algorithm') -> int:
    """
    Calculate the number of times an algorithm must be applied
    to return a 3x3x3 cube to its solved state.

    Computes the order by analyzing the facelet permutation
    induced by the algorithm. The order is the LCM of the
    permutation cycle lengths, computed efficiently after a single
    algorithm application (versus O(order * n) for brute-force
    simulation, where n is the algorithm length).

    This is also known as the "order" of the algorithm in group theory.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        The number of times the algorithm must be applied to return to
        solved state. -1 if the algorithm cannot be applied on 3x3x3 cube.

    Note:
        The maximum possible order of any element in the 3x3x3 Rubik's cube
        group is 2520 (including wide and slice moves).

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

    cube = VCube(initial=UNIQUE_FACELETS_3x3x3, size=3, check=False)

    try:
        cube.rotate(algorithm)
    except InvalidMoveError:
        return -1

    result = cube.state
    permutation = [result.index(c) for c in UNIQUE_FACELETS_3x3x3]

    # A rotated solved cube is still solved: all facelets of each
    # face map to the same destination face (possibly a different one).
    face_size = cube.face_size
    if all(
        permutation[i] // face_size == permutation[start] // face_size
        for start in range(0, len(permutation), face_size)
        for i in range(start + 1, start + face_size)
    ):
        return 1

    return permutation_order(permutation)
