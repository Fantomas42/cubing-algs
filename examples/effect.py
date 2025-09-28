from cubing_algs.effects import EFFECTS
from cubing_algs.vcube import VCube


def show_cube_effect(effect_name: str) -> None:
    print(effect_name.upper())
    print('=' * len(effect_name))

    print('\nInitial:')

    cube = VCube()
    cube.show(
        effect=effect_name,
    )

    print('\nMoved:')

    cube.rotate("F R U D L B R2 F' D2 B'")
    cube.show(
        effect=effect_name,
    )

    print()


for effect in EFFECTS:
    show_cube_effect(effect)
