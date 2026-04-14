"""Display a text resume of an algorithm based on its to_dict() data."""
# ruff: noqa: T201
import argparse
from typing import Any

from cubing_algs.constants import DEFAULT_CUBE_SIZE
from cubing_algs.parsing import parse_moves


def section(title: str) -> None:
    """Print a section header."""
    print(f'\n{title}')
    print('-' * 70)


def yesno(*, value: bool) -> str:
    """
    Format a boolean as Yes/No.

    Args:
        value: Boolean value to format.

    Returns:
        The string 'Yes' when value is truthy, otherwise 'No'.

    """
    return 'Yes' if value else 'No'


def print_overview(data: dict[str, Any], size: int) -> None:
    """Print the algorithm overview block."""
    print('=' * 70)
    print(f'Algorithm:      {data["moves"]}')
    print(f'Cube size:      {size}x{size}x{size}')
    print('=' * 70)

    section('OVERVIEW')
    print(f'  Cycles:                 {data["cycles"]}')
    print(f'  Minimum cube size:      {data["min_cube_size"]}')
    print(f'  Standard notation:      {yesno(value=data["is_standard"])}')
    print(f'  SiGN notation:          {yesno(value=data["is_sign"])}')
    print(f'  Has rotations:          {yesno(value=data["has_rotations"])}')
    print(
        f'  Has internal rotations: '
        f'{yesno(value=data["has_internal_rotations"])}',
    )
    print(f'  Has pauses:             {yesno(value=data["has_pauses"])}')
    print(f'  Has times:              {yesno(value=data["has_times"])}')


def print_metrics(metrics: dict[str, Any]) -> None:
    """Print move metrics."""
    section('METRICS')
    print(f'  HTM (half turn):        {metrics["htm"]}')
    print(f'  QTM (quarter turn):     {metrics["qtm"]}')
    print(f'  STM (slice turn):       {metrics["stm"]}')
    print(f'  ETM (execution):        {metrics["etm"]}')
    print(f'  QSTM:                   {metrics["qstm"]}')
    print(f'  RTM (rotations):        {metrics["rtm"]}')
    print(f'  Outer moves:            {metrics["outer_moves"]}')
    print(f'  Inner moves:            {metrics["inner_moves"]}')
    print(f'  Rotations:              {metrics["rotations"]}')
    print(f'  Pauses:                 {metrics["pauses"]}')
    print(f'  Generators:             {", ".join(metrics["generators"])}')


def print_ergonomics(ergo: dict[str, Any]) -> None:
    """Print ergonomics information."""
    section('ERGONOMICS')
    print(f'  Rating:                 {ergo["ergonomic_rating"]}')
    print(f'  Difficulty:             {ergo["difficulty_classification"]}')
    print(f'  Comfort score:          {ergo["comfort_score"]:.1f}/100')
    print(f'  Ergonomic score:        {ergo["ergonomic_score"]:.3f}')
    print(f'  Flow score:             {ergo["flow_score"]:.3f}')
    print(f'  Estimated TPS:          {ergo["estimated_tps"]:.2f}')
    print(f'  Execution time:         {ergo["estimated_execution_time"]:.2f}s')
    print(
        f'  Hand usage (R/L/both):  '
        f'{ergo["right_hand_moves"]} / '
        f'{ergo["left_hand_moves"]} / '
        f'{ergo["both_hand_moves"]}',
    )
    print(f'  Hand balance ratio:     {ergo["hand_balance_ratio"]:.2f}')
    print(f'  Regrips:                {ergo["regrip_count"]}')
    print(f'  Awkward moves:          {ergo["awkward_moves"]}')
    print(f'  Flow breaks:            {ergo["flow_breaks"]}')
    print(
        f'  Triggers:               '
        f'{ergo["trigger_count"]} '
        f'(coverage {ergo["trigger_coverage"]})',
    )
    if ergo.get('detected_patterns'):
        print(
            f'  Detected patterns:      '
            f'{", ".join(ergo["detected_patterns"])}',
        )
    if ergo.get('suggestions'):
        print('  Suggestions:')
        for suggestion in ergo['suggestions']:
            print(f'    - {suggestion}')


def print_structure(struct: dict[str, Any]) -> None:
    """Print structural analysis."""
    section('STRUCTURE')
    print(f'  Compressed:             {struct["compressed"]}')
    print(f'  Efficiency rating:      {struct["efficiency_rating"]}')
    print(f'  Total structures:       {struct["total_structures"]}')
    print(f'  Conjugates:             {struct["conjugate_count"]}')
    print(f'  Commutators:            {struct["commutator_count"]}')
    print(f'  Pure commutators:       {struct["pure_commutator_count"]}')
    print(f'  Max nesting depth:      {struct["max_nesting_depth"]}')
    print(
        f'  Compression ratio:      '
        f'{struct["compression_ratio"]:.2%}',
    )
    print(
        f'  Coverage:               '
        f'{struct["coverage_percent"]:.0%} '
        f'({struct["uncovered_moves"]} uncovered)',
    )
    print(
        f'  Best structure score:   '
        f'{struct["best_structure_score"]:.2f}',
    )


def print_memory(mem: dict[str, Any]) -> None:
    """Print memorization difficulty."""
    section('MEMORY')
    print(f'  Rating:                 {mem["memory_rating"]}')
    print(f'  Score:                  {mem["memory_score"]:.1f}/100')
    print(f'  Move count:             {mem["move_count"]}')
    print(f'  Effective chunks:       {mem["effective_chunks"]}')
    print(f'  Distinct triggers:      {mem["distinct_triggers"]}')
    print(
        f'  Trigger coverage:       '
        f'{mem["trigger_coverage_percent"]:.0%}',
    )
    print(f'  Distinct faces:         {mem["distinct_faces"]}')
    print(f'  Has structure:          {yesno(value=mem["has_structure"])}')
    print(f'  Repeated patterns:      {mem["repeated_patterns"]}')
    print(
        f'  Unfamiliar moves:       '
        f'{mem["unfamiliar_move_percent"]:.0%}',
    )


def print_impacts(impacts: dict[str, Any]) -> None:
    """Print the impact on the cube."""
    section('IMPACTS')
    print(
        f'  Facelets mobilized:     '
        f'{impacts["facelets_mobilized_count"]} '
        f'({impacts["facelets_scrambled_percent"]:.0%})',
    )
    print(f'  Facelets fixed:         {impacts["facelets_fixed_count"]}')

    face_mobility = impacts['facelets_face_mobility']
    mobility_str = ', '.join(
        f'{face}:{count}' for face, count in face_mobility.items()
    )
    print(f'  Face mobility:          {mobility_str}')

    piece_impact = impacts['facelets_piece_type_impact']
    piece_str = ', '.join(
        f'{name}:{count}' for name, count in piece_impact.items()
    )
    print(f'  Piece type impact:      {piece_str}')

    print(
        f'  Corners moved:          '
        f'{impacts["cubies_corners_moved"]} '
        f'(twisted: {impacts["cubies_corners_twisted"]})',
    )
    print(
        f'  Edges moved:            '
        f'{impacts["cubies_edges_moved"]} '
        f'(flipped: {impacts["cubies_edges_flipped"]})',
    )
    print(f'  Complexity score:       {impacts["cubies_complexity_score"]}')
    print(
        f'  Parity signature:       '
        f'{impacts["cubies_parity_signature"]["signature"]} '
        f'(valid: {yesno(value=impacts["cubies_parity_valid"])})',
    )
    print(f'  Suggested approach:     {impacts["cubies_suggested_approach"]}')

    qtm = impacts['facelets_qtm_distance']
    print(
        f'  QTM distance:           '
        f'mean {qtm["mean"]:.2f}, max {qtm["max"]}, sum {qtm["sum"]}',
    )
    manhattan = impacts['facelets_manhattan_distance']
    print(
        f'  Manhattan distance:     '
        f'mean {manhattan["mean"]:.2f}, '
        f'max {manhattan["max"]}, '
        f'sum {manhattan["sum"]}',
    )

    if impacts.get('cubies_patterns'):
        section('DETECTED PATTERNS')
        for pattern in impacts['cubies_patterns']:
            print(f'  - {pattern}')


def resume(algorithm: str, size: int) -> None:
    """Print a text resume of an algorithm."""
    algo = parse_moves(algorithm)
    data = algo.to_dict(size)

    print_overview(data, size)
    print_metrics(data['metrics'])
    print_ergonomics(data['ergonomics'])
    print_structure(data['structure'])
    print_memory(data['memory'])
    print_impacts(data['impacts'])
    print()


def main() -> None:
    """Parse CLI arguments and display the algorithm resume."""
    parser = argparse.ArgumentParser(
        description='Display a text resume of a cube algorithm.',
        epilog="""examples:
  %(prog)s "R U R' U'"
  %(prog)s "R U R' U R U2 R'" -s 3
  %(prog)s "Rw U Rw'" -s 4""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'algorithm',
        help='Algorithm to analyze (e.g. "R U R\'")',
    )
    parser.add_argument(
        '-s', '--size',
        type=int,
        default=DEFAULT_CUBE_SIZE,
        help=f'Cube size (default: {DEFAULT_CUBE_SIZE})',
    )
    args = parser.parse_args()

    resume(args.algorithm, args.size)


if __name__ == '__main__':
    main()
