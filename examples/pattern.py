"""Demonstrate cube pattern visualization using predefined patterns."""
from cubing_algs.patterns import get_pattern
from cubing_algs.vcube import VCube

c = VCube()

c.rotate(get_pattern('3T'))

c.show()
