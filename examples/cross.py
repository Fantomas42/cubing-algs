"""Demonstrate cross visualization mode for CFOP method."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate('B L F L F R F L B R')

print('Before:')
c.show()

print('After:')
c.show('cross')
