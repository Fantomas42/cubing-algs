"""Display masks for displaying different pieces."""
from cubing_algs.annotations import POVDisplayMask

# 0 Dimmed (transparent)
# 1 Visible
# 2 Masked
# 3 Removed

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

L3_MASK: POVDisplayMask = (
    '111111111'
    '111000000'
    '111000000'
    '000000000'
    '111000000'
    '111000000'
)
