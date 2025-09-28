"""
Impact analysis tools for Rubik's cube algorithms.

This module provides functions to analyze the spatial impact of algorithms
on cube facelets, including which facelets are moved, how they move,
and statistical analysis of the algorithm's effect on the cube.
"""
from typing import TYPE_CHECKING
from typing import Any
from typing import NamedTuple

from cubing_algs.constants import FACE_ORDER
from cubing_algs.facelets import cubies_to_facelets

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover
    from cubing_algs.vcube import VCube  # pragma: no cover


class ImpactData(NamedTuple):
    """
    Container for core impact computation results.
    """
    impact_mask: str
    movements: dict[int, int]
    state_unique: str
    state_unique_moved: str
    cube: 'VCube'


def get_impact_data(algorithm: 'Algorithm') -> ImpactData:
    """
    Compute core impact data that other functions can reuse.

    This is the fundamental computation that calculates:
    - Which facelets move (impact mask)
    - Where each facelet moves to (movements)
    - The unique state representations

    All other impact functions should use this as their base computation
    to avoid redundancy.
    """
    from cubing_algs.vcube import VCube  # noqa: PLC0415

    cube = VCube()
    cube.rotate(algorithm)

    # Create unique state with each facelet having a unique character
    state_unique = ''.join([chr(ord('A') + i) for i in range(54)])
    state_unique_moved = cubies_to_facelets(*cube.to_cubies, state_unique)

    # Compute impact mask
    impact_mask = ''.join(
        '0' if f1 == f2 else '1'
        for f1, f2 in zip(state_unique, state_unique_moved, strict=True)
    )

    # Compute movements
    movements = {}
    for original_pos in range(54):
        original_char = state_unique[original_pos]
        final_pos = state_unique_moved.find(original_char)

        # Only record if facelet actually moved
        if final_pos != original_pos:
            movements[original_pos] = final_pos

    return ImpactData(
        impact_mask=impact_mask,
        movements=movements,
        state_unique=state_unique,
        state_unique_moved=state_unique_moved,
        cube=cube,
    )


def compute_face_impact(impact_mask: str) -> dict[str, int]:
    """Calculate face impact from impact mask."""
    face_impact = {}

    for i, face_name in enumerate(FACE_ORDER):
        start_idx = i * 9
        end_idx = start_idx + 9
        face_mask = impact_mask[start_idx:end_idx]
        face_impact[face_name] = face_mask.count('1')

    return face_impact


def compute_displacement(original_pos: int, final_pos: int) -> int:
    """Calculate displacement distance between two positions."""
    # Convert to face coordinates
    orig_face = original_pos // 9
    orig_pos_in_face = original_pos % 9
    orig_row = orig_pos_in_face // 3
    orig_col = orig_pos_in_face % 3

    final_face = final_pos // 9
    final_pos_in_face = final_pos % 9
    final_row = final_pos_in_face // 3
    final_col = final_pos_in_face % 3

    # Manhattan distance
    distance = abs(orig_row - final_row) + abs(orig_col - final_col)

    if orig_face == final_face:
        return distance

    return 3 + distance # TODO handle adjacent


def compute_impacts(algorithm: 'Algorithm') -> dict[str, Any]:
    """
    Compute comprehensive impact metrics for an algorithm.

    Returns:
        dict: Dictionary containing various impact metrics:
        Keys include:
            - impact_mask: Binary mask of impacted facelets
            - impacted_facelets: Total number of moved facelets
            - invariant_facelets: Count of unmoved facelets

            - average_displacement: Average movement distance
            - max_displacement: Maximum movement distance
            - face_impact: Impact breakdown by face
    """
    # TODO review
    impact_data = get_impact_data(algorithm)

    displacements = {
        original_pos: compute_displacement(original_pos, final_pos)
        for original_pos, final_pos in impact_data.movements.items()
    }

    displacement_values = list(displacements.values())
    avg_displacement = (
        sum(displacement_values) / len(displacement_values)
        if displacement_values else 0
    )
    max_displacement = max(displacement_values) if displacement_values else 0

    face_fixed_count = impact_data.impact_mask.count('0')
    face_mobilized_count = impact_data.impact_mask.count('1')

    return {
        'cube': impact_data.cube,
        'transformation_mask': impact_data.impact_mask,

        'facelet_fixed_count': face_fixed_count,
        'facelet_mobilized_count': face_mobilized_count,
        'facelet_scrambled_percent': face_mobilized_count / 54,  # TODO fix 54
        'facelet_permutations': impact_data.movements,

        'facelet_distances': displacements,
        'facelet_distance_mean': avg_displacement,
        'facelet_distance_max': max_displacement,
        'facelet_distance_sum': sum(displacement_values),

        'face_mobility': compute_face_impact(impact_data.impact_mask),
    }
