"""Display masks for displaying different pieces."""
from cubing_algs.annotations import POVDisplayMask

# 0 Dimmed (transparent)
# 1 Visible
# 2 Oriented (masked)
# 3 Removed

EMPTY_MASK: POVDisplayMask = '0' * 54

FULL_MASK: POVDisplayMask = '1' * 54

ORIENTED_MASK: POVDisplayMask = '2' * 54

HIDDEN_MASK: POVDisplayMask = '3' * 54

CROSS_BOTTOM_MASK: POVDisplayMask = (
    '222202222'
    '222202212'
    '222202212'
    '212111212'
    '222202212'
    '222202212'
)

CROSS_TOP_MASK: POVDisplayMask = (
    '212111212'
    '212202222'
    '212202222'
    '222202222'
    '212202222'
    '212202222'
)

F2L_MASK: POVDisplayMask = (
    '000000000'
    '000111111'
    '000111111'
    '111111111'
    '000111111'
    '000111111'
)

F2L_LL_MASK: POVDisplayMask = (
    '111111111'
    '000111111'
    '000111111'
    '111111111'
    '000111111'
    '000111111'
)

F2L_CLL_MASK: POVDisplayMask = (
    '101010101'
    '101000000'
    '101000000'
    '000000000'
    '101000000'
    '101000000'
)

F2L_ELL_MASK: POVDisplayMask = (
    '010101010'
    '010000000'
    '010000000'
    '000000000'
    '010000000'
    '010000000'
)

L3_MASK: POVDisplayMask = (
    '111111111'
    '111000000'
    '111000000'
    '000000000'
    '111000000'
    '111000000'
)

OLL_MASK: POVDisplayMask = (
    '111111111'
    '222000000'
    '222000000'
    '000000000'
    '222000000'
    '222000000'
)

PLL_MASK: POVDisplayMask = (
    '000000000'
    '111000000'
    '111000000'
    '000000000'
    '111000000'
    '111000000'
)

LSE_MASK: POVDisplayMask = (
    '010111010'
    '010000000'
    '010010010'
    '010010010'
    '010000000'
    '010010010'
)

CMLL_MASK: POVDisplayMask = (
    '121222121'
    '121000000'
    '121020020'
    '020020020'
    '121000000'
    '121020020'
)
