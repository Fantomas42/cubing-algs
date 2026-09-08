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
    '222222222'
    '222111111'
    '222111111'
    '111111111'
    '222111111'
    '222111111'
)

F2L_FR_MASK: POVDisplayMask = (
    '222222222'
    '222112112'
    '222211211'
    '211211222'
    '222222222'
    '222222222'
)

F2L_FL_MASK: POVDisplayMask = (
    '222222222'
    '222222222'
    '222112112'
    '112112222'
    '222211211'
    '222222222'
)

F2L_BR_MASK: POVDisplayMask = (
    '222222222'
    '222211211'
    '222222222'
    '222211211'
    '222222222'
    '222112112'
)

F2L_BL_MASK: POVDisplayMask = (
    '222222222'
    '222222222'
    '222222222'
    '222112112'
    '222112112'
    '222211211'
)

AF2L_MASK: POVDisplayMask = (
    '000000000'
    '000111111'
    '000111111'
    '111111111'
    '000111111'
    '000111111'
)

LL_MASK: POVDisplayMask = (
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

OCLL_MASK: POVDisplayMask = (
    '101000101'
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

CPLL_MASK: POVDisplayMask = (
    '000000000'
    '101000000'
    '101000000'
    '000000000'
    '101000000'
    '101000000'
)

EPLL_MASK: POVDisplayMask = (
    '000000000'
    '010000000'
    '010000000'
    '000000000'
    '010000000'
    '010000000'
)

ZBLL_MASK: POVDisplayMask = (
    '101000101'
    '111000000'
    '111000000'
    '000000000'
    '111000000'
    '111000000'
)

CLL_MASK: POVDisplayMask = (
    '121222121'
    '121000000'
    '121000000'
    '000000000'
    '121000000'
    '121000000'
)

COLL_MASK: POVDisplayMask = (
    '101000101'
    '121000000'
    '121000000'
    '000000000'
    '121000000'
    '121000000'
)

ELL_MASK: POVDisplayMask = (
    '212121212'
    '212000000'
    '212000000'
    '000000000'
    '212000000'
    '212000000'
)

EOLL_MASK: POVDisplayMask = (
    '212111212'
    '222000000'
    '222000000'
    '000000000'
    '222000000'
    '222000000'
)

LS_MASK: POVDisplayMask = (
    '222202222'
    '222100100'
    '222001001'
    '001000000'
    '222000000'
    '222000000'
)

LS_OLL_MASK: POVDisplayMask = (
    '111111111'
    '222100100'
    '222001001'
    '001000000'
    '222000000'
    '222000000'
)

LS_OCLL_MASK: POVDisplayMask = (
    '101000101'
    '222100100'
    '222001001'
    '001000000'
    '222000000'
    '222000000'
)

ELS_MASK: POVDisplayMask = (
    '212111212'
    '222100200'
    '222001002'
    '002000000'
    '222000000'
    '222000000'
)

ZBLS_MASK: POVDisplayMask = (
    '212111212'
    '222100100'
    '222001001'
    '001000000'
    '222000000'
    '222000000'
)

CLS_MASK: POVDisplayMask = (
    '101000101'
    '222000100'
    '222000001'
    '001000000'
    '222000000'
    '222000000'
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
    '222112222'
    '222111222'
    '242414242'
    '222211222'
    '222414222'
)

L6EO_MASK: POVDisplayMask = (
    '040414040'  # U edges oriented, center reference
    '020000000'  # UR side sticker masked
    '020010020'  # UF / DF side stickers masked, center reference
    '040010040'  # DF / DB edges oriented, center reference
    '020000000'  # UL side sticker masked
    '020010020'  # UB / DB side stickers masked, center reference
)

L10P_MASK: POVDisplayMask = (
    '111111111'  # last layer corners + edges + center visible
    '111000000'  # LL corners + UR edge visible
    '111010010'  # LL corners + UF / DF edges + center visible
    '010010010'  # DF / DB edges + center visible
    '111000000'  # LL corners + UL edge visible
    '111010010'  # LL corners + UB / DB edges + center visible
)

NO_CENTER_MASK: POVDisplayMask = (
    '111131111'
    '111131111'
    '111131111'
    '111131111'
    '111131111'
    '111131111'
)

NO_CORNER_MASK: POVDisplayMask = (
    '313111313'
    '313111313'
    '313111313'
    '313111313'
    '313111313'
    '313111313'
)

NO_EDGE_MASK: POVDisplayMask = (
    '131313131'
    '131313131'
    '131313131'
    '131313131'
    '131313131'
    '131313131'
)
