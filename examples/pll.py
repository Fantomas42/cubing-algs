"""Demonstrate PLL (Permute Last Layer) visualization mode."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("y x' L2 U' L2 D F2 R2 U R2 D' F2")  # T Perm

print('Before:')
c.show()

print('After:')
c.show(mode='pll')

print('After LD orientation:')
c.show(mode='pll', orientation='LD')

print('After DL orientation:')
c.show(mode='pll', orientation='DL')
