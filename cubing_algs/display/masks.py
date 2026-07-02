"""Display masks for displaying different pieces."""
from cubing_algs.annotations import POVDisplayMask

# 0 Dimmed
# 1 Visible
# 2 Masked
# 3 Hidden
# 4 Oriented

DIMMED_MASK: POVDisplayMask = '0' * 54

VISIBLE_MASK: POVDisplayMask = '1' * 54

MASKED_MASK: POVDisplayMask = '2' * 54

HIDDEN_MASK: POVDisplayMask = '3' * 54

ORIENTED_MASK: POVDisplayMask = '4' * 54

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

AF2L_MASK: POVDisplayMask = (
    '222222222'
    '222111111'
    '222111111'
    '111111111'
    '222111111'
    '222111111'
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

EO_MASK: POVDisplayMask = (
    '242414242'
    '222212222'
    '222414222'
    '242414242'
    '222212222'
    '222414222'
)

EO_LINE_MASK: POVDisplayMask = (
    '242414242'
    '222212222'
    '222414212'
    '212414212'
    '222212222'
    '222414212'
)

EO_CROSS_MASK: POVDisplayMask = (
    '242414242'
    '222212212'
    '222414212'
    '212111212'
    '222212212'
    '222414212'
)

EO_SLICE_MASK: POVDisplayMask = (
    '242414242'
    '222212212'
    '222414222'
    '242111242'
    '222212212'
    '222414222'
)

EO_EDGE_MASK: POVDisplayMask = (
    '242414242'
    '222212222'
    '222114222'
    '242414242'
    '222111222'
    '222411222'
)
