"""Demonstrate state masking functionality for cube visualization."""
# ruff: noqa: T201
from cubing_algs.masks import F2L_MASK
from cubing_algs.masks import state_masked
from cubing_algs.vcube import VCube

base_cube = VCube()
base_cube.rotate("R U R' U'")

print('Facelets masked')
base_cube.show(mask=F2L_MASK)


new_cube = VCube(
    state_masked(base_cube.state, F2L_MASK),
    check=False,
)

print('State masked')
new_cube.show()
