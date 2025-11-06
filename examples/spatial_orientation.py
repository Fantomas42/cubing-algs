# ruff: noqa: T201
"""
Demonstrate preservation of the cube spatial orientation
when serializing/deserializing facelets to cubies.
"""
from cubing_algs.vcube import VCube

cube = VCube()
cube.rotate('F R x')
cube.show()

print(cube)

n_cube = VCube.from_cubies(*cube.to_cubies)
n_cube.show()

print(n_cube)
