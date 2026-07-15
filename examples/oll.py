"""Demonstrate OLL (Orient Last Layer) visualization mode."""
from cubing_algs.vcube import VCube

c = VCube()

c.rotate("y x F U F' R' F R U' R' F' R")  # 14 Anti-Gun

print('Before:')
c.show()

print('After:')
c.show(mode='oll')

print('After RU orientation:')
c.show(mode='oll', orientation='RU')

print('After UR orientation:')
c.show(mode='oll', orientation='UR')
