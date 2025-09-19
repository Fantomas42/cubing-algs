from cubing_algs.constants import INITIAL_STATE
from cubing_algs.masks import CENTERS_MASK
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import facelets_masked
from cubing_algs.palettes import PALETTES
from cubing_algs.vcube import VCube


def show_cube_palette(palette_name):
    print(palette_name.upper())
    print('=' * len(palette_name))

    print('\nInitial:')

    cube = VCube()
    cube.show(palette=palette_name)

    print('\nMoved:')

    cube.rotate("F R U D L B R2 F' D2 B'")
    cube.show(palette=palette_name)

    print('\nMoved masked:')

    cube.show(palette=palette_name, mask=CENTERS_MASK)

    print('\nExtended:')

    cube.show(palette=palette_name, mode='extended')

    print('\nHidden:')

    cube = VCube(facelets_masked(INITIAL_STATE, F2L_MASK), check=False)
    cube.show(palette=palette_name)


for palette_name in PALETTES:
    show_cube_palette(palette_name)
