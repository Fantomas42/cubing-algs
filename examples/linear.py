"""Demonstrate linear display mode for cube visualization."""
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("R U R' U' L F L' F' z2 F U F' R' F R U' R' F' R z2")

print('Before:')
c.show()

print('After:')
c.show(layout='linear')
