"""Transform applied algorithm moves to a Kociemba solution."""
from cubing_algs.algorithm import Algorithm
from cubing_algs.vcube import VCube


def kociemba_moves(old_moves: Algorithm) -> Algorithm:
    """
    Transform algorithm to a Kociemba algorithm.

    Args:
        old_moves: The algorithm to process.

    Returns:
        A new Algorithm filtered by the Kociemba solver.

    """
    cube = VCube()
    cube.rotate(old_moves)

    return VCube().to_algorithm(cube)
