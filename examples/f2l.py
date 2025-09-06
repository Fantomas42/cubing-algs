from cubing_algs.vcube import VCube

c = VCube()

c.rotate("y' z2 R U R' U' z2 y2")

print('Before:')
c.show()

print('After:')
c.show('f2l')
