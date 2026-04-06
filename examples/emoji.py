"""Demonstrate emoji facelet display mode for cube visualization."""
# ruff: noqa: T201
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import OLL_MASK
from cubing_algs.solved_state import SOLVED_FACELETS_3x3x3
from cubing_algs.vcube import VCube


def facelets_masked(state: str, mask: str) -> str:
    """
    Mask facelets.

    Returns:
      A state masked.

    """
    masked = []
    for i, m in enumerate(mask):
        if m == '1':
            masked.append(state[i])
        else:
            masked.append('-')

    return ''.join(masked)


c = VCube()

c.rotate("R U R' U' L F L' F' z2 F U F' R' F R U' R' F' R z2")

c_hidden = VCube(
    facelets_masked(SOLVED_FACELETS_3x3x3, F2L_MASK),
    check=False,
)

c_hidden.rotate("R U R' U' L F L' F' z2 F U F' R' F R U' R' F' R z2")

print('Before:')
c.show()
print()
c.show(layout='linear')
print()
c.show(layout='linear', mask=OLL_MASK)
print()
c_hidden.show(layout='linear')


print('After:')
c.show(facelet='emoji')
print()
c.show(layout='linear', facelet='emoji')
print()
c.show(layout='linear', facelet='emoji', mask=OLL_MASK)
print()
c_hidden.show(layout='linear', facelet='emoji')
