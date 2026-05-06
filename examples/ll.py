"""Demonstrate PLL (Permute Last Layer) visualization mode."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("z2 R U2 R' U' R U' R' z2")  # Anti-sune

print('Before:')
c.show()

print('After:')
c.show(mode='ll')
