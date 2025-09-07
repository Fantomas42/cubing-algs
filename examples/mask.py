from cubing_algs.constants import CROSS_MASK
from cubing_algs.constants import F2L_BL_MASK
from cubing_algs.constants import F2L_BR_MASK
from cubing_algs.constants import F2L_FL_MASK
from cubing_algs.constants import F2L_FR_MASK
from cubing_algs.constants import F2L_MASK
from cubing_algs.constants import L1_MASK
from cubing_algs.constants import L2_MASK
from cubing_algs.constants import L3_MASK
from cubing_algs.constants import OLL_MASK
from cubing_algs.constants import PLL_MASK
from cubing_algs.vcube import VCube


def show_cube_masked(name, mask):
    c = VCube()

    print(name, '====>')
    c.show(mask=mask, orientation='DF')


examples = (
    ['OLL', OLL_MASK],
    ['PLL', PLL_MASK],
    ['Cross', CROSS_MASK],
    ['F2L', F2L_MASK],
    ['F2L FR', F2L_FR_MASK],
    ['F2L FL', F2L_FL_MASK],
    ['F2L BR', F2L_BR_MASK],
    ['F2L BL', F2L_BL_MASK],
    ['L1', L1_MASK],
    ['L2', L2_MASK],
    ['L3', L3_MASK],
)

for name, mask in examples:
    show_cube_masked(name, mask)
