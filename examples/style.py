"""Demonstrate all available letter styles for cube display."""
# ruff: noqa: T201
from cubing_algs.styles import STYLES
from cubing_algs.vcube import VCube


def show_cube_style(style_name: str) -> None:
    """
    Display cube visualization with a specific letter style.

    Args:
        style_name: Name of the style to apply.

    """
    config = STYLES[style_name]
    config_desc = ', '.join(
        f'{k}: {v}' for k, v in config.items()
    ) if config else '(none)'

    print(style_name.upper())
    print('=' * len(style_name))
    print(f'Config: {config_desc}')

    print('\nInitial:')

    cube = VCube()
    cube.show(
        style=style_name,
    )

    print('\nMoved:')

    cube.rotate("F R U D L B R2 F' D2 B'")
    cube.show(
        style=style_name,
    )

    print()


for style in STYLES:
    show_cube_style(style)
