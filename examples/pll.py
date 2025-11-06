"""Demonstrate PLL (Permute Last Layer) visualization mode."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("z2 L2 U' L2 D F2 R2 U R2 D' F2 z2")  # T Perm

print('Before:')
c.show()

print('After:')
c.show('pll')
