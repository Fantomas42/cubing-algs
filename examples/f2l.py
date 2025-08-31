from cubing_algs.vcube import VCube

c = VCube()

c.rotate("z2 R U R' U' z2")

c.show(
    orientation='z2',
    mode='f2l',
)
