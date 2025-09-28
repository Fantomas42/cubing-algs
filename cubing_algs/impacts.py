"""
Impact analysis tools for Rubik's cube algorithms.

This module provides functions to analyze the spatial impact of algorithms
on cube facelets, including which facelets are moved, how they move,
and statistical analysis of the algorithm's effect on the cube.
"""
from typing import TYPE_CHECKING
from typing import NamedTuple

from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.facelets import cubies_to_facelets

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover
    from cubing_algs.vcube import VCube  # pragma: no cover


class ImpactData(NamedTuple):
    """
    Container for core impact computation results.
    """
    cube: 'VCube'
    transformation_mask: str

    fixed_count: int
    mobilized_count: int
    scrambled_percent: float
    permutations: dict[int, int]

    distances: dict[int, int]
    distance_mean: float
    distance_max: int
    distance_sum: int

    face_mobility: dict[str, int]


def compute_face_impact(impact_mask: str) -> dict[str, int]:
    """
    Calculate face impact from impact mask.
    """
    face_impact = {}

    for i, face_name in enumerate(FACE_ORDER):
        start_idx = i * 9
        end_idx = start_idx + 9
        face_mask = impact_mask[start_idx:end_idx]
        face_impact[face_name] = face_mask.count('1')

    return face_impact


def compute_distance(original_pos: int, final_pos: int, cube: 'VCube') -> int:
    """
    Calculate displacement distance between two positions.
    """
    orig_face = original_pos // cube.face_size
    orig_face_name = FACE_ORDER[orig_face]
    orig_pos_in_face = original_pos % cube.face_size
    orig_row = orig_pos_in_face // cube.size
    orig_col = orig_pos_in_face % cube.size

    final_face = final_pos // cube.face_size
    final_face_name = FACE_ORDER[final_face]
    final_pos_in_face = final_pos % cube.face_size
    final_row = final_pos_in_face // cube.size
    final_col = final_pos_in_face % cube.size

    # Manhattan distance
    distance = abs(orig_row - final_row) + abs(orig_col - final_col)

    if orig_face == final_face:
        return distance

    factor = 1
    if final_face_name == OPPOSITE_FACES[orig_face_name]:
        factor = 2

    return cube.size * factor + distance


def compute_impacts(algorithm: 'Algorithm') -> ImpactData:
    """
    Compute comprehensive impact metrics for an algorithm.

    Returns:
        ImpactData: Namedtuple containing various impact metrics:
        Metrics include:
            - cube: The VCube impacted
            - transformation_mask: Binary mask of impacted facelets

            - fixed_count: Count of unmoved facelets
            - mobilized_count: Total number of moved facelets
            - scrambled_percent: Percent of moves facelets

            - permutations: The permuted facelets

            - distances: The moved facelets distances
            - distance_mean: Average facelet distance done
            - distance_max: Maximum facelet distance
            - distance_sum: Sum of facelet distances

            - face_mobility: Impact breakdown by face
    """
    from cubing_algs.vcube import VCube  # noqa: PLC0415

    cube = VCube()
    cube.rotate(algorithm)

    # Create unique state with each facelet having a unique character
    state_unique = ''.join(
        [
            chr(ord('A') + i)
            for i in range(cube.face_size * cube.face_number)
        ],
    )
    state_unique_moved = cubies_to_facelets(*cube.to_cubies, state_unique)

    mask = ''.join(
        '0' if f1 == f2 else '1'
        for f1, f2 in zip(state_unique, state_unique_moved, strict=True)
    )

    permutations = {}
    for original_pos in range(54):
        final_pos = state_unique_moved.find(
            state_unique[original_pos],
        )

        if final_pos != original_pos:
            permutations[original_pos] = final_pos

    distances = {
        original_pos: compute_distance(original_pos, final_pos, cube)
        for original_pos, final_pos in permutations.items()
    }

    distance_values = list(distances.values())
    distance_sum = sum(distance_values)
    distance_mean = (
        distance_sum / len(distance_values)
        if distance_values else 0
    )
    distance_max = max(distance_values) if distance_values else 0

    fixed_count = mask.count('0')
    mobilized_count = mask.count('1')
    scrambled_percent = mobilized_count / len(state_unique)

    face_mobility = compute_face_impact(mask)

    return ImpactData(
        cube=cube,
        transformation_mask=mask,

        fixed_count=fixed_count,
        mobilized_count=mobilized_count,
        scrambled_percent=scrambled_percent,

        permutations=permutations,

        distances=distances,
        distance_mean=distance_mean,
        distance_max=distance_max,
        distance_sum=distance_sum,

        face_mobility=face_mobility,
    )
