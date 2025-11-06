"""Demonstrate condensed facelet display mode for cube visualization."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("R U R' U' L F L' F' z2 F U F' R' F R U' R' F' R z2")

print('Before:')
c.show()
print()
c.show(mode='linear')

print('After:')
c.show(facelet='condensed')
print()
c.show(mode='linear', facelet='condensed')
