"""Demonstrate all available letter styles for cube display."""
import argparse

from cubing_algs.display.styles import STYLES
from cubing_algs.vcube import VCube

DEFAULT_SIZES = (2, 3, 4, 5, 6, 7)


def show_cube_style(style_name: str, sizes: tuple[int, ...]) -> None:
    """
    Display cube visualization with a specific letter style.

    Args:
        style_name: Name of the style to apply.
        sizes: Cube sizes to display.

    """
    config = STYLES[style_name]
    config_desc = ', '.join(
        f'{k}: {v}' for k, v in config.items()
    ) if config else '(none)'

    print(style_name.upper())
    print('=' * len(style_name))
    print(f'Config: {config_desc}')

    for size in sizes:
        print(f'Size: {size}')
        cube = VCube(size=size)
        cube.show(
            layout='linear',
            style=style_name,
        )


def main() -> None:
    """Parse command-line arguments and display cube styles."""
    parser = argparse.ArgumentParser(
        description=(
            'Display cube visualizations using different letter styles'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""Available styles:
{', '.join(sorted(STYLES.keys()))}

Examples:
  python style.py                        # Show all styles with all sizes
  python style.py -s default             # Show only default style
  python style.py -s default bold -n 3   # Show default and bold at size 3
  python style.py -n 3 5                 # Show all styles at sizes 3 and 5
""",
    )

    parser.add_argument(
        '-s', '--styles',
        nargs='*',
        help=(
            'Specific style(s) to display. '
            'If not specified, all styles will be shown.'
        ),
    )

    parser.add_argument(
        '-n', '--sizes',
        nargs='+',
        type=int,
        default=None,
        help=(
            'Cube size(s) to display (default: 2 3 4 5 6 7).'
        ),
    )

    args = parser.parse_args()

    if args.styles is not None and len(args.styles) == 0:
        parser.print_help()
        return

    styles_to_show = args.styles if args.styles is not None else STYLES.keys()
    sizes = tuple(args.sizes) if args.sizes is not None else DEFAULT_SIZES

    for style_name in styles_to_show:
        show_cube_style(style_name, sizes)


if __name__ == '__main__':
    main()
