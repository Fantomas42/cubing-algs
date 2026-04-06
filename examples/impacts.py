"""Demonstrate comprehensive algorithm impact analysis."""
# ruff: noqa: T201
from typing import TYPE_CHECKING

from cubing_algs.algorithm import Algorithm

if TYPE_CHECKING:
    from cubing_algs.impacts import CycleAnalysis


def print_cycle_info(
    label: str,
    cycles: list[list[int]],
    analysis: 'CycleAnalysis | None',
) -> None:
    """Print cycle details for corners or edges."""
    print(f'\n  {label} cycles:           { cycles }')
    if analysis is None or analysis['cycle_count'] == 0:
        return
    print(f'    Cycle count:           { analysis["cycle_count"] }')
    print(f'    Cycle lengths:         { analysis["cycle_lengths"] }')
    if analysis['two_cycles'] > 0:
        print(f'    2-cycles (swaps):      { analysis["two_cycles"] }')
    if analysis['three_cycles'] > 0:
        print(f'    3-cycles:              { analysis["three_cycles"] }')


def show_impact(algorithm: str) -> None:
    """Display comprehensive impact analysis for an algorithm."""
    print(f'{ "=" * 70 }')
    print(f'Algorithm: { algorithm }')
    print('=' * 70)

    algo = Algorithm.parse_moves(algorithm)
    impacts = algo.impacts()

    # Facelet Analysis (Visual/Spatial Impact)
    print('\nFACELET ANALYSIS (Visual/Spatial Impact)')
    print('-' * 70)
    print(f'  Fixed facelets:          { impacts.facelets_fixed_count }/54')
    print(f'  Mobilized facelets:      { impacts.facelets_mobilized_count }/54')
    print(f'  Scrambled percent:       { impacts.facelets_scrambled_percent:.1%}')  # noqa: E501
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
    print('\n  Face mobility:')
    for face, count in impacts.facelets_face_mobility.items():
        print(f'    {face} face:               {count}/9 facelets moved')

    piece_types = impacts.facelets_piece_type_impact
    print('\n  Piece type impact:')
    for piece_type, count in sorted(piece_types.items()):
        print(f'    {piece_type}:{"." * (20 - len(piece_type))} { count }')

    # Cubie Analysis (Piece-Level Impact)
    print('\nCUBIE ANALYSIS (Piece-Level Impact)')
    print('-' * 70)
    print(f'  Corners moved:           { impacts.cubies_corners_moved }/8')
    print(f'  Corners twisted:         { impacts.cubies_corners_twisted }/8')
    print(f'  Edges moved:             { impacts.cubies_edges_moved }/12')
    print(f'  Edges flipped:           { impacts.cubies_edges_flipped }/12')

    print('\n  Parity:')
    print(
        f'    Corner parity:         { impacts.cubies_corner_parity } '
        f'({ "even" if impacts.cubies_corner_parity == 0 else "odd" })',
    )
    print(
        f'    Edge parity:           { impacts.cubies_edge_parity } '
        f'({ "even" if impacts.cubies_edge_parity == 0 else "odd" })',
    )
    print(
        f'    Parity valid:          '
        f'{ "✓" if impacts.cubies_parity_valid else "✗" }',
    )

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

    print(
        '\n  Complexity score:        '
        f'{ impacts.cubies_complexity_score }',
    )
    print(
        '  Suggested approach:      '
        f'{ impacts.cubies_suggested_approach }',
    )

    if impacts.cubies_patterns:
        print('\n  Pattern classification:  ')
        for pattern in impacts.cubies_patterns:
            print(f'    { pattern }')

    # Visual representation
    print('\nCUBE VISUALIZATION')
    print('-' * 70)
    algo.show()


# Examples demonstrating different types of algorithms
show_impact('R')
show_impact("R'")
show_impact("R U R' U'")
show_impact("R U R' U R U2 R'")  # Sune
show_impact("R U R' F' R U R' U' R' F R2 U' R'")  # T-Perm
