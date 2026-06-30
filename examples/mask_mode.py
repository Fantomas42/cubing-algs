"""Demonstrate F2L (First Two Layers) visualization with special cases."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("z2 R U' R' U R U' R' U R U' R'")

for mode in ('full', 'dimmed', 'masked', 'hidden', 'oriented'):
    print(mode.title())
    c.show(mode=mode)
    c.show(mode=mode, facelet='emoji')
