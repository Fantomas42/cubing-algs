"""Transform an algorithm to an equivalent Kociemba solver solution."""
from cubing_algs.algorithm import Algorithm
from cubing_algs.vcube import VCube


def kociemba_moves(old_moves: Algorithm) -> Algorithm:
    """
    Transform an algorithm to an equivalent Kociemba solver solution.

    Applies the input algorithm to a virtual cube and uses the Kociemba
    solver to find an equivalent solution that reaches the same cube state.
    The result uses only basic face moves (R, U, F, L, D, B) plus rotations
    for orientation changes.

    Timing and pause information is stripped from the input before solving.

    Args:
        old_moves: The algorithm to process.

    Returns:
        A new Algorithm with the Kociemba solver solution.

    """
    moves_str = ' '.join(
        str(move.untimed) for move in old_moves if not move.is_pause
    )

    if not moves_str:
        return Algorithm()

    cube = VCube()
    cube.rotate(moves_str)

    return VCube().to_algorithm(cube)
