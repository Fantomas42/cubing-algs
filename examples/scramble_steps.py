# ruff: noqa: T201
"""
Example usage of CFOP step scramble generation functions.

This demonstrates how to generate scrambles for:
- F2L (First Two Layers)
- OLL (Orientation of Last Layer)
- PLL (Permutation of Last Layer)
- OCLL (Orientation of Corners of Last Layer)
- Other last layer variants

With options to control AUF (Adjust U Face) and specific cases.
"""

from random import Random

from cubing_algs.scrambler_steps import scramble_ocll_case
from cubing_algs.scrambler_steps import scramble_step
from cubing_algs.vcube import VCube

RNG = Random()


def show(name, mode, *, auf=False):
    scramble = scramble_step(name, rng=RNG, include_auf=auf)
    print(f'   Scramble: {scramble}')
    print(f'   Moves: {len(scramble)}')

    cube = VCube()
    cube.rotate('z2' + scramble)
    cube.show(mode=mode)


def show_ocll(name):
    scramble = scramble_ocll_case(name, rng=RNG)
    print(f'   Scramble: {scramble}')
    print(f'   Moves: {len(scramble)}')

    cube = VCube()
    cube.rotate('z2' + scramble)
    cube.show(mode='oll')


def main() -> None:
    """Demonstrate CFOP step scramble generation."""
    rng = Random()

    print('=' * 60)
    print('CFOP Step Scramble Examples')
    print('=' * 60)

    # F2L
    print('\n1. F2L (First Two Layers):')
    print('   (Cross + all 4 F2L pairs remaining)')
    show('F2L', 'f2l')

    # OLL
    print('\n2. OLL (Orientation of Last Layer):')
    print('   (All last layer pieces disoriented)')
    show('OLL', 'oll')

    # PLL
    print('\n3. PLL (Permutation of Last Layer):')
    print('   (Last layer oriented, needs permutation)')
    show('PLL', 'pll', auf=True)

    # LL (Full Last Layer)
    print('\n4. LL (Full Last Layer):')
    print('   (Both orientation and permutation unsolved)')
    show('LL', 'pll')

    # OCLL (Orientation of Corners Last Layer)
    print('\n5. OCLL (Corners Orientation):')
    print('   (Only corner orientation unsolved)')
    show('OCLL', 'oll')

    # Specific OCLL Case - Sune
    print('\n6. Specific OCLL Case - Sune:')
    print('   (Generate a specific corner orientation pattern)')
    show_ocll('Sune')

    # Specific OCLL Case - T
    print('\n7. Specific OCLL Case - T:')
    show_ocll('T')

    # ZBLL (corners oriented, everything else scrambled)
    print('\n8. ZBLL (Zborowski-Bruchem Last Layer):')
    print('   (Corners oriented, all pieces permuted)')
    show('ZBLL', 'oll')

    # COLL (Corner Orientation + Last Layer)
    print('\n9. COLL (Corners Orientation of Last Layer):')
    print('   (Corners oriented and permuted)')
    show('COLL', 'oll')

    # Without AUF (no random U layer adjustment)
    print('\n10. PLL without AUF:')
    print('    (No random U layer adjustment at the end)')
    show('PLL', 'pll')

    print('\n' + '=' * 60)
    print('Notes:')
    print('  - F2L = First Two Layers (cross + 4 F2L pairs)')
    print('  - OLL = Orient Last Layer (make top face all yellow)')
    print('  - PLL = Permute Last Layer (solve last layer)')
    print('  - LL = Full Last Layer (OLL + PLL combined)')
    print('  - OCLL = Orient Corners Last Layer (corner orientation only)')
    print('  - ZBLL = Advanced: corners oriented, full last layer')
    print('  - COLL = Advanced: corners oriented and permuted')
    print('  - AUF = Adjust U Face (random U layer rotation)')
    print()
    print('  Available OCLL cases:')
    print('    T, U, L, H, Pi, Sune, AntiSune, Solved')
    print('=' * 60)


if __name__ == '__main__':
    main()
