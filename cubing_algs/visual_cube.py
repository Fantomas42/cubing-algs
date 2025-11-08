"""Visual Cube tools."""
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from cubing_algs.algorithm import Algorithm
    from cubing_algs.vcube import VCube

PUZZLE = 3

FORMAT = 'svg'

SIZE = 200

BACKGROUND_COLOR = 't'

SCHEMA = 'wrgyob'

BASE_URL = os.getenv('VISUAL_CUBE_URL', 'https://cube.rider.biz/visualcube.php')

VISUAL_URL = (
    f'{BASE_URL}?fmt={ FORMAT }&size={ SIZE }'
    f'&bg={ BACKGROUND_COLOR }&sch={ SCHEMA }'
)


def visual_cube_algorithm(algorithm: 'Algorithm', size: int = PUZZLE) -> str:
    """
    Generate a VisualCube URL for visualizing an algorithm.

    Args:
        algorithm: The algorithm to visualize.
        size: The puzzle size (default: 3 for 3x3x3).

    Returns:
        A URL string that can be used to display the algorithm visualization.

    """
    moves = ''.join(str(m) for m in algorithm)

    return f'{ VISUAL_URL }&pzl={ size }&alg={ moves }'


def visual_cube_cube(cube: 'VCube') -> str:
    """
    Generate a VisualCube URL for visualizing a cube state.

    Args:
        cube: The VCube instance to visualize.

    Returns:
        A URL string that can be used to display the cube state visualization.

    """
    return f'{ VISUAL_URL }&pzl={ cube.size }&fd={ cube.state.lower() }'
