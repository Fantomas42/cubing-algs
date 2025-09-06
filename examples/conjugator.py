from cubing_algs.parsing import parse_moves
from cubing_algs.vcube import VCube

c = VCube()

c.rotate(parse_moves('[[R: U], D] B [F: [U, R]]'))

c.show()
