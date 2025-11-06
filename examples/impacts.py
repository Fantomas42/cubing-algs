"""Demonstrate comprehensive algorithm impact analysis."""
# ruff: noqa: T201
from cubing_algs.algorithm import Algorithm


def show_impact(algorithm: str) -> None:  # noqa: PLR0915, C901
    """Display comprehensive impact analysis for an algorithm."""
    print(f'{ "=" * 70 }')
    print(f'Algorithm: { algorithm }')
    print('=' * 70)

    algo = Algorithm.parse_moves(algorithm)
    impacts = algo.impacts

    # Facelet Analysis (Visual/Spatial Impact)
    print('\nFACELET ANALYSIS (Visual/Spatial Impact)')
    print('-' * 70)
    print(f'  Fixed facelets:          { impacts.facelets_fixed_count }/54')
    print(f'  Mobilized facelets:      { impacts.facelets_mobilized_count }/54')
    print(f'  Scrambled percent:       { impacts.facelets_scrambled_percent:.1%}')  # noqa: E501
    print('\n  Manhattan distance metrics:')
    print(f'    Mean displacement:     { impacts.facelets_manhattan_distance.mean:.2f}')  # noqa: E501
    print(f'    Max displacement:      { impacts.facelets_manhattan_distance.max }')  # noqa: E501
    print(f'    Total displacement:    { impacts.facelets_manhattan_distance.sum }')  # noqa: E501
    print('\n  QTM distance metrics:')
    print(f'    Mean displacement:     { impacts.facelets_qtm_distance.mean:.2f}')  # noqa: E501
    print(f'    Max displacement:      { impacts.facelets_qtm_distance.max }')
    print(f'    Total displacement:    { impacts.facelets_qtm_distance.sum }')
    print('\n  Face mobility:')
    for face, count in impacts.facelets_face_mobility.items():
        print(f'    {face} face:               {count}/9 facelets moved')

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
        print(
            f'\n  Corner cycles:           '
            f'{ impacts.cubies_corner_cycles }',
        )
        cc_analysis = impacts.cubies_corner_cycle_analysis
        if cc_analysis['cycle_count'] > 0:
            print(
                f'    Cycle count:           '
                f'{ cc_analysis["cycle_count"] }',
            )
            print(
                f'    Cycle lengths:         '
                f'{ cc_analysis["cycle_lengths"] }',
            )
            if cc_analysis['two_cycles'] > 0:
                print(
                    f'    2-cycles (swaps):      '
                    f'{ cc_analysis["two_cycles"] }',
                )
            if cc_analysis['three_cycles'] > 0:
                print(
                    f'    3-cycles:              '
                    f'{ cc_analysis["three_cycles"] }',
                )

    if impacts.cubies_edge_cycles:
        print(
            f'\n  Edge cycles:             '
            f'{ impacts.cubies_edge_cycles }',
        )
        ec_analysis = impacts.cubies_edge_cycle_analysis
        if ec_analysis['cycle_count'] > 0:
            print(
                '    Cycle count:           '
                f'{ ec_analysis["cycle_count"] }',
            )
            print(
                '    Cycle lengths:         '
                f'{ ec_analysis["cycle_lengths"] }',
            )
            if ec_analysis['two_cycles'] > 0:
                print(
                    '    2-cycles (swaps):      '
                    f'{ ec_analysis["two_cycles"] }',
                )
            if ec_analysis['three_cycles'] > 0:
                print(
                    f'    3-cycles:              '
                    f'{ ec_analysis["three_cycles"] }',
                )

    print(
        '\n  Complexity score:        '
        f'{ impacts.cubies_complexity_score }',
    )
    print(
        '  Suggested approach:      '
        f'{ impacts.cubies_suggested_approach }',
    )

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
