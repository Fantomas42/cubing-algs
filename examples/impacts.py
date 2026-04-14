"""Demonstrate comprehensive algorithm impact analysis."""
# ruff: noqa: T201
import sys
from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm

if TYPE_CHECKING:
    from cubing_algs.impacts import CycleAnalysis
    from cubing_algs.impacts import ImpactData


def print_cycle_info(
    label: str,
    cycles: list[list[int]],
    analysis: 'CycleAnalysis | None',
) -> None:
    """Print cycle details for corners or edges."""
    print(f'\n  {label} cycles:           { cycles }')
    if analysis is None or analysis.cycle_count == 0:
        return
    print(f'    Cycle count:           { analysis.cycle_count }')
    print(f'    Cycle lengths:         { analysis.cycle_lengths }')
    if analysis.two_cycles > 0:
        print(f'    2-cycles (swaps):      { analysis.two_cycles }')
    if analysis.three_cycles > 0:
        print(f'    3-cycles:              { analysis.three_cycles }')


def print_distance_metrics(impacts: 'ImpactData') -> None:
    """Print Manhattan and QTM distance metrics."""
    manhattan = impacts.facelets_manhattan_distance
    if manhattan is not None:
        print('\n  Manhattan distance metrics:')
        print(f'    Mean displacement:     { manhattan.mean:.2f}')
        print(f'    Max displacement:      { manhattan.max }')
        print(f'    Total displacement:    { manhattan.sum }')
    qtm = impacts.facelets_qtm_distance
    if qtm is not None:
        print('\n  QTM distance metrics:')
        print(f'    Mean displacement:     { qtm.mean:.2f}')
        print(f'    Max displacement:      { qtm.max }')
        print(f'    Total displacement:    { qtm.sum }')


def print_face_analysis(impacts: 'ImpactData') -> None:
    """Print face mobility, face-to-face matrix, and symmetry info."""
    print(f'\n  State:                   { impacts.facelets_state }')
    mask = impacts.facelets_transformation_mask
    print(f'  Transformation mask:     { mask }')

    print('\n  Face mobility:')
    for face, count in impacts.facelets_face_mobility.items():
        print(f'    {face} face:               {count}/9 facelets moved')

    print('\n  Face-to-face matrix:')
    for from_face, targets in impacts.facelets_face_to_face_matrix.items():
        flows = ', '.join(
            f'{to_face}:{count}'
            for to_face, count in targets.items()
            if count > 0
        )
        if flows:
            print(f'    {from_face} -> {flows}')

    print('\n  Symmetry:')
    for axis, is_symmetric in impacts.facelets_symmetry.items():
        mark = '✓' if is_symmetric else '✗'
        print(f'    {axis}:{"." * (22 - len(axis))} { mark }')

    permutations = impacts.facelets_permutations
    if permutations:
        count = len(permutations)
        print(f'\n  Facelet permutations:    { count } facelets moved')


def print_facelet_analysis(impacts: 'ImpactData') -> None:
    """Print facelet-based spatial impact analysis."""
    print('\nFACELET ANALYSIS (Visual/Spatial Impact)')
    print('-' * 70)
    print(f'  Fixed facelets:          { impacts.facelets_fixed_count }/54')
    mobilized = impacts.facelets_mobilized_count
    print(f'  Mobilized facelets:      { mobilized }/54')
    scrambled = impacts.facelets_scrambled_percent
    print(f'  Scrambled percent:       { scrambled:.1%}')

    print_distance_metrics(impacts)
    print_face_analysis(impacts)

    piece_types = impacts.facelets_piece_type_impact
    print('\n  Piece type impact:')
    for piece_type, count in sorted(piece_types.items()):
        print(f'    {piece_type}:{"." * (20 - len(piece_type))} { count }')


def print_parity_info(impacts: 'ImpactData') -> None:
    """Print parity values and signature details."""
    print('\n  Parity:')
    corner_parity = impacts.cubies_corner_parity
    corner_label = 'even' if corner_parity == 0 else 'odd'
    print(f'    Corner parity:         { corner_parity } ({ corner_label })')
    edge_parity = impacts.cubies_edge_parity
    edge_label = 'even' if edge_parity == 0 else 'odd'
    print(f'    Edge parity:           { edge_parity } ({ edge_label })')
    valid_mark = '✓' if impacts.cubies_parity_valid else '✗'
    print(f'    Parity valid:          { valid_mark }')

    signature = impacts.cubies_parity_signature
    if signature is None:
        return
    print('\n  Parity signature:')
    print(f'    Signature:             { signature.signature }')
    sig_mark = '✓' if signature.is_valid else '✗'
    print(f'    Valid:                 { sig_mark }')
    if signature.implications:
        print('    Implications:')
        for implication in signature.implications:
            print(f'      - { implication }')


def print_cubie_analysis(impacts: 'ImpactData') -> None:
    """Print cubie-based piece-level impact analysis."""
    print('\nCUBIE ANALYSIS (Piece-Level Impact)')
    print('-' * 70)
    print(f'  Corners moved:           { impacts.cubies_corners_moved }/8')
    print(f'  Corners twisted:         { impacts.cubies_corners_twisted }/8')
    print(f'  Edges moved:             { impacts.cubies_edges_moved }/12')
    print(f'  Edges flipped:           { impacts.cubies_edges_flipped }/12')

    print('\n  Raw cubie arrays:')
    print(f'    Corner permutation:    { impacts.cubies_corner_permutation }')
    print(f'    Corner orientation:    { impacts.cubies_corner_orientation }')
    print(f'    Edge permutation:      { impacts.cubies_edge_permutation }')
    print(f'    Edge orientation:      { impacts.cubies_edge_orientation }')

    print_parity_info(impacts)

    if impacts.cubies_corner_cycles:
        print_cycle_info(
            'Corner',
            impacts.cubies_corner_cycles,
            impacts.cubies_corner_cycle_analysis,
        )

    if impacts.cubies_edge_cycles:
        print_cycle_info(
            'Edge',
            impacts.cubies_edge_cycles,
            impacts.cubies_edge_cycle_analysis,
        )

    print(f'\n  Complexity score:        { impacts.cubies_complexity_score }')
    print(f'  Suggested approach:      { impacts.cubies_suggested_approach }')

    if impacts.cubies_patterns:
        print('\n  Pattern classification:  ')
        for pattern in impacts.cubies_patterns:
            print(f'    { pattern }')


def show_impact(algorithm: str) -> None:
    """Display comprehensive impact analysis for an algorithm."""
    print(f'{ "=" * 70 }')
    print(f'Algorithm: { algorithm }')
    print('=' * 70)

    algo = Algorithm.parse_moves(algorithm)
    impacts = algo.impacts()

    print_facelet_analysis(impacts)
    print_cubie_analysis(impacts)

    print('\nCUBE VISUALIZATION')
    print('-' * 70)
    algo.show()


if sys.argv[1:]:
    for arg in sys.argv[1:]:
        show_impact(arg)
else:
    # Default examples demonstrating different types of algorithms
    show_impact('R')
    show_impact("R'")
    show_impact("R U R' U'")
    show_impact("R U R' U R U2 R'")  # Sune
    show_impact("R U R' F' R U R' U' R' F R2 U' R'")  # T-Perm
