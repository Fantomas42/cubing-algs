"""
Utilities for expanding parenthesis notation in cube algorithms.

This module handles expansion of:
- Multipliers: (R U)3 → R U R U R U
- Inversions: (R U)' → U' R'
- Combined: (R U)3' → U' R' U' R' U' R'
"""
import re

from cubing_algs.algorithm import Algorithm
from cubing_algs.transform.mirror import mirror_moves


def apply_multiplier(content: str, multiplier: int) -> str:
    """
    Apply multiplier to content.

    Returns:
        Content repeated multiplier times, joined with spaces.

    """
    if multiplier > 0:
        return ' '.join([content] * multiplier)
    return ''


def apply_inversion(old_moves: str) -> str:
    """
    Apply inversion to content.

    Returns:
        Content with moves reversed and each move inverted.

    """
    algo = Algorithm.parse_moves(old_moves)

    return str(algo.transform(mirror_moves))


def expand_parenthesis_multipliers_and_inversions(moves: str) -> str:
    """
    Expand parenthesis multipliers and inversions.

    Handles three patterns:
    - (R U)3 - repeat 3 times
    - (R U)' - invert (reverse and invert each move)
    - (R U)3' - repeat 3 times then invert

    Parentheses without modifiers are left as-is (to be removed by cleaning).
    Handles nested parentheses from inside out.

    Args:
        moves: A string containing move sequences with parenthesis modifiers.

    Returns:
        The expanded move string with all modifiers resolved.

    Examples:
        "(R U R' U')3" -> "R U R' U' R U R' U' R U R' U'"
        "(R U)'" -> "U' R'"
        "(R U R' U')3'" -> "U R U' R' U R U' R' U R U' R'"
        "((R U)2)3" -> "R U R U R U R U R U R U" (6 times total)

    """
    result = moves
    max_iterations = 100
    iteration = 0

    while iteration < max_iterations:
        # Try multiplier with inversion: (...)N'
        match = re.search(r"\(([^()]*)\)(\d+)'", result)
        if match:
            content = match.group(1).strip()
            multiplier = int(match.group(2))
            expanded = apply_inversion(apply_multiplier(content, multiplier))
            result = result[:match.start()] + expanded + result[match.end():]
            iteration += 1
            continue

        # Try just multiplier: (...)N
        match = re.search(r'\(([^()]*)\)(\d+)', result)
        if match:
            content = match.group(1).strip()
            multiplier = int(match.group(2))
            expanded = apply_multiplier(content, multiplier)
            result = result[:match.start()] + expanded + result[match.end():]
            iteration += 1
            continue

        # Try just inversion: (...)'
        match = re.search(r"\(([^()]*)\)'", result)
        if match:
            content = match.group(1).strip()
            expanded = apply_inversion(content)
            result = result[:match.start()] + expanded + result[match.end():]
            iteration += 1
            continue

        break

    return result.strip()
