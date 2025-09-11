from cubing_algs.constants import INITIAL_STATE
from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies


def union_masks(*masks) -> str:
    """
    Performs the union (logical OR) of multiple binary masks.

    Returns '1' if at least one mask has '1' at that position.
    """
    if not masks:
        return ''

    length = len(masks[0])
    result = 0

    for mask in masks:
        result |= int(mask, 2)

    return format(result, f'0{ length }b')


def intersection_masks(*masks) -> str:
    """
    Performs the intersection (logical AND) of multiple binary masks.

    Returns '1' only if all masks have '1' at that position.
    """
    if not masks:
        return ''

    length = len(masks[0])
    result = int(masks[0], 2)

    for mask in masks[1:]:
        result &= int(mask, 2)

    return format(result, f'0{ length }b')


def negate_mask(mask: str) -> str:
    """
    Inverts a binary mask (logical NOT).

    '0' becomes '1' and '1' becomes '0'.
    """
    if not mask:
        return ''

    length = len(mask)
    mask_int = int(mask, 2)

    all_ones = (1 << length) - 1
    negated = mask_int ^ all_ones

    return format(negated, f'0{ length }b')


def facelets_masked(facelets: str, mask: str) -> str:
    """
    Applies a binary mask to a facelets string.

    Returns a new facelets string where positions with '0' in the mask
    are replaced with '0', and positions with '1' retain their original value.
    """
    masked = []

    for i, value in enumerate(facelets):
        if mask[i] == '0':
            masked.append('-')
        else:
            masked.append(value)

    return ''.join(masked)


def state_masked(state: str, mask: str) -> str:
    """
    Applies a binary mask to a cube state.

    Converts the state to cubies, applies the mask
    to the initial state facelets, then converts back
    to a facelets representation showing only the masked pieces.
    """
    return cubies_to_facelets(
        *facelets_to_cubies(state),
        facelets_masked(
            INITIAL_STATE,
            mask,
        ),
    )


FULL_MASK = '1' * 54

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
