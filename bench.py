import timeit
from cubing_algs.vcube import VCube

scramble = "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'" * 100

cube = VCube()
print(timeit.timeit(lambda: cube.rotate(scramble, True), number=10000))

cube = VCube()
print(timeit.timeit(lambda: cube.rotate(scramble, False), number=10000))
