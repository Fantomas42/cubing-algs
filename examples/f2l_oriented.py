from cubing_algs.vcube import VCube

c = VCube()

c.rotate("y2 z2 R U' R' U R' F R F' U")

print('Before:')
c.show()

print('After:')
c.show('f2l')
