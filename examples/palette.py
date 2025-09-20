from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import INITIAL_STATE
from cubing_algs.masks import CENTERS_MASK
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import facelets_masked
from cubing_algs.palettes import PALETTES
from cubing_algs.palettes import load_palette
from cubing_algs.vcube import VCube


def print_colorized(string, colors, line='-'):
    result = '\n' if line == '-' else ''
    result += string + '\n'

    for i, _s in enumerate(string):
        result += colors[i % 6]
        result += line

    result += '\x1b[0;0m'

    print(result)


def show_cube_palette(palette_name):
    palette = load_palette(palette_name)
    colors = [
        '\x1b' + palette[face].split('\x1b')[1].replace('48', '38')
        for face in FACE_ORDER
    ]
    cube_static = VCube()

    cube_moved = VCube()
    cube_moved.rotate("F R U D L B R2 F' D2 B'")

    cube_hidden = VCube(
        facelets_masked(INITIAL_STATE, F2L_MASK),
        check=False,
    )

    print_colorized(palette_name.upper(), colors, '=')
    print_colorized('Initial:', colors)

    cube_static.show(
        palette=palette_name,
    )

    print_colorized('Moved:', colors)
    cube_moved.show(
        palette=palette_name,
    )

    print_colorized('Moved masked:', colors)

    cube_moved.show(
        palette=palette_name,
        mask=CENTERS_MASK,
    )

    print_colorized('Hidden:', colors)

    cube_hidden.show(
        palette=palette_name,
    )

    print_colorized('Extended:', colors)

    cube_moved.show(
        palette=palette_name,
        mode='extended',
    )

    print_colorized('Linear :', colors)
    cube_static.show(
        palette=palette_name,
        mode='linear',
    )
    print()
    cube_moved.show(
        palette=palette_name,
        mode='linear',
    )
    print()
    cube_moved.show(
        palette=palette_name,
        mode='linear',
        mask=CENTERS_MASK,
    )
    print()
    cube_hidden.show(
        palette=palette_name,
        mode='linear',
    )

    print_colorized('Compact linear :', colors)
    cube_static.show(
        palette=palette_name,
        mode='linear',
        facelet='compact',
    )
    print()
    cube_moved.show(
        palette=palette_name,
        mode='linear',
        facelet='compact',
    )
    print()
    cube_moved.show(
        palette=palette_name,
        mode='linear',
        mask=CENTERS_MASK,
        facelet='compact',
    )
    print()
    cube_hidden.show(
        palette=palette_name,
        mode='linear',
        facelet='compact',
    )
    print()


for palette_name in PALETTES:
    show_cube_palette(palette_name)
