"""Demonstrate F2L (First Two Layers) visualization with special cases."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("y' z2 R U R' U'")

print('Before:')
c.show()

print('After:')
c.show(mode='f2l')


print('Special case #1')

c = VCube()
c.rotate("z2 F' L F L'")
c.show(mode='f2l')


print('Special case #2')

c = VCube()

c.rotate("z2 L U' L' U' L U L' U' L U2 L'")
c.show(mode='f2l')


print('Special case #3')

c = VCube()

c.rotate("z2 R' D' R U R' D R U'")
c.show(mode='f2l')


print('Special case #4')

c = VCube()

c.rotate("z2 R U' R' U R U' R' U R U' R'")
c.show(mode='f2l')
