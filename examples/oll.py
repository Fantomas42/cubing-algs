"""Demonstrate OLL (Orient Last Layer) visualization mode."""
# ruff: noqa: T201
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("z2 F U F' R' F R U' R' F' R z2")  # 14 Anti-Gun

print('Before:')
c.show()

print('After:')
c.show('oll')
