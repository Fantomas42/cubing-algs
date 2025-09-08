from cubing_algs.vcube import VCube

c = VCube()

c.rotate("z2 B' U' B F U F' U2")

print('Before:')
c.show()

print('After:')
c.show('af2l')


print('Special case #1')

c = VCube()
c.rotate("z2 L2 B L B' L B U B' z2")
c.show('af2l')


print('Special case #2')

c = VCube()
c.rotate("z2 R' U2 R U' R' F R F' z2")
c.show('af2l')
