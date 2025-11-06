"""Demonstrate comprehensive algorithm structure analysis."""
# ruff: noqa: T201
from cubing_algs.algorithm import Algorithm


def show_structure(algorithm: str) -> None:  # noqa: PLR0915
    """Display comprehensive structure analysis for an algorithm."""
    print(f'{"=" * 70}')
    print(f'Algorithm: {algorithm}')
    print('=' * 70)

    algo = Algorithm.parse_moves(algorithm)
    struct = algo.structure

    # Basic Information
    print('\nBASIC INFORMATION')
    print('-' * 70)
    print(f'  Original:            {struct.original}')
    print(f'  Compressed:          {struct.compressed}')
    print(f'  Original length:     {struct.original_length} moves')

    # Structure Counts
    print('\nSTRUCTURE DETECTION')
    print('-' * 70)
    print(f'  Total structures:    {struct.total_structures}')
    print(f'  Conjugates:          {struct.conjugate_count}')
    print(f'  Commutators:         {struct.commutator_count}')
    print(f'  Max nesting depth:   {struct.max_nesting_depth}')
    print(f'  Nested structures:   {struct.nested_structure_count}')

    # Compression Metrics
    print('\nCOMPRESSION ANALYSIS')
    print('-' * 70)
    print(f'  Original length:     {struct.original_length} moves')
    print(f'  Compressed length:   {struct.compressed_notation_length} chars')
    print(f'  Compression ratio:   {struct.compression_ratio:.1%}')

    # Quality Metrics
    print('\nQUALITY METRICS')
    print('-' * 70)
    print(f'  Average score:       {struct.average_structure_score:.2f}')
    print(f'  Best score:          {struct.best_structure_score:.2f}')

    # Setup and Action Analysis
    if struct.total_structures > 0:
        print('\nSETUP AND ACTION ANALYSIS')
        print('-' * 70)
        print(
            f'  Setup lengths:       {struct.shortest_setup_length}-'
            f'{struct.longest_setup_length} '
            f'(avg: {struct.average_setup_length:.1f})',
        )
        print(
            f'  Action lengths:      {struct.shortest_action_length}-'
            f'{struct.longest_action_length} '
            f'(avg: {struct.average_action_length:.1f})',
        )

    # Coverage Analysis
    print('\nCOVERAGE ANALYSIS')
    print('-' * 70)
    print(f'  Coverage:            {struct.coverage_percent:.1%}')
    print(f'  Uncovered moves:     {struct.uncovered_moves}')

    # Classification Statistics (NEW)
    print('\nCLASSIFICATION STATISTICS')
    print('-' * 70)
    print(f'  Pure commutators:    {struct.pure_commutator_count}')
    print(f'  A9 commutators:      {struct.a9_commutator_count}')
    print(f'  Nested conjugates:   {struct.nested_conjugate_count}')
    print(f'  Simple conjugates:   {struct.simple_conjugate_count}')
    print(f'  With cancellations:  {struct.structures_with_cancellations}')
    print(f'  Avg moves/structure: {struct.average_move_count:.1f}')
    print(f'  Efficiency rating:   {struct.efficiency_rating}')

    # Detailed Structures
    if struct.structures:
        print('\nDETAILED STRUCTURES')
        print('-' * 70)
        for idx, s in enumerate(struct.structures, 1):
            class_tag = f' [{s.classification}]' if s.classification else ''
            pure_tag = ' (PURE)' if s.is_pure else ''
            cancel_tag = ' *cancels*' if s.has_cancellations else ''

            print(
                f'  {idx}. {s.type.capitalize()}: {s}'
                f'{class_tag}{pure_tag}{cancel_tag}',
            )
            print(f'     Score: {s.score:.2f} | Moves: {s.move_count}')
            print(f'     Setup: {s.setup} ({len(s.setup)} moves)')
            print(f'     Action: {s.action} ({len(s.action)} moves)')
            print(f'     Position: {s.start}-{s.end}')
    else:
        print('\nNo structures found.')

    print()


# Examples demonstrating different types of algorithms
# Simple move - no structure
show_structure('R')
# Simple commutator
show_structure("R U R' U'")
# Sune - simple algorithm
show_structure("R U R' U R U2 R'")
# Sexy move with setup
show_structure("F R U R' U' F'")
# T-Perm - complex structure
show_structure("R U R' F' R U R' U' R' F R2 U' R'")
# Jb-Perm
show_structure("R U R' U' R' F R2 U' R' U' R U R' F'")
