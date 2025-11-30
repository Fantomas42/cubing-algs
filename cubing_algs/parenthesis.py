"""
Utilities for expanding parenthesis notation in cube algorithms.

This module handles expansion of:
- Multipliers: (R U)3 → R U R U R U
- Inversions: (R U)' → U' R'
- Combined: (R U)3' → U' R' U' R' U' R'
"""
import re
from re import Match

from cubing_algs.algorithm import Algorithm
from cubing_algs.transform.mirror import mirror_moves

# Compiled regex patterns for performance
_MULT_INV_PATTERN = re.compile(r"\(([^()]*)\)(\d+)'")
_MULT_PATTERN = re.compile(r'\(([^()]*)\)(\d+)')
_INV_PATTERN = re.compile(r"\(([^()]*)\)'")


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


def find_innermost_parenthesis_with_modifier(
    text: str,
) -> tuple[int, int, str, Match[str]] | None:
    """
    Find the innermost parenthesis that has a modifier
    (multiplier or inversion).

    Args:
        text: A string potentially containing nested parentheses with modifiers.

    Returns:
        A tuple of (start_index, end_index, modifier_type, match_object),
        where modifier_type is 'mult_inv', 'mult', or 'inv', or None if no
        parenthesis with modifier is found.

    """
    # Try multiplier with inversion: (...)N'
    match = _MULT_INV_PATTERN.search(text)
    if match:
        return (match.start(), match.end(), 'mult_inv', match)

    # Try just multiplier: (...)N
    match = _MULT_PATTERN.search(text)
    if match:
        return (match.start(), match.end(), 'mult', match)

    # Try just inversion: (...)'
    match = _INV_PATTERN.search(text)
    if match:
        return (match.start(), match.end(), 'inv', match)

    return None


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

    while True:
        paren_info = find_innermost_parenthesis_with_modifier(result)
        if paren_info is None:
            break

        start, end, modifier_type, match = paren_info

        # Extract content and modifier details from the match object
        if modifier_type == 'mult_inv':
            content = match.group(1).strip()
            multiplier = int(match.group(2))
            expanded = apply_inversion(apply_multiplier(content, multiplier))
        elif modifier_type == 'mult':
            content = match.group(1).strip()
            multiplier = int(match.group(2))
            expanded = apply_multiplier(content, multiplier)
        else:  # modifier_type == 'inv'
            content = match.group(1).strip()
            expanded = apply_inversion(content)

        result = result[:start] + expanded + result[end:]

    return result.strip()
