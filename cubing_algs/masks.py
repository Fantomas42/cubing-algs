def union_masks(*masks):
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


def intersection_masks(*masks):
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


def negate_mask(mask):
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
