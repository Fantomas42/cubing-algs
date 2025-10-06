"""
Type stubs for the C extension module.

This module provides optimized C implementations for cube rotations.
"""

def rotate_move(state: str, move: str) -> str:
    """
    Apply a move to a cube state using optimized C implementation.

    Args:
        state: 54-character facelet string representing cube state
        move: Move notation string (e.g., 'R', 'U2', "F'")

    Returns:
        New 54-character facelet string after applying the move
    """
