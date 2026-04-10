"""Binary masks for identifying and manipulating cube regions and pieces."""
from typing import TYPE_CHECKING

from cubing_algs.annotations import CubeFacelets
from cubing_algs.annotations import CubeMask

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm


def union_masks(*masks: CubeMask) -> CubeMask:
    """
    Perform the union (logical OR) of multiple binary masks.

    Returns '1' if at least one mask has '1' at that position.

    Args:
        *masks: Variable number of binary mask strings.

    Returns:
        The union of all masks as a binary string.

    Raises:
        ValueError: If masks have different lengths.

    """
    if not masks:
        return ''

    length = len(masks[0])
    if not all(len(m) == length for m in masks):
        msg = 'All masks must have the same length'
        raise ValueError(msg)

    result = 0

    for mask in masks:
        result |= int(mask, 2)

    return format(result, f'0{ length }b')


def intersection_masks(*masks: CubeMask) -> CubeMask:
    """
    Perform the intersection (logical AND) of multiple binary masks.

    Returns '1' only if all masks have '1' at that position.

    Args:
        *masks: Variable number of binary mask strings.

    Returns:
        The intersection of all masks as a binary string.

    Raises:
        ValueError: If masks have different lengths.

    """
    if not masks:
        return ''

    length = len(masks[0])
    if not all(len(m) == length for m in masks):
        msg = 'All masks must have the same length'
        raise ValueError(msg)

    result = int(masks[0], 2)

    for mask in masks[1:]:
        result &= int(mask, 2)

    return format(result, f'0{ length }b')


def negate_mask(mask: CubeMask) -> CubeMask:
    """
    Invert a binary mask (logical NOT).

    '0' becomes '1' and '1' becomes '0'.

    Args:
        mask: The binary mask string to invert.

    Returns:
        The inverted mask as a binary string.

    """
    if not mask:
        return ''

    length = len(mask)
    mask_int = int(mask, 2)

    all_ones = (1 << length) - 1
    negated = mask_int ^ all_ones

    return format(negated, f'0{ length }b')


def compute_algorithm_mask(
        algorithm: 'Algorithm',
        size: int = 3,
) -> tuple[CubeMask, CubeFacelets]:
    """
    Compute an orientation-aware binary mask of facelets
    affected by an algorithm.

    The mask is expressed in solved-state coordinates: each
    position in the string corresponds to the facelet at that
    index on a solved cube.  This means the mask defines
    precisely which physical facelet positions are tracked,
    regardless of any whole-cube reorientation the algorithm
    may perform.  Callers that need the mask in display
    coordinates (after rotations) can re-apply the full
    algorithm to permute the '1' bits into their final
    positions.

    Problem: when an algorithm contains rotations (e.g. y R),
    comparing unique_facelets with cube_mask.state would mark
    every facelet as moved — the rotation displaces all of
    them.  We only want to highlight facelets moved by the
    face turns (R), not by the rotations (y).

    Solution: strip rotations before applying to the mask
    cube.  degrip_full_moves absorbs inline rotations into
    face moves (y R → B y), then split_moves_ending_rotations
    separates the trailing rotations.  For "y R":

      degrip:  y R  →  B y
      split:   B y  →  face_moves=B, rotations=y

      cube_mask.rotate(B)  =  B(identity)
      unique_facelets      =  identity

      comparison: identity vs B(identity)
          → only B-affected positions get '1'

    Args:
        algorithm: The algorithm to analyze.
        size: Size of the cube.

    Returns:
        A tuple of:
        - A binary mask string ('0'/'1'), one character per
          facelet in solved-state order.  '1' means the
          facelet at that position was moved by the algorithm.
        - The transformed unique facelets state, useful for
          computing permutations by the caller.

    """
    from cubing_algs.solved_state import get_unique_facelets  # noqa: PLC0415
    from cubing_algs.transform.degrip import degrip_full_moves  # noqa: PLC0415
    from cubing_algs.transform.rotation import (  # noqa: PLC0415
        split_moves_ending_rotations,
    )
    from cubing_algs.vcube import VCube  # noqa: PLC0415

    unique_facelets = get_unique_facelets(size)
    deoriented_algo, _orientation = split_moves_ending_rotations(
        degrip_full_moves(algorithm),
    )

    cube_mask = VCube(
        initial=unique_facelets,
        size=size,
        check=False,
    )
    cube_mask.rotate(deoriented_algo)

    mask = ''.join(
        '0' if f1 == f2 else '1'
        for f1, f2 in zip(
                unique_facelets,
                cube_mask.state,
                strict=True,
        )
    )

    return mask, cube_mask.state


FULL_MASK: CubeMask = '1' * 54

# Masks are mainly used to highlight or hide facelets when displaying a cube
# state, making it easy to focus on a specific solving feature (OLL, PLL,
# F2L, cross, etc.).
#
# A mask is a 54-character binary string in facelet-state format (same layout
# as VCube.state). '1' highlights a facelet; '0' hides it.
#
# Masks are written from the user's point of view: setting U facelets to '1'
# means "highlight what I see on top". This is more intuitive than working in
# solved-cube coordinates and makes masks color-neutral — they describe
# positions, not which color occupies them, so the same mask works regardless
# of the cube's color scheme or orientation.
#
# Internally, when a mask is used via a display mode, it is first converted
# from user-POV to cube coordinates before being tracked through the move
# history. For example, if the user holds the cube with yellow on top (a z2
# from the solved state), a mask with U='1' is transformed to D='1' in
# internal coordinates, then rotated through the algorithm moves so the
# highlighted facelets follow the right stickers.
#
# Example: PLL_MASK highlights the top row of all four side faces — the
# stickers the user sees at the top of F, B, L, R. A PLL algorithm permutes
# those pieces without rotations. Because the user holds the cube z2, the mask
# is converted to track the D-adjacent rows internally, correctly following
# each sticker as it is permuted by the algorithm.

CENTERS_MASK = (
    '000010000'
    '000010000'
    '000010000'
    '000010000'
    '000010000'
    '000010000'
)

CORNERS_MASK = (
    '101000101'
    '101000101'
    '101000101'
    '101000101'
    '101000101'
    '101000101'
)

EDGES_MASK = (
    '010101010'
    '010101010'
    '010101010'
    '010101010'
    '010101010'
    '010101010'
)

CROSS_BOTTOM_MASK = (
    '000000000'
    '000010010'
    '000010010'
    '010111010'
    '000010010'
    '000010010'
)

CROSS_TOP_MASK = (
    '010111010'
    '010010000'
    '010010000'
    '000000000'
    '010010000'
    '010010000'
)

L1_MASK = (
    '000000000'
    '000000111'
    '000000111'
    '111111111'
    '000000111'
    '000000111'
)

L2_MASK = (
    '000000000'
    '000111000'
    '000111000'
    '000000000'
    '000111000'
    '000111000'
)

L3_MASK = (
    '111111111'
    '111000000'
    '111000000'
    '000000000'
    '111000000'
    '111000000'
)

F2L_MASK = (
    '000000000'
    '000111111'
    '000111111'
    '111111111'
    '000111111'
    '000111111'
)

F2L_FR_MASK = (
    '000000000'
    '000100100'
    '000001001'
    '001000000'
    '000000000'
    '000000000'
)

F2L_FL_MASK = (
    '000000000'
    '000000000'
    '000100100'
    '100000000'
    '000001001'
    '000000000'
)

F2L_BR_MASK = (
    '000000000'
    '000001001'
    '000000000'
    '000000001'
    '000000000'
    '000100100'
)

F2L_BL_MASK = (
    '000000000'
    '000000000'
    '000000000'
    '000000100'
    '000100100'
    '000001001'
)

F2L_LL_MASK = (
    '111111111'
    '000111111'
    '000111111'
    '111111111'
    '000111111'
    '000111111'
)

F2L_CLL_MASK = (
    '101010101'
    '000111111'
    '000111111'
    '111111111'
    '000111111'
    '000111111'
)

F2L_ELL_MASK = (
    '010111010'
    '000111111'
    '000111111'
    '111111111'
    '000111111'
    '000111111'
)

OLL_MASK = (
    '111111111'
    '000000000'
    '000000000'
    '000000000'
    '000000000'
    '000000000'
)

PLL_MASK = (
    '000000000'
    '111000000'
    '111000000'
    '000000000'
    '111000000'
    '111000000'
)
