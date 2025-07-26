from cubing_algs.vcube import VCube

cube = VCube()
scramble = "U2 D2 F U2 F2 U R' L U2 R2 U' B2 D R2 L2 F2 U' L2 D F2 U'" * 100


print(cube.rotate(scramble))
