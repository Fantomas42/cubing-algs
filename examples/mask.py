from cubing_algs.masks import CENTERS_MASK
from cubing_algs.masks import CORNERS_MASK
from cubing_algs.masks import CROSS_MASK
from cubing_algs.masks import EDGES_MASK
from cubing_algs.masks import F2L_BL_MASK
from cubing_algs.masks import F2L_BR_MASK
from cubing_algs.masks import F2L_FL_MASK
from cubing_algs.masks import F2L_FR_MASK
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import L1_MASK
from cubing_algs.masks import L2_MASK
from cubing_algs.masks import L3_MASK
from cubing_algs.masks import OLL_MASK
from cubing_algs.masks import PLL_MASK
from cubing_algs.masks import intersection_masks
from cubing_algs.masks import union_masks
from cubing_algs.vcube import VCube


def show_cube_masked(name, mask):
    c = VCube()

    print(name, '====>')
    c.show(mask=mask, orientation='DF')


examples = (
    ['CENTERS', CENTERS_MASK],
    ['CORNERS', CORNERS_MASK],
    ['EDGES', EDGES_MASK],
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
    ['CORNERS | EDGES', union_masks(CORNERS_MASK, EDGES_MASK)],
    ['L1 | L3', union_masks(L1_MASK, L3_MASK)],
    [
        'PLL | (F2L FR FL BR BL & L1)',
        union_masks(
            PLL_MASK,
            intersection_masks(
                L1_MASK,
                union_masks(
                    F2L_BL_MASK, F2L_BR_MASK,
                    F2L_FL_MASK, F2L_FR_MASK,
                ),
            ),
        ),
     ],
)

for name, mask in examples:
    show_cube_masked(name, mask)
