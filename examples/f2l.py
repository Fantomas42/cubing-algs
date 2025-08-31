from cubing_algs.vcube import VCube

cube = VCube()

cube.rotate("z2 R U R' U' z2")

cube.show(
    orientation='z2',
    mode='f2l',
)
