"""Binary masks for identifying and manipulating cube regions and pieces."""
from typing import TYPE_CHECKING

from cubing_algs.annotations import CubeFacelets
from cubing_algs.annotations import Mask
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies
from cubing_algs.solved_state import SOLVED_FACELETS_3x3x3

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm


def union_masks(*masks: Mask) -> Mask:
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


def intersection_masks(*masks: Mask) -> Mask:
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


def negate_mask(mask: Mask) -> Mask:
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


_MASK_CACHE: dict[Mask, tuple[bool, ...]] = {}
_CACHE_SIZE_LIMIT = 1000  # Prevent unbounded memory growth


def facelets_masked(facelets: CubeFacelets, mask: Mask) -> CubeFacelets:
    """
    Apply a binary mask to a facelets string.

    Returns a new facelets string where positions with '0' in the mask
    are replaced with '-', and positions with '1' retain their original value.

    Optimized for high-frequency usage with caching and fast string operations.

    Args:
        facelets: The facelets string to mask.
        mask: The binary mask string.

    Returns:
        The masked facelets string with '-' for masked positions.

    """
    if mask in _MASK_CACHE:
        translation = _MASK_CACHE[mask]
        return ''.join(
            char if keep else '-'
            for char, keep in zip(facelets, translation, strict=True)
        )

    # Build and cache translation for new masks
    translation = tuple(c == '1' for c in mask)

    # Manage cache size to prevent memory bloat
    if len(_MASK_CACHE) >= _CACHE_SIZE_LIMIT:
        # Remove oldest half of cache entries (batch-FIFO eviction)
        items = list(_MASK_CACHE.items())
        _MASK_CACHE.clear()
        _MASK_CACHE.update(items[_CACHE_SIZE_LIMIT // 2:])

    _MASK_CACHE[mask] = translation

    return ''.join(
        char if keep else '-'
        for char, keep in zip(facelets, translation, strict=True)
    )


def state_masked(state: CubeFacelets, mask: Mask) -> CubeFacelets:
    """
    Apply a binary mask to a cube state.

    Converts the state to cubies, applies the mask
    to the initial state facelets, then converts back
    to a facelets representation showing only the masked pieces.

    Args:
        state: The cube state string to mask.
        mask: The binary mask string.

    Returns:
        The masked cube state as a facelets string.

    """
    return cubies_to_facelets(
        *facelets_to_cubies(state),
        facelets_masked(
            SOLVED_FACELETS_3x3x3,
            mask,
        ),
    )


def compute_algorithm_mask(
        algorithm: 'Algorithm',
        size: int = 3,
) -> tuple[Mask, CubeFacelets]:
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


FULL_MASK: Mask = '1' * 54

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

CROSS_MASK = (
    '010111010'
    '010010000'
    '010010000'
    '000000000'
    '010010000'
    '010010000'
)

L1_MASK = (
    '111111111'
    '111000000'
    '111000000'
    '000000000'
    '111000000'
    '111000000'
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
    '000000000'
    '000000111'
    '000000111'
    '111111111'
    '000000111'
    '000000111'
)

F2L_MASK = (
    '111111111'
    '111111000'
    '111111000'
    '000000000'
    '111111000'
    '111111000'
)

F2L_FR_MASK = (
    '000000001'
    '100100000'
    '001001000'
    '000000000'
    '000000000'
    '000000000'
)

F2L_FL_MASK = (
    '000000100'
    '000000000'
    '100100000'
    '000000000'
    '001001000'
    '000000000'
)

F2L_BR_MASK = (
    '001000000'
    '001001000'
    '000000000'
    '000000000'
    '000000000'
    '100100000'
)

F2L_BL_MASK = (
    '100000000'
    '000000000'
    '000000000'
    '000000000'
    '100100000'
    '001001000'
)

F2L_LL_MASK = (
    '111111111'
    '111111000'
    '111111000'
    '111111111'
    '111111000'
    '111111000'
)

F2L_CLL_MASK = (
    '111111111'
    '111111000'
    '111111000'
    '101010101'
    '111111000'
    '111111000'
)

F2L_ELL_MASK = (
    '111111111'
    '111111000'
    '111111000'
    '010111010'
    '111111000'
    '111111000'
)

OLL_MASK = (
    '000000000'
    '000000000'
    '000000000'
    '111111111'
    '000000000'
    '000000000'
)

PLL_MASK = (
    '000000000'
    '000000111'
    '000000111'
    '000000000'
    '000000111'
    '000000111'
)
