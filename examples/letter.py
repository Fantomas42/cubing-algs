"""Demonstrate cube pattern visualization using predefined letter patterns."""
from cubing_algs.patterns import ALPHABET
from cubing_algs.patterns import get_letter
from cubing_algs.vcube import VCube

for letter in ALPHABET:
    print(letter)
    print('=')
    c = VCube()
    c.rotate(get_letter(letter))
    c.show()
