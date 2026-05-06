"""Demonstrate cross visualization mode for CFOP method."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate('z2 B L F L F R F L B R')

print('Orientation (DF)')
print('Before:')
c.show()

print('After (cross bottom):')
c.show(mode='cross')

print('After (cross top):')
c.show(mode='cross-top')
