# ruff: noqa: T201
"""
Example usage of step-based scramble generation functions.

This demonstrates how to generate scrambles for various speedcubing methods:
- CFOP (Fridrich): F2L, OLL, PLL, and variants
- ZZ Method: ZZF2L, ZZRB, ZZLS, ZZLL
- Roux Method: SB, CMLL, CMLLEO
- Petrus Method: PETRUS2X2X3, PETRUSEO, PETRUSF2L
- Last Layer variants: LL, CLL, OLLCP, COLL, ZBLL, 2GLL, OCLL, ELL, EPLL, CPLL
- Last Slot variants: LS, ELS, TSLE, CLS, CPLS, EJLS, EJF2L, TTLL, WV, SV,
  VLS, VHLS

With options to control AUF (Adjust U Face) and specific OCLL cases.

Usage:
    python scramble_steps.py                  # Run all demos
    python scramble_steps.py --list           # List available steps
    python scramble_steps.py -m cfop          # Show only CFOP steps
    python scramble_steps.py -m zz roux       # Show ZZ and Roux steps
    python scramble_steps.py -s PLL OLL       # Show specific steps
    python scramble_steps.py --ocll           # Show all OCLL cases
    python scramble_steps.py --ocll Sune T    # Show specific OCLL cases
    python scramble_steps.py --auf            # Enable AUF
    python scramble_steps.py --seed 123       # Set random seed
"""

import argparse
from random import Random

from cubing_algs.constants import ORIENTATION_FACE_MOVES
from cubing_algs.constants import ORIENTATIONS
from cubing_algs.scrambler import scramble_ocll_case
from cubing_algs.scrambler import scramble_step
from cubing_algs.scrambler.steps import SUPPORTED_STEPS
from cubing_algs.vcube import VCube

# OCLL cases available
OCLL_CASES = ['T', 'U', 'L', 'H', 'Pi', 'Sune', 'AntiSune', 'Solved']

# Steps organized by method
METHODS: dict[str, list[str]] = {
    'cfop': [
        'F2L',
        'OLL',
        'PLL',
        'LL',
    ],
    'cfop-ll': [
        'CLL',
        'OLLCP',
        'COLL',
        'ZBLL',
        'OCLL',
        'ELL',
        'EPLL',
        'CPLL',
    ],
    'cfop-ls': [
        'LS',
        'ELS',
        'CLS',
        'CPLS',
        'EJLS',
        'EJF2L',
        'TTLL',
        'WV',
        'SV',
        'VLS',
        'VHLS',
    ],
    'zz': [
        'ZZF2L',
        'ZZRB',
        'ZZLS',
        'TSLE',
        'ZZLL',
        '2GLL',
    ],
    'roux': [
        'SB',
        'CMLL',
        'CMLLEO',
    ],
    'petrus': [
        'PETRUS2X2X3',
        'PETRUSEO',
        'PETRUSF2L',
    ],
}

# Step descriptions and display modes
STEP_INFO: dict[str, tuple[str, str]] = {
    # Last Layer steps
    'LL': ('Full Last Layer (orientation + permutation)', 'll'),
    'OLL': ('Orient Last Layer (make top face yellow)', 'oll'),
    'PLL': ('Permute Last Layer (oriented, needs permutation)', 'pll'),
    'CLL': ('Corners Last Layer (corners + edges scrambled)', 'oll'),
    'OLLCP': ('OLL + Corner Permutation', 'oll'),
    'COLL': ('Corner OLL (corners oriented+permuted)', 'oll'),
    'ZBLL': ('Zborowski-Bruchem LL (corners oriented, all permuted)', 'll'),
    '2GLL': ('2-Gen Last Layer (phase edges only)', 'oll'),
    'OCLL': ('Orient Corners Last Layer (corner orientation only)', 'oll'),
    'ELL': ('Edge Last Layer (edge orientation + permutation)', 'pll'),
    'EPLL': ('Edge Permutation Last Layer (edges permuted only)', 'pll'),
    'CPLL': ('Corner Permutation Last Layer (corners permuted only)', 'pll'),
    'ZZLL': ('ZZ Last Layer (phase edges, corners oriented)', 'll'),
    # F2L variants
    'F2L': ('First Two Layers (cross + 4 F2L pairs)', 'f2l'),
    'ZZF2L': ('ZZ F2L (edges oriented, R/U/L moveset)', 'f2l'),
    'ZZRB': ('ZZ Right Block (R+U pieces scrambled)', 'f2l'),
    'PETRUSF2L': ('Petrus F2L (R+U block remaining)', 'f2l'),
    # Last Slot variants
    'LS': ('Last Slot (one F2L pair + last layer)', 'f2l'),
    'ELS': ('Edge Last Slot (LS with edge orientation)', 'f2l'),
    'ZZLS': ('ZZ Last Slot (edges oriented)', 'f2l'),
    'TSLE': ('Top Slot + Last Edge', 'f2l'),
    'CLS': ('Corner Last Slot (corner + U edges)', 'f2l'),
    'CPLS': ('Corner Permutation Last Slot', 'f2l'),
    'EJLS': ('Edge Just Last Slot (DFR disoriented)', 'f2l'),
    'EJF2L': ('Edge Just F2L', 'f2l'),
    'TTLL': ('Two-Twist Last Layer (DFR + U corners)', 'f2l'),
    'WV': ("Winter Variation (after R U R')", 'll'),
    'SV': ("Summer Variation (after R U' R')", 'll'),
    'VLS': ("Valk Last Slot (after R U' R')", 'f2l'),
    'VHLS': ('Valk-Harris Last Slot', 'f2l'),
    # Roux method
    'CMLL': ('Corners of Last Layer (Roux)', 'cmll'),
    'CMLLEO': ('CMLL + Edge Orientation (Roux)', 'lse'),
    'SB': ('Second Block (Roux R+U+DF+DB)', 'f2l'),
    # Petrus method
    'PETRUS2X2X3': ('Petrus 2x2x3 block (U+R+F scrambled)', 'f2l'),
    'PETRUSEO': ('Petrus Edge Orientation (U+F scrambled)', 'f2l'),
}


def show_step(
    name: str,
    rng: Random,
    orientation: str,
    *,
    auf: bool = False,
) -> None:
    """Display a step scramble with cube visualization."""
    description, mode = STEP_INFO.get(name, (name, 'oll'))
    rotation = ORIENTATION_FACE_MOVES[orientation]
    prefix = f'{rotation} ' if rotation else ''
    print(f'\n   {name}: {description}')

    scramble = scramble_step(name, rng=rng, include_auf=auf)
    print(f'   Scramble: {prefix}{scramble}')
    print(f'   Moves: {len(scramble)}')

    cube = VCube()
    cube.rotate(rotation + scramble)
    cube.show(mode=mode)


def show_ocll_case(case: str, rng: Random, orientation: str) -> None:
    """Display a specific OCLL case scramble."""
    scramble = scramble_ocll_case(case, rng=rng)
    rotation = ORIENTATION_FACE_MOVES[orientation]
    prefix = f'{rotation} ' if rotation else ''
    print(f'\n   OCLL {case}:')
    print(f'   Scramble: {prefix}{scramble}')
    print(f'   Moves: {len(scramble)}')

    cube = VCube()
    cube.rotate(rotation + scramble)
    cube.show(mode='oll')


def section(title: str) -> None:
    """Print a section header."""
    print('\n' + '=' * 60)
    print(title)
    print('=' * 60)


def print_list() -> None:
    """Print available steps and methods."""
    section('Available Steps and Methods')

    print('\nMethods (use with -m/--method):')
    for method, steps in METHODS.items():
        print(f'  {method}: {", ".join(steps)}')

    print('\nAll Steps (use with -s/--step):')
    print(f'  {", ".join(SUPPORTED_STEPS)}')

    print('\nOCLL Cases (use with --ocll):')
    print(f'  {", ".join(OCLL_CASES)}')

    print('\nTerminology:')
    print('  AUF = Adjust U Face (random U layer rotation)')
    print('  F2L = First Two Layers')
    print('  OLL = Orientation of Last Layer')
    print('  PLL = Permutation of Last Layer')
    print('  LL  = Last Layer (OLL + PLL)')
    print('  LS  = Last Slot (final F2L pair)')
    print('  EO  = Edge Orientation')
    print('=' * 60)


def demo_method(
    method: str,
    rng: Random,
    orientation: str,
    *,
    auf: bool = False,
) -> None:
    """Demonstrate steps for a specific method."""
    titles = {
        'cfop': 'CFOP Method (Cross → F2L → OLL → PLL)',
        'cfop-ll': 'CFOP Last Layer Variants',
        'cfop-ls': 'CFOP Last Slot Variants',
        'zz': 'ZZ Method (EOLine → F2L → Last Layer)',
        'roux': 'Roux Method (FB → SB → CMLL → LSE)',
        'petrus': 'Petrus Method (2x2x2 → 2x2x3 → EO → F2L → LL)',
    }

    section(titles.get(method, method.upper()))
    for step in METHODS.get(method, []):
        show_step(step, rng, orientation, auf=auf)


def demo_steps(
    steps: list[str],
    rng: Random,
    orientation: str,
    *,
    auf: bool = False,
) -> None:
    """Demonstrate specific steps."""
    section('Selected Steps')
    for step in steps:
        step_upper = step.upper()
        # Handle case-insensitive matching
        matched = None
        for supported in SUPPORTED_STEPS:
            if supported.upper() == step_upper:
                matched = supported
                break
        if matched:
            show_step(matched, rng, orientation, auf=auf)
        else:
            print(f'\n   Warning: Step "{step}" not recognized')
            print(f'   Available: {", ".join(SUPPORTED_STEPS)}')


def demo_ocll(cases: list[str] | None, rng: Random, orientation: str) -> None:
    """Demonstrate OCLL cases."""
    section('OCLL Cases')
    print('\nCorner orientation patterns for last layer')

    if cases:
        for case in cases:
            # Case-insensitive matching
            matched = None
            for ocll in OCLL_CASES:
                if ocll.upper() == case.upper():
                    matched = ocll
                    break
            if matched:
                show_ocll_case(matched, rng, orientation)
            else:
                print(f'\n   Warning: OCLL case "{case}" not recognized')
                print(f'   Available: {", ".join(OCLL_CASES)}')
    else:
        for case in OCLL_CASES:
            show_ocll_case(case, rng, orientation)


def demo_all(rng: Random, orientation: str, *, auf: bool = False) -> None:
    """Run all demos."""
    section('Step Scramble Examples - All Speedcubing Methods')

    for method in ['cfop', 'cfop-ll', 'cfop-ls', 'zz', 'roux', 'petrus']:
        demo_method(method, rng, orientation, auf=auf)

    demo_ocll(None, rng, orientation)

    print_list()


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace.

    """
    parser = argparse.ArgumentParser(
        description='Generate scrambles for speedcubing steps.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      Run all demos
  %(prog)s --list               List available steps and methods
  %(prog)s -m cfop              Show only CFOP method steps
  %(prog)s -m zz roux           Show ZZ and Roux method steps
  %(prog)s -s PLL OLL F2L       Show specific steps
  %(prog)s --ocll               Show all OCLL cases
  %(prog)s --ocll Sune T        Show specific OCLL cases
  %(prog)s --auf                Enable AUF (Adjust U Face)
  %(prog)s --seed 123           Set random seed for reproducibility
""",
    )

    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available steps and methods',
    )

    parser.add_argument(
        '-m', '--method',
        nargs='+',
        choices=list(METHODS.keys()),
        metavar='METHOD',
        help=f'Filter by method: {", ".join(METHODS.keys())}',
    )

    parser.add_argument(
        '-s', '--step',
        nargs='+',
        metavar='STEP',
        help='Show specific steps (e.g., PLL OLL F2L)',
    )

    parser.add_argument(
        '--ocll',
        nargs='*',
        metavar='CASE',
        help='Show OCLL cases (all if no case specified)',
    )

    parser.add_argument(
        '--auf',
        action='store_true',
        help='Enable AUF (Adjust U Face)',
    )

    parser.add_argument(
        '-o', '--orientation',
        choices=ORIENTATIONS,
        default='DF',
        metavar='ORIENTATION',
        help='Cube orientation, e.g. DF, UF, RD (default: DF)',
    )

    parser.add_argument(
        '--seed',
        help='Random seed for reproducibility (default: 42)',
    )

    return parser.parse_args()


def main() -> None:
    """Run the step scramble demo with CLI argument handling."""
    args = parse_args()

    # Initialize RNG with seed
    rng = Random(args.seed)  # noqa: S311

    auf = args.auf
    orientation = args.orientation

    # Handle --list
    if args.list:
        print_list()
        return

    # Handle --ocll (can be empty list for all cases, or specific cases)
    if args.ocll is not None:
        demo_ocll(args.ocll or None, rng, orientation)
        return

    # Handle --step
    if args.step:
        demo_steps(args.step, rng, orientation, auf=auf)
        return

    # Handle --method
    if args.method:
        for method in args.method:
            demo_method(method, rng, orientation, auf=auf)
        return

    # Default: run all demos
    demo_all(rng, orientation, auf=auf)


if __name__ == '__main__':
    main()
