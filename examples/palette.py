import argparse

from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import INITIAL_STATE
from cubing_algs.masks import CENTERS_MASK
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import facelets_masked
from cubing_algs.palettes import PALETTES
from cubing_algs.palettes import load_palette
from cubing_algs.vcube import VCube


def print_colorized(string: str, colors: list[str], line: str = '-') -> None:
    result = '\n' if line == '-' else ''
    result += string + '\n'

    for i, _s in enumerate(string):
        result += colors[i % 6]
        result += line

    result += '\x1b[0;0m'

    print(result)


def show_cube_palette(palette_name: str) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            'Display cube visualizations using different color palettes'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""Available palettes:
{', '.join(sorted(PALETTES.keys()))}

Examples:
  python palette.py                    # Show all palettes
  python palette.py -p default         # Show only default palette
  python palette.py -p neon vibrant    # Show neon and vibrant palettes
""",
    )

    parser.add_argument(
        '-p', '--palettes',
        nargs='*',
        help=(
            'Specific palette(s) to display. '
            'If not specified, all palettes will be shown.'
        ),
    )

    args = parser.parse_args()

    if args.palettes is None:
        palettes_to_show = PALETTES.keys()
    elif len(args.palettes) == 0:
        parser.print_help()
        return
    else:
        palettes_to_show = args.palettes

    for palette_name in palettes_to_show:
        show_cube_palette(palette_name)


if __name__ == '__main__':
    main()
