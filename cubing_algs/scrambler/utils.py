"""Utility functions for advanced scrambler modules."""
import kociemba

from cubing_algs.initial_state import INITIAL_STATE_3x3x3
from cubing_algs.vcube import VCube


def vcube_to_kociemba_string(cube: VCube) -> str:
    """
    Convert VCube state to Kociemba solver format.

    The Kociemba format is a 54-character string representing the cube state
    in a specific facelet ordering: URFDLB (U face, then R, then F, etc.).
    Each face is read in row-major order (left-to-right, top-to-bottom).

    Args:
        cube: VCube instance (must be 3x3x3).

    Returns:
        54-character string in Kociemba format (URFDLB ordering).

    Raises:
        ValueError: If cube is not 3x3x3.

    """
    if cube.size != 3:
        msg = (
            f'Kociemba solver only supports 3x3x3 cubes, '
            f'got {cube.size}x{cube.size}x{cube.size}'
        )
        raise ValueError(msg)

    # VCube uses URFDLB ordering, which matches Kociemba
    # Just need to ensure we return the state string directly
    return cube.state


def solve_to_algorithm(kociemba_state: str) -> str:
    """
    Generate solving algorithm for a given cube state using Kociemba solver.

    This function requires the kociemba package to be installed.
    Install with: pip install kociemba

    Args:
        kociemba_state: Cube state in Kociemba format (54-character string).

    Returns:
        Algorithm string to solve the cube (space-separated moves).

    """
    if kociemba_state == INITIAL_STATE_3x3x3:
        return ''

    solution: str = kociemba.solve(kociemba_state)
    return solution
